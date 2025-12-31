from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import SecurityAudit
from .serializers import SecurityAuditSerializer

@method_decorator(csrf_exempt, name='dispatch')
class LogSecurityEventView(generics.CreateAPIView):
    """
    Internal API endpoint for Agent Service to log security violations.
    In a real production environment, this should be protected by an internal API key or similar.
    For now, we use AllowAny but in practice it would be restricted.
    """
    queryset = SecurityAudit.objects.all()
    serializer_class = SecurityAuditSerializer
    authentication_classes = [] # Disable default auth (SessionAuth) to avoid CSRF
    permission_classes = [AllowAny] # TODO: Add internal service authentication
