# Generated migration to change author from FK/integer to text field
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='author',
            field=models.CharField(max_length=255, null=True, blank=True, db_column='author'),
        ),
    ]

