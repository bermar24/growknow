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

