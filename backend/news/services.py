from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from django.db import DatabaseError, OperationalError

from .models import NewsArticle, Tool
from .serializers import NewsArticleSerializer, ToolSerializer


class ReadProvider(Protocol):
    def list_items(self) -> list[dict[str, Any]]:
        ...

    def get_item(self, pk: str) -> dict[str, Any] | None:
        ...


class ORMReadProvider:
    def __init__(self, model, serializer_class, order_by: str):
        self.model = model
        self.serializer_class = serializer_class
        self.order_by = order_by

    def list_items(self) -> list[dict[str, Any]]:
        queryset = self.model.objects.all().order_by(self.order_by)
        if not queryset.exists():
            return []
        return self.serializer_class(queryset, many=True).data

    def get_item(self, pk: str) -> dict[str, Any] | None:
        instance = self.model.objects.filter(id=pk).first()
        if not instance:
            return None
        return self.serializer_class(instance).data


class StaticJsonReadProvider:
    def __init__(self, filename: str):
        static_dir = Path(__file__).resolve().parent / "static" / "news_data"
        self.file_path = static_dir / filename

    def _load_data(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def list_items(self) -> list[dict[str, Any]]:
        return self._load_data()

    def get_item(self, pk: str) -> dict[str, Any] | None:
        for item in self._load_data():
            if str(item.get("id")) == str(pk):
                return item
        return None


class FallbackReadService:
    def __init__(self, primary: ReadProvider, fallback: ReadProvider):
        self.primary = primary
        self.fallback = fallback

    def list_items(self) -> list[dict[str, Any]]:
        # SOLID (OCP/DIP): add new data sources without changing API views by composing providers.
        # Pattern (Strategy-style composition): switch source behavior at runtime based on data availability/errors.
        # Benefit: fallback rules live in one place instead of being duplicated across endpoints.
        try:
            primary_items = self.primary.list_items()
            if primary_items:
                return primary_items
        except (DatabaseError, OperationalError):
            pass
        return self.fallback.list_items()

    def get_item(self, pk: str) -> dict[str, Any] | None:
        # SOLID (SRP): isolate fallback retrieval policy from transport/controller code.
        # Pattern (Strategy-style composition): retrieval delegates to interchangeable providers.
        # Benefit: controllers stay small and easier to test.
        try:
            item = self.primary.get_item(pk)
            if item is not None:
                return item
        except (DatabaseError, OperationalError):
            pass
        return self.fallback.get_item(pk)


class ReadServiceFactory:
    @staticmethod
    def create_news_article_service() -> FallbackReadService:
        # SOLID (DIP): callers receive a service abstraction, not concrete provider wiring.
        # Pattern (Factory Method): centralizes object creation for a consistent dependency graph.
        # Benefit: changing source implementations is a one-file change.
        return FallbackReadService(
            primary=ORMReadProvider(NewsArticle, NewsArticleSerializer, order_by="-created_at"),
            fallback=StaticJsonReadProvider("articles.json"),
        )

    @staticmethod
    def create_tools_service() -> FallbackReadService:
        # SOLID (DIP): same abstraction for tools endpoint keeps view code closed to source changes.
        # Pattern (Factory Method): creates a ready-to-use service with DB + static providers.
        # Benefit: removes repeated setup code from multiple views.
        return FallbackReadService(
            primary=ORMReadProvider(Tool, ToolSerializer, order_by="name"),
            fallback=StaticJsonReadProvider("tools.json"),
        )

