# Migration: remove external_id from Tool model
from django.db import migrations


def remove_external_id(apps, schema_editor):
    # Drop the column if it exists (best-effort). Different DB backends
    # have different behaviors; use Raw SQL for safety in Postgres.
    try:
        schema_editor.execute('ALTER TABLE public.news_tool DROP COLUMN IF EXISTS external_id;')
    except Exception:
        # If raw SQL execution is not supported on some backends in this environment,
        # ignore and let Django handle schema changes via other means.
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0004_add_categories_vendors"),
    ]

    operations = [
        migrations.RunPython(remove_external_id, migrations.RunPython.noop),
    ]

