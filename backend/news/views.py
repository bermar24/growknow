from typing import Callable

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from django.db import connection

from .models import NewsArticle, Tool
from .serializers import NewsArticleSerializer, ToolSerializer
from .services import ReadServiceFactory


class ReadResponseFacade:
    def __init__(self, read_service):
        self.read_service = read_service

    def list_response(self):
        # SOLID (SRP): keep HTTP response formatting out of endpoint classes.
        # Pattern (Facade): provide one small API for list/detail response building.
        # Benefit: endpoints reuse one implementation instead of duplicating branches.
        return Response(self.read_service.list_items())

    def detail_response(self, pk: str):
        item = self.read_service.get_item(pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(item)


class ReadServiceMixin:
    service_factory: Callable[[], object] | None = None

    @property
    def read_service(self):
        if not hasattr(self, "_read_service"):
            factory = type(self).service_factory
            if factory is None:
                raise NotImplementedError("service_factory must be defined")
            # SOLID (DIP): endpoint code depends on the service abstraction, not concrete providers.
            # Pattern (Factory Method): create dependencies through a factory callback.
            # Benefit: swapping data sources is a local change in factory wiring.
            # Access the factory through the class to avoid binding plain function objects as instance methods.
            self._read_service = factory()
        return self._read_service

    @property
    def response_facade(self):
        if not hasattr(self, "_response_facade"):
            self._response_facade = ReadResponseFacade(self.read_service)
        return self._response_facade


class NewsArticleViewSet(ReadServiceMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for news articles. Change to ModelViewSet for full CRUD.
    """
    queryset = NewsArticle.objects.all().order_by('-created_at')
    serializer_class = NewsArticleSerializer
    service_factory = ReadServiceFactory.create_news_article_service

    # SOLID (OCP): behavior extensions now happen via service_factory/facade composition.
    # Pattern (Facade + Factory Method): endpoint delegates response and dependency creation.
    # Benefit: avoids duplicated retrieval/not-found logic in each endpoint class.
    def list(self, request, *args, **kwargs):
        return self.response_facade.list_response()

    def retrieve(self, request, pk=None, *args, **kwargs):
        return self.response_facade.detail_response(str(pk))


class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    """DRF viewset for tools backed by the Tool model."""
    queryset = Tool.objects.all().order_by('name')
    serializer_class = ToolSerializer


class ToolsListView(ReadServiceMixin, APIView):
    """Return list of tools from DB if available, otherwise fall back to static JSON."""
    service_factory = ReadServiceFactory.create_tools_service

    def get(self, request):
        return self.response_facade.list_response()


class ToolsDetailView(ReadServiceMixin, APIView):
    service_factory = ReadServiceFactory.create_tools_service

    def get(self, request, pk=None):
        return self.response_facade.detail_response(str(pk))


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
