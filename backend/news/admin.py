from django.contrib import admin
from .models import NewsArticle, AuditLog, Tool


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'published_at', 'author')
    list_filter = ('status', 'author')
    search_fields = ('title', 'content', 'source_link')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'timestamp', 'actor', 'article')
    search_fields = ('action',)
    list_filter = ('action',)


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name', 'url', 'category', 'pricing', 'price_from')
    search_fields = ('name', 'url', 'category')
    readonly_fields = ('created_at',)
