# Migration to change `author` from FK to text (CharField) so it matches the
# Supabase table and the current `NewsArticle` model.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newsarticle",
            name="author",
            field=models.CharField(max_length=255, null=True, blank=True, db_column='author'),
        ),
    ]
