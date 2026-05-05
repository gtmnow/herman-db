"""Normalize auth user tenant pointers to primary memberships.

This migration tightens the authority boundary between:

- user_tenant_membership: authoritative membership state
- auth_users.tenant_id: derived primary-tenant pointer for compatibility
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260505_0012"
down_revision = "20260505_0011"
branch_labels = None
depends_on = None


PRIMARY_MEMBERSHIP_INDEX = "ux_user_tenant_membership_primary_active"


def upgrade() -> None:
    bind = op.get_bind()

    # Normalize the compatibility tenant pointer from the authoritative primary membership.
    bind.execute(
        sa.text(
            """
            UPDATE auth_users AS a
            SET
              tenant_id = m.tenant_id,
              updated_at = CURRENT_TIMESTAMP
            FROM user_tenant_membership AS m
            WHERE m.user_id_hash = a.user_id_hash
              AND m.is_primary = true
              AND m.status != 'deleted'
              AND coalesce(a.tenant_id, '') <> coalesce(m.tenant_id, '')
            """
        )
    )

    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {PRIMARY_MEMBERSHIP_INDEX}
                ON user_tenant_membership (user_id_hash)
                WHERE is_primary = true AND status != 'deleted'
                """
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text(f"DROP INDEX IF EXISTS {PRIMARY_MEMBERSHIP_INDEX}"))
