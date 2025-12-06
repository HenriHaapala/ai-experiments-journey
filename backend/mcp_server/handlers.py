"""
MCP Tool Handlers
Implements the actual logic for each MCP tool using Django ORM
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from portfolio.models import RoadmapSection, RoadmapItem, LearningEntry, KnowledgeChunk
from django.db.models import Q, Count
import cohere


def generate_embedding(text: str) -> list[float]:
    """Generate embedding for text using Cohere"""
    api_key = os.getenv("COHERE_API_KEY")
    model_name = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")

    client = cohere.Client(api_key=api_key)
    text = text.strip()[:8000]  # Limit length

    resp = client.embed(
        texts=[text],
        model=model_name,
        input_type="search_query",
    )
    return resp.embeddings[0]


def handle_get_roadmap(arguments: dict) -> dict:
    """Get the complete AI Career Roadmap"""
    sections = RoadmapSection.objects.prefetch_related('items').all().order_by('order')
    
    roadmap_data = []
    for section in sections:
        items = []
        for item in section.items.all().order_by('order'):
            items.append({
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "order": item.order,
                "is_active": item.is_active
            })
        
        roadmap_data.append({
            "id": section.id,
            "title": section.title,
            "description": section.description,
            "order": section.order,
            "items": items
        })
    
    return {
        "success": True,
        "roadmap": roadmap_data,
        "total_sections": len(roadmap_data),
        "total_items": sum(len(s["items"]) for s in roadmap_data)
    }


def handle_get_learning_entries(arguments: dict) -> dict:
    """Get learning log entries"""
    roadmap_item_id = arguments.get("roadmap_item_id")
    limit = arguments.get("limit", 10)
    
    queryset = LearningEntry.objects.select_related('roadmap_item').all()
    
    if roadmap_item_id:
        queryset = queryset.filter(roadmap_item_id=roadmap_item_id)
    
    entries = queryset.order_by('-created_at')[:limit]
    
    entries_data = []
    for entry in entries:
        entries_data.append({
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "roadmap_item": entry.roadmap_item.title if entry.roadmap_item else None,
            "is_public": entry.is_public,
            "created_at": entry.created_at.isoformat()
        })
    
    return {
        "success": True,
        "entries": entries_data,
        "count": len(entries_data)
    }


def handle_search_knowledge(arguments: dict) -> dict:
    """Semantic search using RAG"""
    query = arguments.get("query")
    top_k = arguments.get("top_k", 5)
    
    if not query:
        return {"success": False, "error": "Query is required"}
    
    # Generate query embedding
    query_vector = generate_embedding(query)
    
    # Perform vector similarity search
    chunks = KnowledgeChunk.objects.annotate(
        similarity=KnowledgeChunk.objects.cosine_similarity('embedding', query_vector)
    ).order_by('-similarity')[:top_k]
    
    results = []
    for chunk in chunks:
        results.append({
            "id": chunk.id,
            "title": chunk.title,
            "content": chunk.content[:500],  # Truncate for brevity
            "source_type": chunk.source_type,
            "section_title": chunk.section_title or "",
            "similarity": float(getattr(chunk, 'similarity', 0))
        })
    
    return {
        "success": True,
        "results": results,
        "query": query,
        "count": len(results)
    }


def handle_add_learning_entry(arguments: dict) -> dict:
    """Create a new learning entry"""
    title = arguments.get("title")
    content = arguments.get("content")
    roadmap_item_id = arguments.get("roadmap_item_id")
    is_public = arguments.get("is_public", True)
    
    if not title or not content:
        return {"success": False, "error": "Title and content are required"}
    
    # Create the entry
    entry_data = {
        "title": title,
        "content": content,
        "is_public": is_public
    }
    
    if roadmap_item_id:
        try:
            roadmap_item = RoadmapItem.objects.get(id=roadmap_item_id)
            entry_data["roadmap_item"] = roadmap_item
        except RoadmapItem.DoesNotExist:
            return {"success": False, "error": f"Roadmap item {roadmap_item_id} not found"}
    
    entry = LearningEntry.objects.create(**entry_data)
    
    # Generate embedding for the entry (triggers KnowledgeChunk creation via signal)
    # The signal handler in models.py will automatically create the KnowledgeChunk
    
    return {
        "success": True,
        "entry": {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "created_at": entry.created_at.isoformat()
        }
    }


def handle_get_progress_stats(arguments: dict) -> dict:
    """Get portfolio progress statistics"""
    
    # Roadmap stats
    total_sections = RoadmapSection.objects.count()
    total_items = RoadmapItem.objects.count()
    active_items = RoadmapItem.objects.filter(is_active=True).count()
    items_with_entries = RoadmapItem.objects.annotate(
        entry_count=Count('learning_entries')
    ).filter(entry_count__gt=0).count()

    # Learning entries stats
    total_entries = LearningEntry.objects.count()
    public_entries = LearningEntry.objects.filter(is_public=True).count()

    # Knowledge base stats
    total_chunks = KnowledgeChunk.objects.count()
    chunks_by_source = {}
    for source_type in ['learning_entry', 'roadmap_item', 'site_content', 'document']:
        count = KnowledgeChunk.objects.filter(source_type=source_type).count()
        chunks_by_source[source_type] = count

    # Calculate completion percentage (items with learning entries)
    completion_percentage = (items_with_entries / total_items * 100) if total_items > 0 else 0

    return {
        "success": True,
        "stats": {
            "roadmap": {
                "total_sections": total_sections,
                "total_items": total_items,
                "active_items": active_items,
                "items_with_entries": items_with_entries,
                "completion_percentage": round(completion_percentage, 2)
            },
            "learning": {
                "total_entries": total_entries,
                "public_entries": public_entries,
                "private_entries": total_entries - public_entries
            },
            "knowledge_base": {
                "total_chunks": total_chunks,
                "by_source": chunks_by_source
            }
        }
    }


# Tool handler registry
TOOL_HANDLERS = {
    "get_roadmap": handle_get_roadmap,
    "get_learning_entries": handle_get_learning_entries,
    "search_knowledge": handle_search_knowledge,
    "add_learning_entry": handle_add_learning_entry,
    "get_progress_stats": handle_get_progress_stats
}
