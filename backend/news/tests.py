from django.test import TestCase, Client
from django.urls import reverse
import json

class TestStaticFallbackAPI(TestCase):
    def setUp(self):
        self.client = Client()

    def test_articles_list_static_fallback(self):
        resp = self.client.get('/api/news/articles/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        first = data[0]
        self.assertIn('id', first)
        self.assertIn('title', first)

    def test_article_detail_static_fallback(self):
        resp = self.client.get('/api/news/articles/1/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIsInstance(data, dict)
        self.assertEqual(str(data.get('id')), '1')

class TestToolsAPI(TestCase):
    def setUp(self):
        self.client = Client()

    def test_tools_list_static_fallback(self):
        resp = self.client.get('/api/news/tools/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        first = data[0]
        self.assertIn('id', first)
        self.assertIn('name', first)

    def test_tool_detail_static_fallback(self):
        resp = self.client.get('/api/news/tools/1/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIsInstance(data, dict)
        self.assertEqual(str(data.get('id')), '1')
