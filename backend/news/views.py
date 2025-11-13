from rest_framework import viewsets
from .models import NewsArticle
from .serializers import NewsArticleSerializer

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for news articles. Change to ModelViewSet for full CRUD.
    """
    queryset = NewsArticle.objects.all().order_by('-created_at')
    serializer_class = NewsArticleSerializer

