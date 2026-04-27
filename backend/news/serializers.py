from rest_framework import serializers
from .models import NewsArticle, Tool
from .adapters import SourceMetadataAdapter


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
        # SOLID (SRP): keep serializer focused on field exposure, not URL parsing details.
        # Pattern (Adapter): delegate source-shape conversion to SourceMetadataAdapter.
        # Benefit: source mapping rules are reusable and easier to change in one place.
        return SourceMetadataAdapter.from_article(obj)

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
