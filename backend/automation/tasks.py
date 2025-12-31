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
        "agents": {
            "section_keywords": ["agent", "mcp", "automation", "tool"],
            "tokens": ["mcp", "agent", "agents", "tool", "tools", "automation", "webhook", "orchestration"],
            "paths": ["automation/", "mcp_server/", "agent_service/", "scripts/agents"],
        },
        "rag": {
            "section_keywords": ["rag", "vector", "embedding", "search"],
            "tokens": ["rag", "retrieval", "embedding", "embeddings", "vector", "chunk", "chunks", "chunking", "pgvector", "similarity", "index"],
            "paths": ["vector", "embedding", "rag", "search", "knowledge"],
        },
        "safety": {
            "section_keywords": ["safety", "security", "guardrail", "audit", "evaluation", "bias"],
            "tokens": ["security", "guardrail", "guardrails", "audit", "safety", "jailbreak", "attack", "defense", "bias", "eval", "evaluation"],
            "paths": ["security", "audit", "guardrail", "safety", "tests/security"],
        },
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


def _match_roadmap_item_by_text(
    summary: Optional[str],
    raw: str,
    files: Optional[List[str]] = None,
    llm_candidates: Optional[List[Dict[str, Any]]] = None,
) -> Optional[int]:
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
    taxonomy = _section_bias_tokens()
    debug_candidates = []
    file_paths = files or []

    for item in RoadmapItem.objects.select_related("section").all():
        title = (item.title or "").lower()
        desc = (item.description or "").lower()
        section_title = (item.section.title if item.section else "") or ""
        section_title_lower = section_title.lower()

        # Exact phrase matches get a heavy boost
        score = 0
        for phrase, weight in [
            (title, 3),
            (desc, 2),
            (section_title_lower, 4),
        ]:
            if phrase and phrase in text:
                score += len(phrase) * weight

        # Token-level overlap with variable weights
        tokens: List[tuple[str, int]] = []
        for chunk, weight in [
            (title, 2),
            (desc, 1),
            (section_title_lower, 3),
        ]:
            if not chunk:
                continue
            for tok in chunk.replace("/", " ").split():
                if len(tok) >= 3:
                    tokens.append((tok, weight))

        for tok, weight in tokens:
            if tok in text:
                score += len(tok) * weight

        # Section bias: strong bonus if text or file paths contain bias tokens that map to the section
        section_bias_score = 0
        section_key = None
        for key, cfg in taxonomy.items():
            for kw in cfg.get("section_keywords", []):
                if kw in section_title_lower:
                    section_key = key
                    break
            if section_key:
                break

        if section_key and section_key in taxonomy:
            for tok in taxonomy[section_key].get("tokens", []):
                if tok in text:
                    section_bias_score += 25
                    break  # one token hit is enough
            for path in taxonomy[section_key].get("paths", []):
                if any(path in fp.lower() for fp in file_paths):
                    section_bias_score += 25
                    break

        # Bonus if LLM suggested this item/section with confidence
        llm_bonus = 0
        if llm_candidates:
            for cand in llm_candidates:
                item_name = (cand.get("item") or "").lower()
                section_name = (cand.get("section") or "").lower()
                conf = float(cand.get("confidence", 0))
                if conf <= 0:
                    continue
                if item_name and item_name == title:
                    llm_bonus = max(llm_bonus, int(conf * 50))
                elif section_name and section_name == section_title_lower:
                    llm_bonus = max(llm_bonus, int(conf * 25))

        # Penalize very broad sections (e.g., Foundations) when no section-specific tokens matched
        broad_section_penalty = 0
        if "foundation" in section_title_lower and section_bias_score == 0:
            broad_section_penalty = 15

        score += section_bias_score + llm_bonus - broad_section_penalty

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


