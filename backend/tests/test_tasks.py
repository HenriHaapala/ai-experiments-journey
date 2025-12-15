import pytest

from automation.tasks import _match_roadmap_item_by_text
from portfolio.models import RoadmapSection, RoadmapItem


@pytest.mark.django_db
def test_match_prefers_agents_section():
    agents_section = RoadmapSection.objects.create(title="2. Agents + MCP", order=2)
    rag_section = RoadmapSection.objects.create(title="3. RAG Systems", order=3)

    agents_item = RoadmapItem.objects.create(
        section=agents_section,
        title="MCP installation, tools, custom tools",
        description="Multi-agent systems and automation",
        order=1,
    )
    RoadmapItem.objects.create(
        section=rag_section,
        title="Embeddings, vector DBs, chunking",
        description="Vector stores and retrieval",
        order=1,
    )

    summary = "Improved Groq webhook for MCP agents and automation of tool calls"
    matched_id = _match_roadmap_item_by_text(summary, raw="")
    assert matched_id == agents_item.id


@pytest.mark.django_db
def test_match_prefers_rag_section():
    agents_section = RoadmapSection.objects.create(title="2. Agents + MCP", order=2)
    rag_section = RoadmapSection.objects.create(title="3. RAG Systems", order=3)

    RoadmapItem.objects.create(
        section=agents_section,
        title="MCP installation, tools, custom tools",
        description="Multi-agent systems and automation",
        order=1,
    )
    rag_item = RoadmapItem.objects.create(
        section=rag_section,
        title="Embeddings, vector DBs, chunking",
        description="Vector stores and retrieval",
        order=1,
    )

    summary = "Added vector DB embeddings and chunking improvements for retrieval"
    matched_id = _match_roadmap_item_by_text(summary, raw="")
    assert matched_id == rag_item.id


@pytest.mark.django_db
def test_match_returns_none_when_no_overlap():
    RoadmapSection.objects.create(title="2. Agents + MCP", order=2)
    RoadmapSection.objects.create(title="3. RAG Systems", order=3)

    summary = "Updated UI colors and typography"
    matched_id = _match_roadmap_item_by_text(summary, raw="")
    assert matched_id is None
