# Schema Governance

## Core Rules

- `herman-db` is the only structural schema authority for the shared Herman Postgres database.
- Shared schema changes must be expressed as reviewed migrations in this repo.
- Applications must not run production/shared-database structural DDL at startup.
- Applications may perform startup schema-version compatibility checks only.
- Application-local test helpers may create ephemeral schemas only in isolated test contexts.

## Version Contract

- Canonical version table: `alembic_version`
- Baseline canonical revision: `20260504_0006`
- Apps must declare compatible canonical revisions.
- Cleanup migrations after baseline are additive until all apps have switched to the canonical contract.

## Table Classes

- `core`: foundational cross-app tables
- `shared-owned`: one write owner, multiple readers
- `derived`: recomputable projections or analytics
- `app-local`: single-app tables that still live in the shared database
