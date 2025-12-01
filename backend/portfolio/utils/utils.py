from typing import Any, Dict, List, Tuple, Optional

from django.db.models import F
from pgvector.django import CosineDistance

from ..models import KnowledgeChunk


def smart_retrieve(
    query_vector: List[float],
    *,
    top_k: int = 5,
    candidate_k: Optional[int] = None,
    source_types: Optional[List[str]] = None,
    document_id: Optional[int] = None,
) -> Tuple[List[KnowledgeChunk], Dict[str, Any]]:
    """
    Robust retrieval that works with any amount of data.

    - Always returns up to top_k chunks if ANY exist that match the filters.
    - NEVER drops all chunks just because similarities are low.
    - Uses candidate_k > top_k for better ordering, but falls back safely.
    - Provides confidence + debug info, but debug does NOT remove results.

    Arguments:
        query_vector: embedding of the query
        top_k: how many chunks to finally return (like your old [:5])
        candidate_k: how many to fetch from DB before ranking
                     (default = max(top_k, 16))
        source_types: optional list of KnowledgeChunk.source_type values
        document_id: optional DocumentUpload.id (only chunks from that doc)
    """

    qs = KnowledgeChunk.objects.all()

    # Optional filters (but they must NEVER silently kill everything)
    if source_types:
        qs = qs.filter(source_type__in=source_types)

    if document_id is not None:
        qs = qs.filter(
            source_type=KnowledgeChunk.SourceType.DOCUMENT,
            source_id=document_id,
        )

    # If after filters there is nothing, we genuinely have no data
    total_available = qs.count()
    if total_available == 0:
        debug: Dict[str, Any] = {
            "status": "no_results",
            "reason": "no_rows_after_filters",
            "scores": [],
            "top_k": top_k,
            "candidate_k": candidate_k,
            "filters": {
                "source_types": source_types,
                "document_id": document_id,
            },
        }
        return [], debug

    # Candidate_k: how many to pull BEFORE we rank
    if candidate_k is None:
        candidate_k = max(top_k, 16)

    candidate_k = min(candidate_k, total_available)

    raw_qs = (
        qs.annotate(distance=CosineDistance(F("vector"), query_vector))
        .order_by("distance")[:candidate_k]
    )

    # If somehow this is empty, treat as no results
    if not raw_qs:
        debug = {
            "status": "no_results",
            "reason": "annotate_order_empty",
            "scores": [],
            "top_k": top_k,
            "candidate_k": candidate_k,
            "filters": {
                "source_types": source_types,
                "document_id": document_id,
            },
        }
        return [], debug

    # Compute similarities for diagnostics (NOT for hard filtering)
    scored: List[Tuple[KnowledgeChunk, float]] = []
    for ch in raw_qs:
        # CosineDistance ∈ [0, 2], lower is better; we map to rough similarity
        sim = 1.0 - float(ch.distance)
        scored.append((ch, sim))

    # Sort highest similarity first
    scored.sort(key=lambda x: x[1], reverse=True)

    # Take up to top_k – but DO NOT drop everything based on sim
    top = scored[:top_k]
    chunks = [c for c, _ in top]
    scores = [s for _, s in top]

    # There MUST be at least one chunk here if raw_qs wasn’t empty
    max_score = max(scores) if scores else 0.0
    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Confidence classification is only for info
    if not scores:
        status = "no_results"
    elif max_score < 0.2:
        status = "very_low_confidence"
    elif max_score < 0.4:
        status = "low_confidence"
    else:
        status = "ok"

    debug = {
        "status": status,
        "scores": scores,
        "max_score": max_score,
        "avg_score": avg_score,
        "top_k": top_k,
        "candidate_k": candidate_k,
        "total_available": total_available,
        "returned": len(chunks),
        "filters": {
            "source_types": source_types,
            "document_id": document_id,
        },
    }

    return chunks, debug