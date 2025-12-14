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


def _match_roadmap_item_by_text(summary: Optional[str], raw: str) -> Optional[int]:
    """
    Try to map the entry to a roadmap item using the Groq summary (preferred) and raw text.
    Simple keyword overlap against roadmap item titles/descriptions.
    """
    if RoadmapItem.objects.count() == 0:
        return None

    text = " ".join(
        t for t in [summary or "", raw] if t
    ).lower()

    best_id: Optional[int] = None
    best_score = 0

    for item in RoadmapItem.objects.select_related("section").all():
        title = (item.title or "").lower()
        desc = (item.description or "").lower()

        score = 0
        for token in [title, desc]:
            if token and token in text:
                score += len(token)

        if score > best_score:
            best_score = score
            best_id = item.id

    # Require a minimal match; otherwise return None
    return best_id if best_score >= 4 else None


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
        "You turn GitHub events into concise learning log entries focused on what was built or learned. "
        "Use commit messages and change details; surface key tools, frameworks, libraries, and languages when present. "
        "Do NOT mention repository names, branches, delivery IDs, commit counts, or authors. "
        "Do NOT use phrases like 'GitHub push'. "
        "Return 1-2 sentences plus 2-4 short bullets. Keep it factual and under 120 words. "
        "Include which roadmap area this likely relates to if you can infer it from the changes."
    )

    raw_text = entry.get("content", "")
    event_context = json.dumps(payload, indent=2)
    user_prompt = (
        "Source GitHub event data (JSON):\n"
        f"{event_context}\n\n"
        "Raw text prepared for the log:\n"
        f"{raw_text}\n\n"
        "Write the learning-focused summary now (no repo/branch/delivery metadata):"
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

    created: List[int] = []
    with transaction.atomic():
        for entry in entries:
            ai_summary = _summarize_entry_with_groq(entry)
            content = entry["content"]

            if ai_summary:
                content = f"{ai_summary}\n\n---\nRaw event:\n{entry['content']}"

            # Prefer mapping by Groq summary/raw text; fallback to naive message match
            roadmap_item_id = (
                _match_roadmap_item_by_text(ai_summary, content)
                or _guess_roadmap_item_id(messages)
            )

            # Compute a nicer title: use roadmap section if matched; else generic update
            title = entry["title"]
            if roadmap_item_id:
                item = RoadmapItem.objects.select_related("section").filter(id=roadmap_item_id).first()
                if item and item.section:
                    title = f"{item.section.order}. {item.section.title}"
                    if ai_summary:
                        # Append roadmap relation for clarity
                        content = (
                            f"{ai_summary}\n\nRelated to: {item.section.title} > {item.title}"
                            f"\n\n---\nRaw event:\n{entry['content']}"
                        )
            elif ai_summary:
                title = "Learning update"

            created_entry = LearningEntry.objects.create(
                title=title,
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
