from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from pathlib import Path
import json
from backend.news.models import NewsArticle, ArticleStatus


class Command(BaseCommand):
    help = "Import static articles from backend/news/static/news_data/articles.json into the NewsArticle model."

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to articles.json (optional)')
        parser.add_argument('--author', type=str, help='Username to set as author for imported articles (optional)')
        parser.add_argument('--force', action='store_true', help='Re-import and overwrite existing articles with same source_link')

    def handle(self, *args, **options):
        file_path = options['file'] or Path(__file__).resolve().parent.parent.parent / 'static' / 'news_data' / 'articles.json'
        file_path = Path(file_path)
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        author_user = None
        author_value = None
        if options.get('author'):
            # We'll store the username string in the article's `author` field. If a matching
            # User exists locally we'll still note it (not used for storage) so the caller
            # gets a warning if the username doesn't exist.
            author_value = options['author']
            User = get_user_model()
            try:
                author_user = User.objects.get(username=options['author'])
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Author username '{options['author']}' not found; imported articles will have author='{author_value}' as text."))

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                items = json.load(f)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to parse JSON: {e}'))
                return

        # Diagnostic: show how many items were parsed
        total_items = len(items) if isinstance(items, list) else 0
        self.stdout.write(self.style.NOTICE(f'Parsed {total_items} items from {file_path}'))

        created = 0
        updated = 0
        for idx, item in enumerate(items, start=1):
            # Map JSON shape to model fields
            title = item.get('title') or item.get('headline') or 'Untitled'
            # Prefer detailed content, otherwise summary
            content = item.get('content') or item.get('summary') or ''
            # Source link may be at url or source.url
            source_link = item.get('url') or (item.get('source') and item.get('source').get('url')) or ''

            # Diagnostic per-item
            self.stdout.write(f'Item {idx}/{total_items}: title={title!r} source_link={source_link!r}')

            # Try parsing publishedAt into timezone-aware datetime
            published_at = None
            pub_str = item.get('publishedAt') or item.get('published_at')
            if pub_str:
                try:
                    published_at = parse_datetime(pub_str)
                except Exception:
                    published_at = None

            tags = item.get('tags') or item.get('industry_tags') or []
            # industry_tags field in model expects a list
            industry_tags = tags if isinstance(tags, list) else [tags]

            # Use source_link as dedupe key; if empty, try title
            dedupe_key = source_link or title

            obj = None
            if dedupe_key:
                qs = NewsArticle.objects.filter(source_link=source_link) if source_link else NewsArticle.objects.filter(title=title)
                if qs.exists():
                    obj = qs.first()
                    self.stdout.write(f'  Found existing object with id={obj.pk} for dedupe_key={dedupe_key!r}')
                    if options.get('force'):
                        # overwrite fields
                        obj.title = title
                        obj.content = content
                        obj.published_at = published_at
                        obj.relevance_score = item.get('relevance_score', 0.0)
                        obj.industry_tags = industry_tags
                        if author_value:
                            obj.author = author_value
                        obj.save()
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(f'  Updated object id={obj.pk}'))
                else:
                    obj = None

            if not obj:
                obj = NewsArticle.objects.create(
                    title=title,
                    content=content,
                    source_link=source_link,
                    status=ArticleStatus.PUBLISHED if published_at else ArticleStatus.DRAFT,
                    published_at=published_at,
                    author=author_value,
                    relevance_score=item.get('relevance_score', 0.0),
                    industry_tags=industry_tags,
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created object id={obj.pk}'))

        self.stdout.write(self.style.SUCCESS(f'Import complete. Created: {created}, Updated: {updated}'))
