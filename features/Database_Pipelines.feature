Feature: Manage Supabase database

  As an administrator
  I want to apply schema migrations, manage backups, and configure access on the Supabase project
  So that the production database remains consistent, secure and recoverable.

  Background:
    Given an administrator exists and is authenticated

  Scenario: Apply schema migrations successfully
    When the administrator applies schema migrations
    Then the database schema is up to date

  Scenario: Create and restore a database backup
    When the administrator creates a database backup
    Then a backup file is stored

    When the administrator restores the database from the latest backup
    Then the restore operation completes successfully

  Scenario: Configure database access for a team member
    Given a user "db_maintainer" exists
    When the administrator grants the user database-admin access
    Then the user "db_maintainer" has elevated database permissions

  Scenario: Run, monitor and verify data pipeline
    When the administrator starts the data pipeline run named "daily_ingest"
    Then the pipeline run completes with status "SUCCESS"
    And pipeline run logs contain the text "processed" and "completed"

  Scenario: Handle migration failure gracefully
    Given a migration error is simulated
    When the administrator applies schema migrations
    Then the system reports a migration failure
    And an alert is recorded for administrator review

  Scenario: Backup failure is reported and retried
    Given the backup process is simulated to fail
    When the administrator creates a database backup
    Then the system records the backup failure and schedules a retry
