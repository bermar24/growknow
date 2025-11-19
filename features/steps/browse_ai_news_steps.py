from behave import given, when, then
from backend.news.models import NewsArticle, ArticleStatus
from django.utils import timezone


@given('I am on the AI News page')
def step_impl(context):
    """Set up the canonical news list URL for later requests."""
    # Use the API list endpoint mounted at /api/news/articles/
    context.news_list_url = '/api/news/articles/'


@when('the page loads')
def step_impl(context):
    """Request the news list and store the response on the context."""
    assert hasattr(context, 'client'), "Django test client not found on context"
    context.response = context.client.get(context.news_list_url)
    # Parse JSON if possible and normalise to a list of articles
    try:
        data = context.response.json()
    except Exception:
        data = None

    if isinstance(data, list):
        context.articles = data
    elif isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
        # DRF pagination case
        context.articles = data['results']
    else:
        # Unknown or empty response -> empty list
        context.articles = []


@then('I see a list of recent AI news items with titles and summaries')
def step_impl(context):
    """Assert the list response contains articles with title and summary fields."""
    assert context.response.status_code == 200, f"Unexpected status {context.response.status_code}"
    assert isinstance(context.articles, list), "Articles payload is not a list"
    assert len(context.articles) > 0, "No articles returned by the news list endpoint"

    # Check that at least the first article has the expected keys used by the frontend
    sample = context.articles[0]
    assert 'title' in sample, "Article missing 'title'"
    # The API maps the model `content` to `summary` in the serializer
    assert ('summary' in sample) or ('content' in sample), "Article missing 'summary' or 'content'"


@given('a news item is visible')
def step_impl(context):
    """Ensure a visible article exists and note its id on the context.

    This step will reuse any article returned by a previous list request. If none
    exist, it will create a published NewsArticle in the test database.
    """
    # Prefer an article returned by the list step
    if getattr(context, 'articles', None):
        first = context.articles[0]
        context.visible_article_id = first.get('id')
        return

    # Otherwise create a simple published article in the DB
    article = NewsArticle.objects.create(
        title='Behave Test Article',
        content='Full content for behave test article.',
        source_link='https://example.com/test-article',
        status=ArticleStatus.PUBLISHED,
        published_at=timezone.now(),
        author='behave-test'
    )
    context.visible_article_id = article.pk


@when('I select the news item')
def step_impl(context):
    """Request the article detail endpoint for the visible article id."""
    assert hasattr(context, 'visible_article_id'), 'No visible article id found on context'
    url = f'/api/news/articles/{context.visible_article_id}/'
    context.detail_response = context.client.get(url)
    try:
        context.detail = context.detail_response.json()
    except Exception:
        context.detail = None


@then('I see the full article and related links')
def step_impl(context):
    """Assert the article detail response contains expected fields like summary and url."""
    assert context.detail_response.status_code == 200, f"Unexpected detail status {context.detail_response.status_code}"
    assert isinstance(context.detail, dict), "Article detail payload is not a dict"
    # The serializer exposes the main content as `summary` and the original link as `url`
    assert 'summary' in context.detail or 'content' in context.detail, "Detail missing article body"
    assert 'url' in context.detail or (context.detail.get('source') and context.detail['source'].get('url')), "Detail missing article link/url"

