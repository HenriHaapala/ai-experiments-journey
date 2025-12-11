"""
Main LangChain Agent for AI Portfolio
Uses Groq LLM with MCP tools for intelligent portfolio management
"""
import os
import logging
from typing import Dict, Any, Optional, List

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

from mcp_tools import create_langchain_tools, MCPToolExecutor
from memory import ConversationMemory, get_memory
from prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PortfolioAgent:
    """
    Intelligent agent for managing AI portfolio using LangChain and Groq
    """

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_iterations: int = 10
    ):
        """
        Initialize the portfolio agent

        Args:
            groq_api_key: Groq API key (defaults to environment variable)
            model_name: Groq model to use
            temperature: LLM temperature (0-1)
            max_iterations: Max iterations for agent reasoning loop
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY must be set in environment or provided")

        self.model_name = model_name
        self.temperature = temperature
        self.max_iterations = max_iterations

        # Initialize LLM
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name=self.model_name,
            temperature=self.temperature
        )
        logger.info(f"Initialized Groq LLM: {self.model_name}")

        # Initialize MCP tools
        self.mcp_executor = MCPToolExecutor()
        self.tools = create_langchain_tools(self.mcp_executor)
        logger.info(f"Loaded {len(self.tools)} MCP tools")

        # Initialize memory
        self.memory = get_memory()

        # Create agent
        self.agent_executor = self._create_agent()
        logger.info("Portfolio Agent initialized successfully")

    def _create_agent(self) -> AgentExecutor:
        """
        Create LangChain ReAct agent with tools

        Returns:
            AgentExecutor instance
        """
        # ReAct prompt template
        react_prompt = PromptTemplate.from_template(
            """
{system_prompt}

TOOLS:
You have access to the following tools:

{tools}

Use the following format:

Question: the input question or task
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: JSON object with the tool parameters. Example for add_learning_entry: {{"title": "Docker Deployment", "content": "Learned about Docker", "is_public": true}}
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question/task

CRITICAL: Action Input must be a JSON object with individual fields, NOT a JSON string inside a field.

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""
        )

        # Create agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt.partial(system_prompt=SYSTEM_PROMPT)
        )

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        return agent_executor

    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message with the agent

        Args:
            message: User message
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary with response and metadata
        """
        try:
            logger.info(f"Processing message: {message[:100]}...")

            # Get conversation context if available
            context = ""
            if conversation_id:
                context = self.memory.get_context(conversation_id, max_messages=6)

            # Prepare input with context
            if context and context != "No previous conversation context.":
                full_input = f"{context}\n\nCurrent question: {message}"
            else:
                full_input = message

            # Run agent
            result = self.agent_executor.invoke({"input": full_input})

            # Extract response
            response = result.get("output", "I encountered an issue processing your request.")

            # Store in memory
            if conversation_id:
                self.memory.add_message(conversation_id, "user", message)
                self.memory.add_message(
                    conversation_id,
                    "assistant",
                    response,
                    metadata={
                        "intermediate_steps": len(result.get("intermediate_steps", [])),
                        "model": self.model_name
                    }
                )

            logger.info("Message processed successfully")

            return {
                "success": True,
                "response": response,
                "conversation_id": conversation_id,
                "metadata": {
                    "model": self.model_name,
                    "tools_used": [
                        step[0].tool for step in result.get("intermediate_steps", [])
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "success": False,
                "response": f"I encountered an error: {str(e)}",
                "error": str(e)
            }

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Directly execute a specific tool

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            # Find the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }

            # Execute tool
            result = tool.run(arguments)

            # Parse result to check for backend errors
            try:
                import json
                result_data = json.loads(result) if isinstance(result, str) else result

                # Check if backend returned an error
                if isinstance(result_data, dict) and not result_data.get("success", True):
                    return {
                        "success": False,
                        "error": result_data.get("error", "Unknown error from backend"),
                        "tool": tool_name
                    }
            except (json.JSONDecodeError, AttributeError):
                # If result isn't JSON, treat it as success
                pass

            return {
                "success": True,
                "result": result,
                "tool": tool_name
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Get list of available tools

        Returns:
            List of tool descriptions
        """
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools
        ]


# Singleton instance
_agent_instance: Optional[PortfolioAgent] = None


def get_agent() -> PortfolioAgent:
    """
    Get or create singleton PortfolioAgent instance

    Returns:
        PortfolioAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PortfolioAgent()
    return _agent_instance
