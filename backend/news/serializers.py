from rest_framework import serializers
from .models import NewsArticle, Tool


class NewsArticleSerializer(serializers.ModelSerializer):
    # Map model fields to frontend-friendly keys
    publishedAt = serializers.DateTimeField(source='published_at', allow_null=True)
    summary = serializers.CharField(source='content')
    url = serializers.CharField(source='source_link')
    tags = serializers.ListField(source='industry_tags', child=serializers.CharField(), allow_empty=True)
    # The original frontend used a `source` object; we synthesize a minimal one from source_link
    source = serializers.SerializerMethodField()
    # Frontend expects categories and vendors fields; provide empty defaults for now
    categories = serializers.SerializerMethodField()
    vendors = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        # Expose a curated set of fields mapping to the frontend shape
        fields = (
            'id',
            'title',
            'url',
            'source',
            'summary',
            'tags',
            'categories',
            'vendors',
            'publishedAt',
            'status',
            'relevance_score',
            'created_at',
            'author',
        )

    def get_source(self, obj):
        """
        Return a small `source` dict for the frontend. Prefer stored `source_name` and
        `source_favicon` when present (added as DB columns). Fall back to deriving a
        human-friendly name and a favicon guess from the `source_url` (preferred) or
        `source_link` URL.
        """
        # Prefer the new `source_url` field if present (automation will write here).
        url = getattr(obj, 'source_url', None) or obj.source_link or ''
        # Prefer explicit stored values if they exist
        name = getattr(obj, 'source_name', None) or None
        favicon = getattr(obj, 'source_favicon', None) or None

        if not name and url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                host = (parsed.netloc or '').split(':')[0].lower()
                host_clean = host.replace('www.', '')

                # Small friendly map for common domains -> display names
                host_map = {
                    'openai.com': 'OpenAI',
                    'deepmind.com': 'DeepMind',
                    'anthropic.com': 'Anthropic',
                    'mistral.ai': 'Mistral',
                    'xai.com': 'xAI',
                    'cohere.com': 'Cohere',
                    'stability.ai': 'Stability AI',
                    'techcrunch.com': 'TechCrunch',
                    'venturebeat.com': 'VentureBeat',
                    'europa.eu': 'EU Official Journal',
                    'aisafety.org': 'AI Safety Institute',
                    'ai.meta.com': 'Meta AI Blog',
                    'meta.com': 'Meta',
                }

                name = host_map.get(host_clean)
                if not name and host_clean:
                    # fallback: use the first component of the hostname and capitalize it
                    name = host_clean.split('.')[0].replace('-', ' ').title()

                # default favicon guess (may not exist for all sites)
                if not favicon:
                    favicon = f"https://{host_clean}/favicon.ico" if host_clean else None
            except Exception:
                # keep name and favicon as None on any parse failure
                name = name
                favicon = favicon

        return {
            'name': name,
            'url': url,
            'favicon': favicon,
        }

    def get_categories(self, obj):
        # No categories on the model yet — return empty list for compatibility
        return []

    def get_vendors(self, obj):
        # No vendors on the model yet — return empty list for compatibility
        return []


class ToolSerializer(serializers.ModelSerializer):
    # Use model PK `id` as API id. Map priceFrom -> price_from for frontend compatibility.
    priceFrom = serializers.DecimalField(source='price_from', max_digits=10, decimal_places=2, coerce_to_string=False, required=False, allow_null=True)

    class Meta:
        model = Tool
        # Expose model `id` (primary key) and other fields matching tools.json
        fields = ('id', 'name', 'description', 'url', 'logo', 'category', 'subcategories', 'pricing', 'priceFrom', 'rating', 'tags')
