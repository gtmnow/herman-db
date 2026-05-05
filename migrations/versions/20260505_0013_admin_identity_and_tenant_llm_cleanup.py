"""Retire admin_profiles and normalize platform-managed tenant LLM storage."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260505_0013"
down_revision = "20260505_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    with op.batch_alter_table("tenant_llm_config") as batch_op:
        batch_op.alter_column("provider_type", existing_type=sa.String(length=100), nullable=True)
        batch_op.alter_column("model_name", existing_type=sa.String(length=200), nullable=True)

    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                """
                UPDATE tenant_llm_config
                SET
                  provider_type = NULL,
                  model_name = NULL,
                  endpoint_url = NULL,
                  updated_at = CURRENT_TIMESTAMP
                WHERE credential_mode = 'platform_managed'
                  AND platform_managed_config_id IS NOT NULL
                """
            )
        )

    op.drop_table("admin_profiles")

    with op.batch_alter_table("auth_users") as batch_op:
        batch_op.drop_column("is_admin")


def downgrade() -> None:
    with op.batch_alter_table("auth_users") as batch_op:
        batch_op.add_column(sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.create_table(
        "admin_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("admin_user_id", sa.String(length=36), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"]),
    )
    op.create_index("ix_admin_profiles_admin_user_id", "admin_profiles", ["admin_user_id"], unique=True)

    with op.batch_alter_table("tenant_llm_config") as batch_op:
        batch_op.alter_column("provider_type", existing_type=sa.String(length=100), nullable=False)
        batch_op.alter_column("model_name", existing_type=sa.String(length=200), nullable=False)
