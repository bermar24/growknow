from django.db import models
from django.contrib.auth.models import User

# Define the status choices for the article
class ArticleStatus(models.TextChoices):
    DRAFT = 'DR', 'Draft'
    PENDING_REVIEW = 'PR', 'Pending Review'
    PUBLISHED = 'PB', 'Published'
    ERROR = 'ER', 'Error'

# The core News Article model
class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    # Keep the model attribute named `source_link` for compatibility inside the
    # project, but map it to the database column named `url` (this matches the
    # existing Supabase table). Using `db_column='url'` prevents Django from
    # creating a separate `source_link` column and makes ORM reads/writes use
    # the `url` column in the DB.
    source_link = models.URLField(max_length=500, db_column='url')

    # New column: store the original source URL explicitly as `source_url`.
    # We keep `source_link` for backwards compatibility with older migrations/code,
    # but automation injecting articles should write to `source_url` per the
    # user's preference. This field is nullable so adding it won't require a
    # data migration for existing rows.
    source_url = models.URLField(max_length=500, null=True, blank=True)

    # Optional stored source metadata (new)
    source_name = models.CharField(max_length=255, null=True, blank=True)
    source_favicon = models.CharField(max_length=500, null=True, blank=True)

    # State tracking
    status = models.CharField(
        max_length=2,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
    )

    # Audit and metadata
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # AUTHOR: Changed to a simple text field stored in the existing `author`
    # column in the database. This avoids FK/author_id mismatches and matches
    # the Supabase table where `author` is stored as a (nullable) value.
    author = models.CharField(max_length=255, null=True, blank=True, db_column='author')

    # Fields related to your AI processing (to be populated by n8n/Python workers)
    relevance_score = models.FloatField(default=0.0)
    industry_tags = models.JSONField(default=list)
    # Store categories and vendors as JSON arrays to match `articles.json` structure.
    # These are optional and default to empty lists so adding them is non-destructive.
    categories = models.JSONField(default=list, blank=True)
    vendors = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title

# Model for logging actions (Audit Log)
class AuditLog(models.Model):
    action = models.CharField(max_length=100) # e.g., 'PUBLISH', 'SAVE_DRAFT', 'LOGIN_FAIL'
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(NewsArticle, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"


# Tool model to store AI tools (mapped from frontend tools.json)
class Tool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=1000, blank=True)
    logo = models.CharField(max_length=1000, blank=True)
    category = models.CharField(max_length=255, blank=True)
    subcategories = models.JSONField(default=list, blank=True)
    pricing = models.CharField(max_length=100, blank=True)
    price_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
