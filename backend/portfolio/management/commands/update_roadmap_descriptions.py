"""
Management command to update roadmap item descriptions with meaningful content.
"""

from django.core.management.base import BaseCommand
from portfolio.models import RoadmapSection, RoadmapItem


class Command(BaseCommand):
    help = "Update roadmap item descriptions to include section context"

    def handle(self, *args, **options):
        self.stdout.write("Updating roadmap item descriptions...")

        updated_count = 0

        for section in RoadmapSection.objects.prefetch_related('items').all():
            section_desc = section.description

            for item in section.items.all():
                # Create meaningful description
                new_description = f"{section_desc} Specifically: {item.title}"

                if item.description != new_description:
                    item.description = new_description
                    item.save()
                    updated_count += 1
                    self.stdout.write(f"  ✓ Updated: {item.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Updated {updated_count} roadmap item descriptions"
                f"\n\nNext step: Run 'python manage.py build_knowledge_index' to re-index"
            )
        )
