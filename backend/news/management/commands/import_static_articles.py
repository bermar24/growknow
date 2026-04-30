from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model

from backend.news.models import NewsArticle, ArticleStatus
from ._import_helpers import JsonImportFacade


class ArticleImportProcessor:
    """Handles extraction, deduplication, and CRUD operations for article imports."""

    def __init__(self, command_instance):
        """
        Args:
            command_instance: Django BaseCommand instance for output/styling
        """
        self.cmd = command_instance
        self.created = 0
        self.updated = 0

    def _parse_published_date(self, pub_str):
        """Parse published date string; return None on failure."""
        if not pub_str:
            return None
        try:
            return parse_datetime(pub_str)
        except Exception:
            return None

    def _extract_article_data(self, item):
        """
        Extract and normalize article fields from JSON item.

        Returns dict with mapped fields handling multiple JSON shape variations.
        """
        title = item.get('title') or item.get('headline') or 'Untitled'
        content = item.get('content') or item.get('summary') or ''
        source_link = item.get('url') or (item.get('source') and item.get('source').get('url')) or ''

        tags = item.get('tags') or item.get('industry_tags') or []
        industry_tags = tags if isinstance(tags, list) else [tags]

        pub_str = item.get('publishedAt') or item.get('published_at')
        published_at = self._parse_published_date(pub_str)

        dedupe_key = source_link or title
        relevance_score = item.get('relevance_score', 0.0)

        return {
            'title': title,
            'content': content,
            'source_link': source_link,
            'published_at': published_at,
            'industry_tags': industry_tags,
            'dedupe_key': dedupe_key,
            'relevance_score': relevance_score,
        }

    def _setup_author(self, author_username):
        """
        Set up author user; return (author_user_obj, author_value_string).

        author_user_obj is None if user not found; author_value_string is used for articles.
        """
        if not author_username:
            return None, None

        User = get_user_model()
        author_user = None
        try:
            author_user = User.objects.get(username=author_username)
        except User.DoesNotExist:
            self.cmd.stdout.write(
                self.cmd.style.WARNING(
                    f"Author username '{author_username}' not found; "
                    f"imported articles will have author='{author_username}' as text."
                )
            )
        return author_user, author_username

    def _find_existing_article(self, dedupe_key, source_link, title):
        """Find existing article by source_link or title; return None if not found."""
        if not dedupe_key:
            return None

        if source_link:
            qs = NewsArticle.objects.filter(source_link=source_link)
        else:
            qs = NewsArticle.objects.filter(title=title)

        return qs.first() if qs.exists() else None

    def _update_or_create_article(self, obj, article_data, author_value, force):
        """
        Update existing article if force=True, otherwise create new.

        Returns (was_created, was_updated) tuple.
        """
        if obj and force:
            # Update fields
            obj.title = article_data['title']
            obj.content = article_data['content']
            obj.published_at = article_data['published_at']
            obj.relevance_score = article_data['relevance_score']
            obj.industry_tags = article_data['industry_tags']
            if author_value:
                obj.author = author_value
            obj.save()
            self.cmd.stdout.write(self.cmd.style.SUCCESS(f'  Updated object id={obj.pk}'))
            return False, True

        if not obj:
            # Create new article
            status = ArticleStatus.PUBLISHED if article_data['published_at'] else ArticleStatus.DRAFT
            obj = NewsArticle.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                source_link=article_data['source_link'],
                status=status,
                published_at=article_data['published_at'],
                author=author_value,
                relevance_score=article_data['relevance_score'],
                industry_tags=article_data['industry_tags'],
            )
            self.cmd.stdout.write(self.cmd.style.SUCCESS(f'  Created object id={obj.pk}'))
            return True, False

        return False, False

    def process_items(self, items, author_value, force):
        """
        Process list of items; create/update articles as needed.

        Returns tuple (created_count, updated_count).
        """
        total_items = len(items) if isinstance(items, list) else 0
        self.cmd.stdout.write(
            self.cmd.style.NOTICE(f'Processing {total_items} items')
        )

        for idx, item in enumerate(items, start=1):
            article_data = self._extract_article_data(item)
            dedupe_key = article_data['dedupe_key']

            self.cmd.stdout.write(
                f"Item {idx}/{total_items}: "
                f"title={article_data['title']!r} "
                f"source_link={article_data['source_link']!r}"
            )

            obj = self._find_existing_article(
                dedupe_key,
                article_data['source_link'],
                article_data['title']
            )

            if obj:
                self.cmd.stdout.write(
                    f'  Found existing object with id={obj.pk} for dedupe_key={dedupe_key!r}'
                )

            was_created, was_updated = self._update_or_create_article(
                obj, article_data, author_value, force
            )

            if was_created:
                self.created += 1
            elif was_updated:
                self.updated += 1

        return self.created, self.updated


class Command(BaseCommand):
    help = "Import static articles from backend/news/static/news_data/articles.json into the NewsArticle model."

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to articles.json (optional)')
        parser.add_argument('--author', type=str, help='Username to set as author for imported articles (optional)')
        parser.add_argument('--force', action='store_true', help='Re-import and overwrite existing articles with same source_link')

    def handle(self, *args, **options):
        """
        Main entry point: orchestrate file loading and article import.

        SOLID (SRP): command keeps orchestration; processor handles data transformation & CRUD.
        Pattern (Facade + Strategy): JsonImportFacade + ArticleImportProcessor separate concerns.
        Benefit: lower cyclomatic complexity, testable logic, reusable processor.
        """
        import_facade = JsonImportFacade(self)
        file_path = import_facade.resolve_file_path(options['file'], 'articles.json')

        # Set up author if provided
        processor = ArticleImportProcessor(self)
        _, author_value = processor._setup_author(options.get('author'))

        # Load items from file
        items = import_facade.load_items(file_path)
        if items is None:
            return

        # Process items and track results
        created, updated = processor.process_items(
            items,
            author_value,
            options.get('force', False)
        )

        self.stdout.write(
            self.style.SUCCESS(f'Import complete. Created: {created}, Updated: {updated}')
        )

