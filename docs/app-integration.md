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
- `HERMAN_DB_ALLOWED_REVISIONS=20260504_0006,20260504_0007,20260504_0008,20260504_0009,20260505_0010,20260505_0011,20260505_0012`

## Initial Compatibility Target

| App | Compatible Revisions |
|---|---|
| `Herman-Admin` | `20260504_0006`, `20260504_0007`, `20260504_0008`, `20260504_0009`, `20260505_0010`, `20260505_0011`, `20260505_0012` |
| `herman-prompt` | `20260504_0006`, `20260504_0007`, `20260504_0008`, `20260504_0009`, `20260505_0010`, `20260505_0011`, `20260505_0012` |
| `herman_portal` | `20260504_0006`, `20260504_0007`, `20260504_0008`, `20260504_0009`, `20260505_0010`, `20260505_0011`, `20260505_0012` |
| `prompt_transformer` | `20260504_0006`, `20260504_0007`, `20260504_0008`, `20260504_0009`, `20260505_0010`, `20260505_0011`, `20260505_0012` |
