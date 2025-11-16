# Generated migration to add source_url field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_tool"),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='source_url',
            field=models.URLField(max_length=500, null=True, blank=True),
        ),
    ]

