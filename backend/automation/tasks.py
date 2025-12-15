"""
Task helpers for automation workflows (e.g., creating learning entries).
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple

from django.db import transaction
from groq import Groq

from portfolio.models import LearningEntry, RoadmapItem

logger = logging.getLogger(__name__)


def _roadmap_hint() -> str:
    """
    Build a compact, human-readable roadmap outline for the LLM to reference.
    """
    sections: Dict[str, List[str]] = {}
    for item in RoadmapItem.objects.select_related("section").all():
        section_title = item.section.title if item.section else "Unsectioned"
        sections.setdefault(section_title, []).append(item.title or "")

    if not sections:
        return ""

    lines: List[str] = []
    for section, titles in sections.items():
        deduped = [t for t in dict.fromkeys([t for t in titles if t]).keys()]
        if deduped:
            lines.append(f"- {section}: {', '.join(deduped)}")
        else:
            lines.append(f"- {section}: (no items)")
    return "\n".join(lines)


def _section_bias_tokens() -> Dict[str, List[str]]:
    """
    Heuristic tokens that should strongly bias matching toward specific sections.
    Extendable if new sections are added later.
    """
    return {
        "agents": ["mcp", "agent", "agents", "tool", "tools", "automation"],
        "rag": ["rag", "retrieval", "embedding", "embeddings", "vector", "chunk", "chunks", "chunking", "pgvector"],
    }


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

    text = " ".join(t for t in [summary or "", raw] if t).lower()
    if not text.strip():
        return None

    best_id: Optional[int] = None
    best_score = 0
    bias_tokens = _section_bias_tokens()
    debug_candidates = []

    for item in RoadmapItem.objects.select_related("section").all():
        title = (item.title or "").lower()
        desc = (item.description or "").lower()
        section_title = (item.section.title if item.section else "") or ""

        # Exact phrase matches get a heavy boost
        score = 0
        for phrase, weight in [
            (title, 3),
            (desc, 2),
            (section_title.lower(), 4),
        ]:
            if phrase and phrase in text:
                score += len(phrase) * weight

        # Token-level overlap with variable weights
        tokens: List[tuple[str, int]] = []
        for chunk, weight in [
            (title, 2),
            (desc, 1),
            (section_title.lower(), 3),
        ]:
            if not chunk:
                continue
            for tok in chunk.replace("/", " ").split():
                if len(tok) >= 3:
                    tokens.append((tok, weight))

        for tok, weight in tokens:
            if tok in text:
                score += len(tok) * weight

        # Section bias: strong bonus if text contains bias tokens that map to the section
        section_bias_score = 0
        section_key = "agents" if "agent" in section_title.lower() or "mcp" in section_title.lower() else (
            "rag" if "rag" in section_title.lower() or "vector" in section_title.lower() else None
        )
        if section_key and section_key in bias_tokens:
            for tok in bias_tokens[section_key]:
                if tok in text:
                    section_bias_score += 25
                    break  # one hit is enough for the bonus

        score += section_bias_score

        if score > best_score:
            best_score = score
            best_id = item.id
        debug_candidates.append((item.id, section_title, title, score))

    # Require a minimal match; otherwise return None
    debug_candidates.sort(key=lambda t: t[3], reverse=True)
    if debug_candidates:
        logger.debug(
            "Roadmap match candidates (top 3): %s",
            debug_candidates[:3],
        )

    return best_id if best_score >= 8 else None


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

    roadmap_outline = _roadmap_hint()

    system_prompt = (
        "You write learning-focused summaries of GitHub activity. "
        "Highlight what was built or learned and call out tools, libraries, frameworks, and languages involved. "
        "Do NOT mention repository names, branches, delivery IDs, commit counts, or authors. "
        "Avoid phrases like 'GitHub push' or other transport metadata. "
        "Keep it concise: 1-2 sentences plus 2-4 short bullets, under 120 words total. "
        "Use the provided roadmap outline to infer the most relevant section/item; if high confidence, add one line like "
        "'Likely roadmap: <Section> > <Item>'."
    )

    raw_text = entry.get("content", "")
    event_context = json.dumps(payload, indent=2)
    user_prompt_parts = [
        "Source GitHub event data (JSON):",
        event_context,
        "",
        "Raw text prepared for the log:",
        raw_text,
    ]
    if roadmap_outline:
        user_prompt_parts.extend(["", "Roadmap outline:", roadmap_outline])
    user_prompt_parts.append("")
    user_prompt_parts.append("Write the concise learning-focused summary now.")
    user_prompt = "\n".join(user_prompt_parts)

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


def _build_content_blocks(
    ai_summary: Optional[str],
    entry_content: str,
    roadmap_line: Optional[str],
    roadmap_context: Optional[str],
    dedup_marker: Optional[str],
) -> Tuple[str, str]:
    """
    Returns a tuple of (display_block, content) where content is formatted so the
    summary is shown first, and raw event/meta data is hidden behind a marker.
    """
    display_parts: List[str] = []
    if ai_summary:
        display_parts.append(ai_summary)
    else:
        display_parts.append(entry_content)

    for extra in [roadmap_line, roadmap_context]:
        if extra:
            display_parts.append(extra)

    display_block = "\n\n".join([part for part in display_parts if part and part.strip()])

    meta_parts: List[str] = []
    if ai_summary and dedup_marker:
        meta_parts.append(dedup_marker)
    if ai_summary and entry_content:
        meta_parts.append(entry_content)

    meta_block = ""
    if meta_parts:
        meta_block = f"---\nRaw event:\n" + "\n".join([part for part in meta_parts if part])

    content = "\n\n".join([part for part in [display_block, meta_block] if part])
    return display_block, content


def create_learning_entries_from_events(
    entries: List[Dict[str, Any]],
    delivery_id: Optional[str] = None,
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

            # Prefer mapping by Groq summary/raw text; fallback to naive message match
            roadmap_item_id = (
                _match_roadmap_item_by_text(ai_summary, entry["content"])
                or _guess_roadmap_item_id(messages)
            )

            item = None
            roadmap_line = None
            roadmap_context = None
            if roadmap_item_id:
                item = RoadmapItem.objects.select_related("section").filter(id=roadmap_item_id).first()
                if item and item.section:
                    roadmap_line = f"Related to: {item.section.title} > {item.title}"
                    if item.description:
                        roadmap_context = item.description.strip()

            title = "Learning update"
            if item and item.section:
                title = f"{item.section.order}. {item.section.title}"

            _, content = _build_content_blocks(
                ai_summary=ai_summary,
                entry_content=entry["content"],
                roadmap_line=roadmap_line,
                roadmap_context=roadmap_context,
                dedup_marker=dedup_marker,
            )

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
