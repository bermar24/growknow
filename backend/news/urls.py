from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsArticleViewSet, ToolsListView, ToolsDetailView

router = DefaultRouter()
router.register(r'articles', NewsArticleViewSet, basename='newsarticle')

urlpatterns = [
    path('', include(router.urls)),
    path('tools/', ToolsListView.as_view(), name='tools-list'),
    path('tools/<str:pk>/', ToolsDetailView.as_view(), name='tools-detail'),
]
