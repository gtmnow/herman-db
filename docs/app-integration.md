# App Integration Contract

## Runtime Behavior

Applications integrating with `herman-db` should:

- query `alembic_version`
- require one of their declared compatible revisions
- fail fast on incompatible schema versions
- avoid structural DDL in shared Postgres environments

## Suggested Environment Variables

- `HERMAN_DB_CANONICAL_MODE=true`
- `HERMAN_DB_VERSION_TABLE=alembic_version`
- `HERMAN_DB_ALLOWED_REVISIONS=20260504_0006,20260504_0007,20260504_0008`

## Initial Compatibility Target

| App | Compatible Revisions |
|---|---|
| `Herman-Admin` | `20260504_0006`, `20260504_0007`, `20260504_0008` |
| `herman-prompt` | `20260504_0006`, `20260504_0007` |
| `herman_portal` | `20260504_0006`, `20260504_0007` |
| `prompt_transformer` | `20260504_0006`, `20260504_0007` |
