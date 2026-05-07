from django.test import TestCase, Client
import json

from .models import NewsArticle
from .serializers import NewsArticleSerializer

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


class TestNewsArticleSerializerSummaryFallback(TestCase):
    def test_summary_strips_html_and_entities(self):
        article = NewsArticle.objects.create(
            title='Sample',
            content='<p>Hello <strong>world</strong> &#8230;</p>',
            source_link='https://example.com/article',
        )

        data = NewsArticleSerializer(article).data
        self.assertIn('Hello world', data['summary'])
        self.assertNotIn('<', data['summary'])
        self.assertNotIn('>', data['summary'])

    def test_summary_handles_encoded_html(self):
        article = NewsArticle.objects.create(
            title='Encoded',
            content='&lt;p&gt;Encoded <em>summary</em>&lt;/p&gt;',
            source_link='https://example.com/encoded',
        )

        data = NewsArticleSerializer(article).data
        self.assertEqual(data['summary'], 'Encoded summary')

    def test_input_mapping_for_summary_and_source_is_preserved(self):
        serializer = NewsArticleSerializer(
            data={
                'title': 'Incoming payload',
                'summary': 'Plain summary',
                'url': 'https://example.com/incoming',
                'tags': ['ai'],
                'categories': ['Research'],
                'vendors': ['OpenAI'],
                'source': {
                    'url': 'https://example.com',
                    'name': 'Example',
                    'favicon': 'https://example.com/favicon.ico',
                },
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        validated = serializer.validated_data
        self.assertEqual(validated['content'], 'Plain summary')
        self.assertEqual(validated['source_link'], 'https://example.com/incoming')
        self.assertEqual(validated['source_url'], 'https://example.com')
        self.assertEqual(validated['source_name'], 'Example')
        self.assertEqual(validated['source_favicon'], 'https://example.com/favicon.ico')


