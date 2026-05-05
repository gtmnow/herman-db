"""Normalize user_invitations current-state semantics while preserving history.

The live shared table currently mixes current-state invitation behavior with
historical records. Multiple rows may exist for the same `(user_id_hash,
tenant_id)` pair, and older rows are not always explicitly terminal. This
migration keeps all existing history but makes the current row explicit.

Changes:
- add `is_current`
- mark the latest row per `(user_id_hash, tenant_id)` as current
- expire stale unconsumed rows
- revoke older non-current active rows so historical rows are explicitly terminal
- enforce one current invitation row per `(user_id_hash, tenant_id)` in PostgreSQL
"""

from __future__ import annotations

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "20260505_0010"
down_revision = "20260504_0009"
branch_labels = None
depends_on = None

CURRENT_INDEX = "ux_user_invitations_current_membership"
CURRENT_HELPER_INDEX = "ix_user_invitations_is_current"


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _column_names(inspector, "user_invitations")
    indexes = _index_names(inspector, "user_invitations")
    now = datetime.now(timezone.utc)

    if "is_current" not in columns:
        op.add_column(
            "user_invitations",
            sa.Column("is_current", sa.Boolean(), nullable=True),
        )
        inspector = sa.inspect(bind)
        columns = _column_names(inspector, "user_invitations")
        indexes = _index_names(inspector, "user_invitations")

    # Make the latest invitation row explicit for each membership pair.
    bind.execute(
        sa.text(
            """
            WITH ranked AS (
              SELECT
                id,
                ROW_NUMBER() OVER (
                  PARTITION BY user_id_hash, tenant_id
                  ORDER BY created_at DESC, id DESC
                ) AS row_rank
              FROM user_invitations
            )
            UPDATE user_invitations AS invitation
            SET
              is_current = CASE WHEN ranked.row_rank = 1 THEN TRUE ELSE FALSE END
            FROM ranked
            WHERE invitation.id = ranked.id
            """
        )
    )

    # Explicitly expire rows that have passed their expiry and were never consumed.
    bind.execute(
        sa.text(
            """
            UPDATE user_invitations
            SET
              status = 'expired',
              updated_at = :updated_at
            WHERE accepted_at IS NULL
              AND revoked_at IS NULL
              AND expires_at < :now
              AND status IN ('pending', 'sent', 'failed')
            """
        ),
        {"now": now, "updated_at": now},
    )

    # Older non-current active-ish rows should become terminal history rows.
    bind.execute(
        sa.text(
            """
            UPDATE user_invitations
            SET
              status = CASE
                WHEN status IN ('pending', 'sent', 'failed') THEN 'revoked'
                ELSE status
              END,
              revoked_at = COALESCE(revoked_at, updated_at, created_at, :now),
              updated_at = :updated_at
            WHERE is_current = FALSE
              AND accepted_at IS NULL
              AND revoked_at IS NULL
              AND status IN ('pending', 'sent', 'failed')
            """
        ),
        {"now": now, "updated_at": now},
    )

    with op.batch_alter_table("user_invitations") as batch_op:
        batch_op.alter_column("is_current", existing_type=sa.Boolean(), nullable=False)

    if CURRENT_HELPER_INDEX not in indexes:
        op.create_index(CURRENT_HELPER_INDEX, "user_invitations", ["is_current"], unique=False)

    if bind.dialect.name == "postgresql" and CURRENT_INDEX not in indexes:
        op.create_index(
            CURRENT_INDEX,
            "user_invitations",
            ["user_id_hash", "tenant_id"],
            unique=True,
            postgresql_where=sa.text("is_current = true"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _column_names(inspector, "user_invitations")
    indexes = _index_names(inspector, "user_invitations")

    if CURRENT_INDEX in indexes:
        op.drop_index(CURRENT_INDEX, table_name="user_invitations")
    if CURRENT_HELPER_INDEX in indexes:
        op.drop_index(CURRENT_HELPER_INDEX, table_name="user_invitations")

    if "is_current" in columns:
        with op.batch_alter_table("user_invitations") as batch_op:
            batch_op.drop_column("is_current")
