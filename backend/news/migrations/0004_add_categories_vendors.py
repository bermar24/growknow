# Generated migration to add categories and vendors JSON fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_add_source_url"),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='categories',
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.AddField(
            model_name='newsarticle',
            name='vendors',
            field=models.JSONField(default=list, blank=True),
        ),
    ]

