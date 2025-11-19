from django.test import Client

# Ensure Django settings are configured and apps are loaded before step modules import models.
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
try:
    django.setup()
    # Ensure the test database has migrations applied so tests that use the test client
    # (which relies on the session/auth tables) won't fail with missing relations.
    from django.core import management
    try:
        management.call_command('migrate', '--noinput', verbosity=0)
    except Exception:
        # If migrations cannot run in this environment, tests may still proceed but some
        # steps that rely on DB-backed sessions may fail. We swallow exceptions here
        # to avoid breaking behave import-time, but they will surface during scenario runs.
        pass
except Exception:
    # If django is already configured or setup fails, allow the test run to continue
    pass


def before_scenario(context, scenario):
    """Prepare a Django test client and clear any scenario-specific context.

    This ensures steps that use `context.client` will work and prevents state leaking
    between scenarios.
    """
    context.client = Client()

    # Clear commonly-used context attributes if present
    attrs = [
        'draft_article', 'draft_pk', 'published_article', 'approved',
        'notification_enabled', 'draft_saved', 'db_error_simulated',
        'indexed', 'email_sent', 'login_attempt_success', 'num_drafts',
        'response', 'user'
    ]
    for a in attrs:
        if hasattr(context, a):
            delattr(context, a)


def after_scenario(context, scenario):
    # Tear down client reference
    if hasattr(context, 'client'):
        delattr(context, 'client')
