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
        return {
            'name': None,
            'url': obj.source_link,
            'favicon': None,
        }

    def get_categories(self, obj):
        # No categories on the model yet — return empty list for compatibility
        return []

    def get_vendors(self, obj):
        # No vendors on the model yet — return empty list for compatibility
        return []


class ToolSerializer(serializers.ModelSerializer):
    # map DB fields to frontend-friendly shape
    id = serializers.CharField(source='external_id', allow_null=True)
    name = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    logo = serializers.CharField()
    category = serializers.CharField()
    subcategories = serializers.ListField(child=serializers.CharField())
    pricing = serializers.CharField()
    priceFrom = serializers.DecimalField(source='price_from', max_digits=10, decimal_places=2, coerce_to_string=False)
    rating = serializers.FloatField()
    tags = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Tool
        fields = ('id','name','description','url','logo','category','subcategories','pricing','priceFrom','rating','tags')
