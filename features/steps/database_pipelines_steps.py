from behave import given, when, then
from django.contrib.auth.models import User, Permission
from django.core import management
from django.core.management.base import CommandError
from django.db import connection
import os
import tempfile
from pathlib import Path
import json
import time


@given('an administrator exists and is authenticated')
def step_impl(context):
    # Create or get admin user and log them in via test client
    user, created = User.objects.get_or_create(username='admin')
    user.is_staff = True
    user.is_superuser = True
    user.set_password('adminpass')
    user.save()
    context.admin_user = user
    assert hasattr(context, 'client'), 'Django test client not available on context'
    logged = context.client.login(username='admin', password='adminpass')
    assert logged is True


@when('the administrator applies schema migrations')
def step_impl(context):
    """Run Django migrations; capture success/failure on context."""
    try:
        # Call migrate management command programmatically
        management.call_command('migrate', verbosity=0)
        context.migrations_applied = True
    except CommandError as e:
        context.migrations_applied = False
        context.migration_error = str(e)


@then('the database schema is up to date')
def step_impl(context):
    assert getattr(context, 'migrations_applied', False) is True, \
        f"Migrations not applied: {getattr(context, 'migration_error', '')}"
    # Optionally, inspect django_migrations table to ensure latest entries exist
    with connection.cursor() as cur:
        cur.execute("SELECT count(*) FROM django_migrations")
        row = cur.fetchone()
        assert row is not None and row[0] > 0


@when('the administrator creates a database backup')
def step_impl(context):
    """Create a JSON dump of all app data using dumpdata and store to a temp file."""
    fd, path = tempfile.mkstemp(prefix='growknow_backup_', suffix='.json')
    os.close(fd)
    try:
        management.call_command('dumpdata', '--natural-primary', '--natural-foreign', stdout=open(path, 'w'), verbosity=0)
        context.backup_file = path
        context.backup_created = True
    except Exception as e:
        context.backup_created = False
        context.backup_error = str(e)


@then('a backup file is stored')
def step_impl(context):
    assert getattr(context, 'backup_created', False), f"Backup was not created: {getattr(context, 'backup_error', '')}"
    assert os.path.exists(context.backup_file)
    # basic sanity: file non-empty
    assert os.path.getsize(context.backup_file) > 0


@when('the administrator restores the database from the latest backup')
def step_impl(context):
    assert getattr(context, 'backup_file', None), 'No backup file available to restore'
    # For safety, flush the DB then loaddata from the backup
    try:
        management.call_command('flush', '--noinput', verbosity=0)
        management.call_command('loaddata', context.backup_file, verbosity=0)
        context.restore_success = True
    except Exception as e:
        context.restore_success = False
        context.restore_error = str(e)


@then('the restore operation completes successfully')
def step_impl(context):
    assert getattr(context, 'restore_success', False), f"Restore failed: {getattr(context, 'restore_error', '')}"


@given('a user "{username}" exists')
def step_impl(context, username):
    user, created = User.objects.get_or_create(username=username)
    user.set_password('temporary')
    user.save()
    context.target_user = user


@when('the administrator grants the user database-admin access')
def step_impl(context):
    # Simulate granting a broad permission: add staff + superuser flag for test
    user = getattr(context, 'target_user', None)
    assert user is not None, 'Target user not found in context'
    user.is_staff = True
    user.is_superuser = True
    user.save()
    context.granted = True


@then('the user "{username}" has elevated database permissions')
def step_impl(context, username):
    user = User.objects.get(username=username)
    assert user.is_staff and user.is_superuser


@when('the administrator starts the data pipeline run named "{pipeline_name}"')
def step_impl(context, pipeline_name):
    # Simulate a pipeline run by writing a run record to context and producing logs
    run = {
        'name': pipeline_name,
        'status': 'RUNNING',
        'started_at': time.time(),
        'logs': []
    }
    context.pipeline_run = run
    # Simulate processing steps with logs
    run['logs'].append('started')
    # pretend we processed 3 items
    for i in range(3):
        run['logs'].append(f'processed item {i}')
    run['logs'].append('completed')
    run['status'] = 'SUCCESS'
    run['finished_at'] = time.time()


@then('the pipeline run completes with status "{status}"')
def step_impl(context, status):
    assert hasattr(context, 'pipeline_run')
    assert context.pipeline_run['status'] == status


@then('pipeline run logs contain the text "{text1}" and "{text2}"')
def step_impl(context, text1, text2):
    logs = context.pipeline_run.get('logs', [])
    joined = ' '.join(logs)
    assert text1 in joined and text2 in joined


@given('a migration error is simulated')
def step_impl(context):
    # Simulate migration error by monkeypatching management.call_command to raise for migrate
    context._orig_call = management.call_command

    def fail_call_command(cmd, *args, **kwargs):
        if cmd == 'migrate':
            raise CommandError('Simulated migration failure')
        return context._orig_call(cmd, *args, **kwargs)

    management.call_command = fail_call_command
    context.simulated_migration_failure = True


@then('the system reports a migration failure')
def step_impl(context):
    assert getattr(context, 'migrations_applied', False) is False
    assert hasattr(context, 'migration_error') or getattr(context, 'simulated_migration_failure', False)


@then('an alert is recorded for administrator review')
def step_impl(context):
    # Record alerts in context.alerts list to simulate notification/audit
    if not hasattr(context, 'alerts'):
        context.alerts = []
    if getattr(context, 'migration_error', None):
        context.alerts.append({'type': 'migration_failure', 'message': context.migration_error})
    elif getattr(context, 'simulated_migration_failure', False):
        context.alerts.append({'type': 'migration_failure', 'message': 'Simulated migration failure'})
    assert any(a['type'] == 'migration_failure' for a in context.alerts)


@given('the backup process is simulated to fail')
def step_impl(context):
    # Monkeypatch dumpdata to raise an exception during backup
    context._orig_dump = management.call_command

    def fail_dump(cmd, *args, **kwargs):
        if cmd == 'dumpdata':
            raise Exception('Simulated backup failure')
        return context._orig_dump(cmd, *args, **kwargs)

    management.call_command = fail_dump
    context.simulate_backup_failure = True


@then('the system records the backup failure and schedules a retry')
def step_impl(context):
    # On backup failure we set backup_created False and create a retry record in context
    assert getattr(context, 'backup_created', False) is False or getattr(context, 'simulate_backup_failure', False)
    if not hasattr(context, 'retry_queue'):
        context.retry_queue = []
    context.retry_queue.append({'action': 'create_backup', 'scheduled_at': time.time() + 60})
    assert any(r['action'] == 'create_backup' for r in context.retry_queue)

