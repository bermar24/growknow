from django.contrib import admin
from .models import NewsArticle, AuditLog


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'author', 'published_at')
    list_filter = ('status', 'author')
    search_fields = ('title', 'content')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'actor', 'article', 'timestamp')
    search_fields = ('action',)
    list_filter = ('action',)

