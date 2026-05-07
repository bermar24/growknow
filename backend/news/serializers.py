from html import unescape

from django.utils.html import strip_tags
from rest_framework import serializers
from .models import NewsArticle, Tool
from .adapters import SourceMetadataAdapter


def _summary_to_plain_text(value):
    if not isinstance(value, str):
        return value

    cleaned = value
    # Decode entities twice to handle encoded HTML like "&lt;p&gt;...&lt;/p&gt;".
    for _ in range(2):
        cleaned = unescape(cleaned)

    cleaned = strip_tags(cleaned)
    return ' '.join(cleaned.split())


class NewsArticleSerializer(serializers.ModelSerializer):
    # Map model fields to frontend-friendly keys
    publishedAt = serializers.DateTimeField(source='published_at', allow_null=True, required=False)
    summary = serializers.CharField(source='content')
    url = serializers.CharField(source='source_link')
    tags = serializers.ListField(
        source='industry_tags',
        child=serializers.CharField(),
        allow_empty=True,
        required=False,
        default=list,
    )
    # The original frontend used a `source` object; we synthesize a minimal one from source_link
    source = serializers.SerializerMethodField()
    categories = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False, default=list)
    vendors = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False, default=list)

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

    def to_internal_value(self, data):
        mutable = data.copy()
        source_payload = mutable.pop('source', None)
        validated = super().to_internal_value(mutable)

        if isinstance(source_payload, dict):
            src_url = source_payload.get('url')
            src_name = source_payload.get('name')
            src_favicon = source_payload.get('favicon')
            if src_url:
                validated['source_url'] = src_url
            if src_name:
                validated['source_name'] = src_name
            if src_favicon:
                validated['source_favicon'] = src_favicon
        return validated

    def get_source(self, obj):
        # SOLID (SRP): keep serializer focused on field exposure, not URL parsing details.
        # Pattern (Adapter): delegate source-shape conversion to SourceMetadataAdapter.
        # Benefit: source mapping rules are reusable and easier to change in one place.
        return SourceMetadataAdapter.from_article(obj)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['summary'] = _summary_to_plain_text(data.get('summary', ''))
        return data


class ToolSerializer(serializers.ModelSerializer):
    # Use model PK `id` as API id. Map priceFrom -> price_from for frontend compatibility.
    priceFrom = serializers.DecimalField(source='price_from', max_digits=10, decimal_places=2, coerce_to_string=False, required=False, allow_null=True)

    class Meta:
        model = Tool
        # Expose model `id` (primary key) and other fields matching tools.json
        fields = ('id', 'name', 'description', 'url', 'logo', 'category', 'subcategories', 'pricing', 'priceFrom', 'rating', 'tags')
