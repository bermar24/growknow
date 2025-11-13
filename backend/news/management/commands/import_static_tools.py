from django.core.management.base import BaseCommand
from pathlib import Path
import json
from backend.news.models import Tool

class Command(BaseCommand):
    help = "Import static tools from backend/news/static/news_data/tools.json into the Tool model."

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to tools.json (optional)')
        parser.add_argument('--force', action='store_true', help='Re-import and overwrite existing tools with same url or external_id')

    def handle(self, *args, **options):
        file_path = options['file'] or Path(__file__).resolve().parent.parent.parent / 'static' / 'news_data' / 'tools.json'
        file_path = Path(file_path)
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                items = json.load(f)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to parse JSON: {e}'))
                return

        total_items = len(items) if isinstance(items, list) else 0
        self.stdout.write(self.style.NOTICE(f'Parsed {total_items} items from {file_path}'))

        created = 0
        updated = 0
        for idx, item in enumerate(items, start=1):
            external_id = str(item.get('id')) if item.get('id') is not None else None
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

            self.stdout.write(f'Item {idx}/{total_items}: name={name!r} external_id={external_id!r} url={url!r}')

            obj = None
            # Prefer dedupe by external_id, then url
            if external_id:
                obj = Tool.objects.filter(external_id=external_id).first()
            if not obj and url:
                obj = Tool.objects.filter(url=url).first()

            if obj and options.get('force'):
                obj.external_id = external_id
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
                    external_id=external_id,
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

