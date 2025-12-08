"""
Authentication middleware for MCP SSE endpoints
Provides API key-based authentication for external access
"""
import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class MCPAuthenticationMiddleware:
    """
    Middleware to authenticate MCP API requests using API keys

    Checks for API key in:
    1. X-API-Key header
    2. Authorization: Bearer <token> header
    3. api_key query parameter (for SSE streams)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to MCP endpoints
        if not request.path.startswith('/api/mcp/'):
            return self.get_response(request)

        # Check for API key
        api_key = self._extract_api_key(request)

        if not api_key:
            return self._unauthorized_response("Missing API key")

        # Validate API key
        if not self._validate_api_key(api_key):
            return self._unauthorized_response("Invalid API key")

        # Store authenticated status on request
        request.mcp_authenticated = True

        return self.get_response(request)

    def _extract_api_key(self, request) -> str:
        """Extract API key from request headers or query params"""
        # Check X-API-Key header
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return api_key

        # Check Authorization header (Bearer token)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix

        # Check query parameter (for SSE streams)
        api_key = request.GET.get('api_key')
        if api_key:
            return api_key

        return None

    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate the provided API key

        In production, this should check against a database of valid keys.
        For now, we check against a setting or environment variable.
        """
        # Get valid API keys from settings
        valid_keys = getattr(settings, 'MCP_API_KEYS', [])

        # Also check MCP_API_KEY environment variable (single key)
        single_key = getattr(settings, 'MCP_API_KEY', None)
        if single_key:
            valid_keys.append(single_key)

        # Allow development mode without authentication
        if settings.DEBUG and not valid_keys:
            logger.warning("MCP authentication bypassed in DEBUG mode with no API keys configured")
            return True

        return api_key in valid_keys

    def _unauthorized_response(self, message: str):
        """Return 401 Unauthorized response"""
        return JsonResponse({
            "error": {
                "code": 401,
                "message": message
            }
        }, status=401)


def require_mcp_auth(view_func):
    """
    Decorator to require MCP authentication on specific views

    Usage:
        @require_mcp_auth
        async def my_view(request):
            ...
    """
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'mcp_authenticated', False):
            return JsonResponse({
                "error": {
                    "code": 401,
                    "message": "Authentication required"
                }
            }, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper
