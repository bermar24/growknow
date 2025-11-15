from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import NewsArticle, Tool
from .serializers import NewsArticleSerializer, ToolSerializer
import json
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.views import APIView

# DB imports for robust fallback and health check
from django.db import DatabaseError, OperationalError, connection
from django.http import Http404

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for news articles. Change to ModelViewSet for full CRUD.
    Falls back to static JSON files in backend/news/static/news_data/ when the DB is empty
    or when a database error occurs.
    """
    queryset = NewsArticle.objects.all().order_by('-created_at')
    serializer_class = NewsArticleSerializer

    def _load_static_articles(self):
        static_dir = Path(__file__).resolve().parent / 'static' / 'news_data'
        file_path = static_dir / 'articles.json'
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    return data
                except Exception:
                    return []
        return []

    def list(self, request, *args, **kwargs):
        # Try DB first; fall back to static JSON if DB is empty or inaccessible
        try:
            qs_count = NewsArticle.objects.count()
            if qs_count > 0:
                return super().list(request, *args, **kwargs)
        except (DatabaseError, OperationalError) as e:
            # Database unavailable or error - fall back to static data
            # In production you may want to log this exception
            pass

        # Otherwise fall back to static JSON
        data = self._load_static_articles()
        return Response(data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        # Try DB first; if DB is down or object not found, try static fallback
        try:
            return super().retrieve(request, pk=pk, *args, **kwargs)
        except Http404:
            # Object not in DB; fall through to static fallback
            pass
        except (DatabaseError, OperationalError):
            # DB error - fall back to static
            pass
        except Exception:
            # For safety, try static fallback instead of exposing internal errors
            pass

        # Static fallback
        data = self._load_static_articles()
        for item in data:
            # stored ids are strings in the frontend JSON; compare as str
            if str(item.get('id')) == str(pk):
                return Response(item)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    """DRF viewset for tools backed by the Tool model."""
    queryset = Tool.objects.all().order_by('name')
    serializer_class = ToolSerializer


class ToolsListView(APIView):
    """Return list of tools from DB if available, otherwise fall back to static JSON."""
    def _load_static_tools(self):
        static_dir = Path(__file__).resolve().parent / 'static' / 'news_data'
        file_path = static_dir / 'tools.json'
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    return data
                except Exception:
                    return []
        return []

    def get(self, request):
        # Try DB first
        try:
            if Tool.objects.exists():
                qs = Tool.objects.all().order_by('name')
                serializer = ToolSerializer(qs, many=True)
                return Response(serializer.data)
        except (DatabaseError, OperationalError):
            pass

        # Otherwise fall back to static JSON
        data = self._load_static_tools()
        return Response(data)


class ToolsDetailView(APIView):
    def _load_static_tools(self):
        static_dir = Path(__file__).resolve().parent / 'static' / 'news_data'
        file_path = static_dir / 'tools.json'
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    return data
                except Exception:
                    return []
        return []

    def get(self, request, pk=None):
        # Try DB first
        try:
            # Prefer lookup by primary key `id`. External IDs are deprecated and may not
            # be present in the DB, so avoid relying on them.
            tool = Tool.objects.filter(id=pk).first()
            if tool:
                serializer = ToolSerializer(tool)
                return Response(serializer.data)
        except (DatabaseError, OperationalError):
            pass

        # Static fallback
        data = self._load_static_tools()
        for item in data:
            if str(item.get('id')) == str(pk):
                return Response(item)
        return Response({'detail': 'Not found.'}, status=404)


# Health endpoint to check DB connectivity and basic app liveness
@api_view(['GET'])
def health(request):
    status_obj = {'ok': True, 'db': False}
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
            row = cur.fetchone()
            status_obj['db'] = bool(row and row[0] == 1)
    except Exception as e:
        status_obj['ok'] = False
        status_obj['db_error'] = str(e)
    return Response(status_obj)
