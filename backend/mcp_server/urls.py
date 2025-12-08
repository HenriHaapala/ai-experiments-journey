"""
URL routing for MCP Server SSE endpoints
"""
from django.urls import path
from .transports import mcp_sse_endpoint, mcp_sse_stream

urlpatterns = [
    # JSON-RPC POST endpoint
    path('sse/', mcp_sse_endpoint, name='mcp_sse'),

    # SSE streaming endpoint
    path('stream/', mcp_sse_stream, name='mcp_stream'),
]
