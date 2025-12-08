"""
SSE (Server-Sent Events) Transport for MCP Server
Enables external access to MCP server via HTTP/SSE protocol
"""
import json
import asyncio
import logging
from typing import AsyncIterator
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async

from mcp.server import Server
from mcp.types import JSONRPCMessage, JSONRPCRequest, JSONRPCResponse

logger = logging.getLogger(__name__)


class SSETransport:
    """Server-Sent Events transport for MCP protocol"""

    def __init__(self, server: Server):
        self.server = server
        self.message_queue = asyncio.Queue()

    async def send_message(self, message: JSONRPCMessage):
        """Send a message to the client via SSE"""
        await self.message_queue.put(message)

    async def receive_message(self, data: dict) -> JSONRPCMessage:
        """Receive and process a message from the client"""
        return JSONRPCMessage.model_validate(data)

    async def handle_request(self, request_data: dict) -> dict:
        """Handle a single JSON-RPC request"""
        try:
            # Parse the JSON-RPC request
            request = JSONRPCRequest.model_validate(request_data)

            # Route to appropriate handler
            if request.method == "tools/list":
                # Import tools directly
                from .tools import TOOLS
                from mcp.types import Tool

                tools = []
                for tool_def in TOOLS:
                    tools.append(
                        Tool(
                            name=tool_def["name"],
                            description=tool_def["description"],
                            inputSchema=tool_def["inputSchema"]
                        )
                    )

                response = {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {"tools": [tool.model_dump() for tool in tools]}
                }
            elif request.method == "tools/call":
                # Call a tool
                from .handlers import TOOL_HANDLERS
                from mcp.types import TextContent

                params = request.params or {}
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name not in TOOL_HANDLERS:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "error": {
                            "code": -32602,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }

                # Call handler (wrap in sync_to_async for Django ORM)
                handler = TOOL_HANDLERS[tool_name]
                result_data = await sync_to_async(handler)(arguments or {})

                # Convert to TextContent
                result_text = json.dumps(result_data, indent=2)
                result = [TextContent(type="text", text=result_text)]

                response = {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {"content": [item.model_dump() for item in result]}
                }
            elif request.method == "initialize":
                # Initialize the MCP session
                response = {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "portfolio-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {request.method}"
                    }
                }

            return response

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


async def sse_stream_generator(transport: SSETransport) -> AsyncIterator[str]:
    """Generate SSE stream for client consumption"""
    # Send initial connection message
    yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"

    # Keep connection alive and send messages
    while True:
        try:
            # Wait for messages with timeout for keep-alive
            message = await asyncio.wait_for(
                transport.message_queue.get(),
                timeout=30.0
            )

            # Send message as SSE event
            yield f"data: {json.dumps(message)}\n\n"

        except asyncio.TimeoutError:
            # Send keep-alive ping
            yield f": keepalive\n\n"
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            break


@csrf_exempt
@require_http_methods(["POST"])
async def mcp_sse_endpoint(request):
    """
    HTTP endpoint for MCP requests via SSE

    POST /api/mcp/sse
    Content-Type: application/json

    Body: JSON-RPC request

    Returns: JSON-RPC response
    """
    try:
        # Parse request body
        body = json.loads(request.body.decode('utf-8'))

        # Import server instance
        from .server import app as mcp_server

        # Create transport
        transport = SSETransport(mcp_server)

        # Handle the request
        response_data = await transport.handle_request(body)

        # Return JSON response
        from django.http import JsonResponse
        return JsonResponse(response_data, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error: Invalid JSON"
            }
        }, status=400)
    except Exception as e:
        logger.error(f"Error in MCP SSE endpoint: {e}", exc_info=True)
        return JsonResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
async def mcp_sse_stream(request):
    """
    SSE streaming endpoint for long-lived connections

    GET /api/mcp/stream

    Returns: Server-Sent Events stream
    """
    # Import server instance
    from .server import app as mcp_server

    # Create transport
    transport = SSETransport(mcp_server)

    # Create streaming response
    response = StreamingHttpResponse(
        sse_stream_generator(transport),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'

    return response
