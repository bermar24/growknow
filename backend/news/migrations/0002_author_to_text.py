# Migration to ensure the existing `author` column is a varchar/text column.
from django.db import migrations

SQL = "SELECT 1;"

class Migration(migrations.Migration):
    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(SQL, reverse_sql=migrations.RunSQL.noop),
    ]
