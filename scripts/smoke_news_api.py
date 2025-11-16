"""
Smoke test script: create a NewsArticle and request the DRF endpoints using APIClient
Run with: python3 scripts/smoke_news_api.py
"""
import os
import django
import sys, os
# add repo root so `backend` package is importable when running the script directly
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.news.models import NewsArticle
from rest_framework.test import APIClient

# Create a test article
article = NewsArticle.objects.create(
    title='Smoke test article',
    content='Smoke test content',
    source_link='https://example.com',
    source_url='https://example.com',
)

client = APIClient()

list_res = client.get('/api/news/articles/')
print('LIST status:', list_res.status_code)
print('LIST body:', list_res.json())

detail_res = client.get(f'/api/news/articles/{article.id}/')
print('DETAIL status:', detail_res.status_code)
print('DETAIL body:', detail_res.json())
