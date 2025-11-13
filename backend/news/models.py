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
    source_link = models.URLField(max_length=500)

    # State tracking
    status = models.CharField(
        max_length=2,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
    )

    # Audit and metadata
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')

    # Fields related to your AI processing (to be populated by n8n/Python workers)
    relevance_score = models.FloatField(default=0.0)
    industry_tags = models.JSONField(default=list)

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
    external_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
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
