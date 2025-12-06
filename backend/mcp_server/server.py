"""
MCP Server for AI Portfolio
Exposes portfolio management tools via Model Context Protocol
"""
import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import TOOLS
from .handlers import TOOL_HANDLERS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio-mcp-server")

# Create MCP server instance
app = Server("portfolio-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    tools = []
    for tool_def in TOOLS:
        tools.append(
            Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                inputSchema=tool_def["inputSchema"]
            )
        )
    logger.info(f"Listed {len(tools)} tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution"""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    if name not in TOOL_HANDLERS:
        error_msg = f"Unknown tool: {name}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    
    try:
        # Call the handler
        handler = TOOL_HANDLERS[name]
        result = handler(arguments or {})
        
        # Convert result to JSON string
        import json
        result_text = json.dumps(result, indent=2)
        
        logger.info(f"Tool {name} executed successfully")
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}))]


async def main():
    """Main entry point for MCP server"""
    logger.info("Starting Portfolio MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server running on stdio")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
