from django.contrib import admin
from .models import NewsArticle, AuditLog, Tool


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    # Show the mapped URL column under a friendly getter column and include
    # `source_url` in search fields so admin users can look up articles by either
    # the displayed `url` (stored in `source_link`/db `url`) or the original
    # `source_url` provided by automation.
    list_display = ('id', 'title', 'get_url', 'status', 'published_at', 'author')
    list_filter = ('status', 'author')
    search_fields = ('title', 'content', 'source_link', 'source_url')

    def get_url(self, obj):
        # Display the `source_url` if available, otherwise show the stored URL
        return obj.source_url or obj.source_link
    get_url.short_description = 'URL'
    get_url.admin_order_field = 'source_link'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'timestamp', 'actor', 'article')
    search_fields = ('action',)
    list_filter = ('action',)


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_url', 'category', 'pricing', 'price_from')
    search_fields = ('name', 'url', 'category')
    readonly_fields = ('created_at',)

    def get_url(self, obj):
        return obj.url
    get_url.short_description = 'URL'
    get_url.admin_order_field = 'url'