def _summarize_entry_with_groq(entry: Dict[str, Any]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Use Groq LLM to create a concise learning log summary for a parsed event.
    Returns (summary text, roadmap_candidates) where roadmap_candidates is a list of
    {section, item, confidence} suggested by the LLM. Summary may be None on failure.
    """
    payload = entry.get("summary_payload")
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not payload or not groq_api_key:
        return None, []

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as exc:
        logger.error("Unable to initialize Groq client for webhook summarization: %s", exc)
        return None, []

    roadmap_outline = _roadmap_hint()

    system_prompt = (
        "You write learning-focused summaries of GitHub activity. "
        "Highlight what was built or learned and call out tools, libraries, frameworks, and languages involved. "
        "Do NOT mention repository names, branches, delivery IDs, commit counts, or authors. "
        "Avoid phrases like 'GitHub push' or other transport metadata. "
        "Keep it concise: 1-2 sentences plus 2-4 short bullets, under 120 words total. "
        "Also return the top 2 roadmap candidates using ONLY the section/item names from the provided outline, "
        "with confidence 0-1."
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
    user_prompt_parts.append(
        "Return JSON with fields: summary (string) and roadmap_candidates (array of {section, item, confidence}). "
        "Use exact section/item names from the outline."
    )
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
        content = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Try to recover from fenced JSON blocks
            if "```" in content:
                fenced = content.split("```")
                for block in fenced:
                    block = block.strip()
                    if block.startswith("{") and block.endswith("}"):
                        try:
                            parsed = json.loads(block)
                            break
                        except json.JSONDecodeError:
                            continue
            else:
                parsed = None

        if parsed and isinstance(parsed, dict) and "summary" in parsed:
            summary_text = (parsed.get("summary") or "").strip() or None
            candidates = parsed.get("roadmap_candidates") or []
            if not isinstance(candidates, list):
                candidates = []
            return summary_text, candidates

        return content, []
    except Exception as exc:
        logger.error("Groq summarization failed for webhook delivery: %s", exc)
        return None, []


def _build_content_blocks(
    ai_summary: Optional[str],
    entry_content: str,
    roadmap_line: Optional[str],
    roadmap_context: Optional[str],
    dedup_marker: Optional[str],
    file_paths: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Returns a tuple of (display_block, content) where content is formatted so the
    summary is shown first, and raw event/meta data is hidden behind a marker.
    """
    display_parts: List[str] = []
    summary_text = ai_summary or "Learning update captured automatically; raw event stored separately."
    display_parts.append(summary_text)

    for extra in [roadmap_line, roadmap_context]:
        if extra:
            display_parts.append(extra)

    if file_paths:
        unique_files = sorted(set(file_paths))
        display_parts.append("Files changed:")
        display_parts.extend(unique_files)

    display_block = "\n\n".join([part for part in display_parts if part and part.strip()])

    meta_parts: List[str] = []
    if dedup_marker:
        meta_parts.append(dedup_marker)

    meta_block = ""
    if meta_parts:
        meta_block = f"---\nRaw event:\n" + "\n".join([part for part in meta_parts if part])

    content = "\n\n".join([part for part in [display_block, meta_block] if part])
    return display_block, content


def _select_item_from_llm_candidates(candidates: List[Dict[str, Any]], confidence_threshold: float = 0.6) -> Optional[int]:
    """
    Find the best RoadmapItem id from LLM-proposed candidates when confidence is high enough.
    """
    if not candidates:
        return None

    ordered = sorted(
        candidates,
        key=lambda c: float(c.get("confidence", 0) or 0),
        reverse=True,
    )
    for cand in ordered:
        conf = float(cand.get("confidence", 0) or 0)
        if conf < confidence_threshold:
            continue
        item_name = (cand.get("item") or "").strip().lower()
        section_name = (cand.get("section") or "").strip().lower()

        qs = RoadmapItem.objects.select_related("section").all()
        if item_name:
            qs = qs.filter(title__iexact=item_name)
        if section_name:
            qs = qs.filter(section__title__iexact=section_name) if item_name else qs.filter(section__title__iexact=section_name)

        match = qs.first()
        if match:
            return match.id

    return None


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
            ai_summary, llm_candidates = _summarize_entry_with_groq(entry)
            file_paths = entry.get("files") or (entry.get("summary_payload") or {}).get("files") or []

            llm_match_id = _select_item_from_llm_candidates(llm_candidates)

            # Prefer mapping by Groq summary/raw text; fallback to naive message match
            roadmap_item_id = (
                llm_match_id
                or _match_roadmap_item_by_text(
                    ai_summary,
                    entry["content"],
                    files=file_paths,
                    llm_candidates=llm_candidates,
                )
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
                file_paths=file_paths,
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
