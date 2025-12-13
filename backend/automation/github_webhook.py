"""
GitHub webhook endpoint for automatic learning log generation.
"""
import hmac
import hashlib
import json
import logging
import os
from typing import Any, Dict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .parsers import parse_push_event, parse_pull_request_event
from .tasks import create_learning_entries_from_events

logger = logging.getLogger(__name__)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def _verify_signature(secret: str, payload: bytes, signature_header: str) -> bool:
    """
    Validate the GitHub webhook signature.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    received_sig = signature_header.split("sha256=")[-1]
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, received_sig)


@method_decorator(csrf_exempt, name="dispatch")
class GitHubWebhookView(APIView):
    """
    Handle GitHub webhooks and convert supported events into learning log entries.
    """
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if not GITHUB_WEBHOOK_SECRET:
            return JsonResponse(
                {"success": False, "error": "GITHUB_WEBHOOK_SECRET not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")
        delivery_id = request.headers.get("X-GitHub-Delivery", "")

        if not _verify_signature(GITHUB_WEBHOOK_SECRET, request.body, signature):
            logger.warning("Invalid GitHub webhook signature (delivery %s)", delivery_id)
            return JsonResponse(
                {"success": False, "error": "Invalid signature"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload: Dict[str, Any] = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Invalid JSON payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event_type == "ping":
            return JsonResponse({"success": True, "message": "pong"})

        if event_type == "push":
            parsed_entries = parse_push_event(payload, delivery_id=delivery_id)
            result = create_learning_entries_from_events(parsed_entries, delivery_id=delivery_id)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Processed push event",
                    "created": result.get("created", 0),
                    "skipped": result.get("skipped", 0),
                    "roadmap_item_id": result.get("roadmap_item_id"),
                },
                status=status.HTTP_201_CREATED if result.get("created") else status.HTTP_200_OK,
            )

        if event_type == "pull_request":
            parsed_entries = parse_pull_request_event(payload, delivery_id=delivery_id)
            if not parsed_entries:
                return JsonResponse(
                    {"success": True, "message": "Ignored pull_request action"},
                    status=status.HTTP_200_OK,
                )
            result = create_learning_entries_from_events(parsed_entries, delivery_id=delivery_id)
            return JsonResponse(
                {
                    "success": True,
                    "message": "Processed pull_request event",
                    "created": result.get("created", 0),
                    "skipped": result.get("skipped", 0),
                    "roadmap_item_id": result.get("roadmap_item_id"),
                },
                status=status.HTTP_201_CREATED if result.get("created") else status.HTTP_200_OK,
            )

        return JsonResponse(
            {"success": True, "message": f"Ignored unsupported event '{event_type}'"},
            status=status.HTTP_200_OK,
        )
