"""
Smoke test script: create a NewsArticle and request the DRF endpoints using APIClient
Run with: python3 scripts/smoke_news_api.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.news.models import NewsArticle
from rest_framework.test import APIClient

# Create a test article
article = NewsArticle.objects.create(
    title='Smoke test article',
    content='Smoke test content',
    source_link='https://example.com',
)

client = APIClient()

list_res = client.get('/api/news/articles/')
print('LIST status:', list_res.status_code)
print('LIST body:', list_res.json())

detail_res = client.get(f'/api/news/articles/{article.id}/')
print('DETAIL status:', detail_res.status_code)
print('DETAIL body:', detail_res.json())

