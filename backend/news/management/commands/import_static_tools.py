from django.core.management.base import BaseCommand

from backend.news.models import Tool
from ._import_helpers import JsonImportFacade

class Command(BaseCommand):
    help = "Import static tools from backend/news/static/news_data/tools.json into the Tool model."

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to tools.json (optional)')
        parser.add_argument('--force', action='store_true', help='Re-import and overwrite existing tools with same url')

    def handle(self, *args, **options):
        # SOLID (SRP): this command now focuses on mapping Tool fields, not JSON IO details.
        # Pattern (Facade): JsonImportFacade centralizes shared file-path and parsing behavior.
        # Benefit: easier maintenance when import file handling needs to change.
        import_facade = JsonImportFacade(self)
        file_path = import_facade.resolve_file_path(options['file'], 'tools.json')
        items = import_facade.load_items(file_path)
        if items is None:
            return

        total_items = len(items) if isinstance(items, list) else 0
        self.stdout.write(self.style.NOTICE(f'Parsed {total_items} items from {file_path}'))

        created = 0
        updated = 0
        for idx, item in enumerate(items, start=1):
            # external_id is deprecated; ignore incoming JSON `id` and dedupe by URL only
            external_id = None
            name = item.get('name')
            description = item.get('description') or ''
            url = item.get('url') or ''
            logo = item.get('logo') or ''
            category = item.get('category') or ''
            subcategories = item.get('subcategories') or []
            pricing = item.get('pricing') or ''
            price_from = item.get('priceFrom')
            rating = item.get('rating')
            tags = item.get('tags') or []

            self.stdout.write(f'Item {idx}/{total_items}: name={name!r} url={url!r}')

            obj = None
            # Dedupe by URL only (external_id not used in this project)
            if url:
                obj = Tool.objects.filter(url=url).first()

            if obj and options.get('force'):
                obj.name = name
                obj.description = description
                obj.url = url
                obj.logo = logo
                obj.category = category
                obj.subcategories = subcategories
                obj.pricing = pricing
                obj.price_from = price_from
                obj.rating = rating
                obj.tags = tags
                obj.raw_payload = item
                obj.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'  Updated tool id={obj.pk}'))
            elif not obj:
                obj = Tool.objects.create(
                    name=name,
                    description=description,
                    url=url,
                    logo=logo,
                    category=category,
                    subcategories=subcategories,
                    pricing=pricing,
                    price_from=price_from,
                    rating=rating,
                    tags=tags,
                    raw_payload=item,
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created tool id={obj.pk}'))

        self.stdout.write(self.style.SUCCESS(f'Import complete. Created: {created}, Updated: {updated}'))
