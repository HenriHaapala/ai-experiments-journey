"""
Task helpers for automation workflows (e.g., creating learning entries).
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional

from django.db import transaction
from groq import Groq

from portfolio.models import LearningEntry, RoadmapItem

logger = logging.getLogger(__name__)


def _guess_roadmap_item_id(messages: List[str]) -> Optional[int]:
    """
    Naive roadmap item matching based on commit messages.
    """
    if not messages:
        return None

    message_blob = " ".join(messages).lower()
    for item in RoadmapItem.objects.all():
        title_lower = (item.title or "").lower()
        if title_lower and title_lower in message_blob:
            return item.id

    return None


def _summarize_entry_with_groq(entry: Dict[str, Any]) -> Optional[str]:
    """
    Use Groq LLM to create a concise learning log summary for a parsed event.
    Returns the summary text or None on failure.
    """
    payload = entry.get("summary_payload")
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not payload or not groq_api_key:
        return None

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as exc:
        logger.error("Unable to initialize Groq client for webhook summarization: %s", exc)
        return None

    system_prompt = (
        "You turn GitHub events into concise learning log entries. "
        "Highlight what was built or learned, mention repo/branch, and keep it factual. "
        "Return 1-2 sentences followed by 3-6 short bullets. Keep it under 150 words."
    )

    raw_text = entry.get("content", "")
    event_context = json.dumps(payload, indent=2)
    user_prompt = (
        "Source GitHub event data (JSON):\n"
        f"{event_context}\n\n"
        "Raw text prepared for the log:\n"
        f"{raw_text}\n\n"
        "Produce a concise learning log summary:"
    )

    try:
        response = client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("Groq summarization failed for webhook delivery: %s", exc)
        return None


def create_learning_entries_from_events(
    entries: List[Dict[str, Any]],
    delivery_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create LearningEntry records from parsed automation events.

    Uses the GitHub delivery ID as a lightweight deduplication marker to avoid
    reprocessing the same webhook delivery. If Groq credentials are present,
    a concise AI summary is prepended to the raw event text for the learning log.
    """
    if not entries:
        return {"created": 0, "skipped": 0, "reason": "no_entries"}

    dedup_marker = f"GitHub Delivery ID: {delivery_id}" if delivery_id else None
    if dedup_marker and LearningEntry.objects.filter(content__icontains=dedup_marker).exists():
        logger.info("Skipping webhook delivery %s (already processed)", delivery_id)
        return {"created": 0, "skipped": len(entries), "reason": "duplicate_delivery"}

    messages: List[str] = []
    for entry in entries:
        messages.extend(entry.get("messages") or [])

    roadmap_item_id = _guess_roadmap_item_id(messages)

    created: List[int] = []
    with transaction.atomic():
        for entry in entries:
            ai_summary = _summarize_entry_with_groq(entry)
            content = entry["content"]

            if ai_summary:
                content = f"{ai_summary}\n\n---\nRaw event:\n{content}"

            created_entry = LearningEntry.objects.create(
                title=entry["title"],
                content=content,
                is_public=entry.get("is_public", True),
                roadmap_item_id=entry.get("roadmap_item_id") or roadmap_item_id
            )
            created.append(created_entry.id)

    return {
        "created": len(created),
        "skipped": 0,
        "roadmap_item_id": roadmap_item_id,
        "entry_ids": created,
    }
