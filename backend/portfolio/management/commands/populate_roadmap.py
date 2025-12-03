"""
Management command to populate the AI Career Roadmap from the 2025 edition.
Based on the roadmap PDF structure.
"""

from django.core.management.base import BaseCommand
from portfolio.models import RoadmapSection, RoadmapItem


class Command(BaseCommand):
    help = "Populate AI Career Roadmap sections and items from the 2025 edition"

    def handle(self, *args, **options):
        self.stdout.write("Populating AI Career Roadmap (2025 Edition)...")

        # Define the roadmap structure based on the PDF
        roadmap_data = [
            {
                "title": "Foundations",
                "description": "Core understanding of LLMs, prompting, safety, and CS basics.",
                "order": 1,
                "items": [
                    "Core understanding of LLMs, prompting, safety",
                    "Practical AI use: ChatGPT, Claude, structured outputs",
                    "CS basics: Python, Git, Linux, JSON, APIs",
                ],
            },
            {
                "title": "Agents + MCP",
                "description": "MCP installation, multi-agent systems, and AI-controlled automation.",
                "order": 2,
                "items": [
                    "MCP installation, tools, custom tools",
                    "Multi-agent systems and automation",
                    "AI controlling local tools, pipelines, APIs",
                ],
            },
            {
                "title": "RAG Systems",
                "description": "Embeddings, vector databases, retrieval pipelines, and document assistants.",
                "order": 3,
                "items": [
                    "Embeddings, vector DBs, chunking",
                    "Retrieval pipelines, grounding, evaluation",
                    "Building PDF and multi-doc assistants",
                ],
            },
            {
                "title": "Image AI",
                "description": "Stable Diffusion tools, LoRA training, and model automation.",
                "order": 4,
                "items": [
                    "SD tools, ControlNet, LoRA usage",
                    "LoRA training, DreamBooth, dataset creation",
                    "Model merging, ComfyUI automation",
                ],
            },
            {
                "title": "LLM Fine-Tuning",
                "description": "QLoRA, SFT, PEFT techniques for custom model training.",
                "order": 5,
                "items": [
                    "QLoRA, SFT, PEFT, Axolotl",
                    "Persona, domain, coding fine-tunes",
                ],
            },
            {
                "title": "Training Your Own Models",
                "description": "Math essentials, transformer internals, and multi-GPU training.",
                "order": 6,
                "items": [
                    "Math essentials: linear algebra, probability",
                    "Transformer internals, tokenizers",
                    "Multi-GPU training, FSDP, DeepSpeed",
                ],
            },
            {
                "title": "Deployment & Infrastructure",
                "description": "FastAPI, model serving, Docker, Kubernetes, and production monitoring.",
                "order": 7,
                "items": [
                    "FastAPI, VLLM, model serving",
                    "Docker, Kubernetes, cloud GPU hosting",
                    "Monitoring, logging, cost optimization",
                ],
            },
            {
                "title": "Multimodal AI",
                "description": "Speech, TTS, Whisper, video diffusion, and multimodal LLMs.",
                "order": 8,
                "items": [
                    "Speech, TTS, Whisper",
                    "Video diffusion, multimodal LLMs",
                ],
            },
            {
                "title": "Safety & Evaluation",
                "description": "Guardrails, bias reduction, benchmarks, and evaluation methods.",
                "order": 9,
                "items": [
                    "Guardrails, bias reduction",
                    "Benchmarks and evaluation methods",
                ],
            },
            {
                "title": "Product & Career",
                "description": "Turning AI into products, portfolio building, and interview prep.",
                "order": 10,
                "items": [
                    "Turning AI into products",
                    "Portfolio building, interviews",
                ],
            },
        ]

        # Create sections and items
        sections_created = 0
        items_created = 0

        for section_data in roadmap_data:
            # Create or get the section
            section, created = RoadmapSection.objects.get_or_create(
                title=section_data["title"],
                defaults={
                    "description": section_data["description"],
                    "order": section_data["order"],
                },
            )

            if created:
                sections_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created section: {section.title}")
                )
            else:
                self.stdout.write(f"  Section already exists: {section.title}")

            # Create items for this section
            for idx, item_title in enumerate(section_data["items"], start=1):
                # Create a meaningful description by combining section context with item
                item_description = f"{section_data['description']} Specifically: {item_title}"

                item, item_created = RoadmapItem.objects.get_or_create(
                    section=section,
                    title=item_title,
                    defaults={
                        "order": idx,
                        "is_active": True,
                        "description": item_description,
                    },
                )

                if item_created:
                    items_created += 1
                    self.stdout.write(f"  ✓ Created item: {item_title}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Roadmap population complete!"
                f"\n  Sections created: {sections_created}"
                f"\n  Items created: {items_created}"
                f"\n\nNext steps:"
                f"\n  1. Run: python manage.py build_knowledge_index"
                f"\n  2. Test your RAG system with roadmap questions"
            )
        )
