"""
FastAPI server for AI Portfolio Agent
Provides REST API for interacting with the LangChain agent
"""
import os
import logging
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Portfolio Agent API",
    description="Intelligent agent for portfolio management using LangChain and MCP tools",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to the agent")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent's response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: str

class ToolExecutionRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the MCP tool to execute")
    arguments: dict = Field(default_factory=dict, description="Tool arguments")

class ToolExecutionResponse(BaseModel):
    success: bool
    result: dict
    timestamp: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Docker healthcheck"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="ai-portfolio-agent",
        version="1.0.0"
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "AI Portfolio Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "tools": "/api/tools",
            "docs": "/docs"
        }
    }

# Chat endpoint with agent integration
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI agent

    The agent can:
    - Answer questions about your learning progress
    - Create learning entries
    - Search knowledge base
    - Provide recommendations
    """
    try:
        logger.info(f"Chat request: {request.message}")

        # Import agent (lazy load to avoid startup issues)
        from agent import get_agent

        # Get agent instance
        agent = get_agent()

        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{int(datetime.utcnow().timestamp())}"

        # Process message with agent
        result = agent.chat(request.message, conversation_id=conversation_id)

        if not result.get("success", False):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# Validation Endpoint
class ValidationRequest(BaseModel):
    text: str

class ValidationResponse(BaseModel):
    is_safe: bool
    reason: str

@app.post("/api/validate", response_model=ValidationResponse)
async def validate_prompt(request: ValidationRequest):
    """
    Validate input text against security rules.
    """
    from guardrails_config import validate_input
    from agent import get_agent
    
    # Use the same validation logic as the agent
    is_safe, reason = validate_input(request.text)
    
    if not is_safe:
        # We should also log this here since the backend is asking
        try:
            # We can use the agent instance to reuse logging logic if we refactor,
            # but for now let's just log it directly or assume the caller handles strict logging if needed.
            # actually, let's log it here to ensure "Agent Service" is doing the work.
            import requests
            # Log to Backend Security Audit (recursion? No, backend called us, we call backend logs)
            # To avoid potential loop complexity or double logging, we'll just return the decision 
            # and let the caller (Backend) or this service log it.
            # User requirement: "Agent Service Integration... log violations". 
            # So WE should log it.
            backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
            requests.post(
                f"{backend_url}/api/security/audit/",
                json={
                    "source": "Agent Service (Validation API)",
                    "input_content": request.text,
                    "violation_type": "jailbreak", 
                    "action_taken": "blocked",
                    "metadata": {"reason": reason}
                },
                timeout=5
            )
        except Exception as e:
            logger.error(f"Failed to audit log violation: {e}")

    return ValidationResponse(is_safe=is_safe, reason=reason)

# Direct tool execution endpoint
@app.post("/api/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """
    Directly execute an MCP tool

    Available tools:
    - get_roadmap
    - get_learning_entries
    - search_knowledge
    - add_learning_entry
    - get_progress_stats
    """
    try:
        logger.info(f"Tool execution: {request.tool_name} with args {request.arguments}")

        # Import agent (lazy load)
        from agent import get_agent

        # Get agent instance
        agent = get_agent()

        # Execute tool
        result = agent.execute_tool(request.tool_name, request.arguments)

        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

        return ToolExecutionResponse(
            success=True,
            result=result,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tool execution error: {str(e)}")

# List available tools
@app.get("/api/tools")
async def list_tools():
    """List all available MCP tools and their descriptions"""
    return {
        "tools": [
            {
                "name": "get_roadmap",
                "description": "Get the complete AI Career Roadmap with all sections and items"
            },
            {
                "name": "get_learning_entries",
                "description": "Get learning log entries, optionally filtered by roadmap item"
            },
            {
                "name": "search_knowledge",
                "description": "Semantic search across all portfolio knowledge using RAG"
            },
            {
                "name": "add_learning_entry",
                "description": "Create a new learning log entry"
            },
            {
                "name": "get_progress_stats",
                "description": "Get portfolio progress statistics and metrics"
            }
        ]
    }

class MetricsResponse(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    timestamp: str

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get current AI health metrics (Ragas scores)
    
    Reads from the latest evaluation report (ragas_report.csv)
    """
    import csv
    import statistics
    
    report_path = "ragas_report.csv"
    
    # Default values if no report exists
    metrics = {
        "faithfulness": 0.0,
        "answer_relevancy": 0.0,
        "context_precision": 0.0
    }
    
    if not os.path.exists(report_path):
        return MetricsResponse(
            **metrics,
            timestamp=datetime.utcnow().isoformat()
        )
        
    try:
        # Accumulators
        faithfulness_scores = []
        answer_relevancy_scores = []
        context_precision_scores = []
        
        with open(report_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Helper to parse float safely
                def parse_score(val):
                    try:
                        return float(val) if val and val.strip() != "" else None
                    except ValueError:
                        return None
                
                f_score = parse_score(row.get("faithfulness"))
                a_score = parse_score(row.get("answer_relevancy"))
                c_score = parse_score(row.get("context_precision"))
                
                if f_score is not None:
                    faithfulness_scores.append(f_score)
                if a_score is not None:
                    answer_relevancy_scores.append(a_score)
                if c_score is not None:
                    context_precision_scores.append(c_score)
        
        # Calculate averages if data exists
        if faithfulness_scores:
            metrics["faithfulness"] = statistics.mean(faithfulness_scores)
        if answer_relevancy_scores:
            metrics["answer_relevancy"] = statistics.mean(answer_relevancy_scores)
        if context_precision_scores:
            metrics["context_precision"] = statistics.mean(context_precision_scores)
            
        return MetricsResponse(
            **metrics,
            timestamp=datetime.utcfromtimestamp(os.path.getmtime(report_path)).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error reading metrics: {e}")
        # Return zeros on error
        return MetricsResponse(
            faithfulness=0.0,
            answer_relevancy=0.0,
            context_precision=0.0,
            timestamp=datetime.utcnow().isoformat()
        )
