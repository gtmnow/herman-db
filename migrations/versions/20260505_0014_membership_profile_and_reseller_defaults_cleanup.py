"""Narrow membership profiles and normalize reseller LLM defaults.

This cleanup completes the last two broad duplication areas identified in the
shared Herman schema audit:

* ``user_membership_profiles`` should store only membership-specific descriptive
  metadata, not copied identity or derived usage analytics.
* ``reseller_tenant_defaults`` should follow the same platform-managed LLM
  normalization rule as ``tenant_llm_config``.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "20260505_0014"
down_revision = "20260505_0013"
branch_labels = None
depends_on = None


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "user_membership_profiles"):
        profile_columns = _column_names(inspector, "user_membership_profiles")
        if {"first_name", "last_name", "email"}.intersection(profile_columns) and _table_exists(inspector, "auth_users"):
            bind.execute(
                text(
                    """
                    UPDATE auth_users AS a
                    SET
                      email = COALESCE(NULLIF(a.email, ''), NULLIF(ump.email, ''), a.email),
                      display_name = CASE
                        WHEN (a.display_name IS NULL OR a.display_name = '')
                             AND (NULLIF(ump.first_name, '') IS NOT NULL OR NULLIF(ump.last_name, '') IS NOT NULL)
                          THEN trim(concat_ws(' ', NULLIF(ump.first_name, ''), NULLIF(ump.last_name, '')))
                        ELSE a.display_name
                      END,
                      updated_at = CURRENT_TIMESTAMP
                    FROM user_membership_profiles AS ump
                    JOIN user_tenant_membership AS utm ON utm.id = ump.tenant_membership_id
                    WHERE a.user_id_hash = utm.user_id_hash
                      AND (
                        ((a.display_name IS NULL OR a.display_name = '')
                          AND (NULLIF(ump.first_name, '') IS NOT NULL OR NULLIF(ump.last_name, '') IS NOT NULL))
                        OR ((a.email IS NULL OR a.email = '') AND NULLIF(ump.email, '') IS NOT NULL)
                      )
                    """
                )
            )

        removable_columns = [
            column_name
            for column_name in [
                "first_name",
                "last_name",
                "email",
                "utilization_level",
                "sessions_count",
                "avg_improvement_pct",
                "last_activity_at",
            ]
            if column_name in profile_columns
        ]
        if removable_columns:
            with op.batch_alter_table("user_membership_profiles") as batch_op:
                for column_name in removable_columns:
                    batch_op.drop_column(column_name)

    if _table_exists(inspector, "reseller_tenant_defaults"):
        defaults_columns = _column_names(inspector, "reseller_tenant_defaults")
        if {
            "default_credential_mode",
            "default_platform_managed_config_id",
            "default_provider_type",
            "default_model_name",
            "default_endpoint_url",
        }.issubset(defaults_columns):
            bind.execute(
                text(
                    """
                    UPDATE reseller_tenant_defaults
                    SET
                      default_provider_type = NULL,
                      default_model_name = NULL,
                      default_endpoint_url = NULL,
                      updated_at = CURRENT_TIMESTAMP
                    WHERE default_credential_mode = 'platform_managed'
                      AND default_platform_managed_config_id IS NOT NULL
                    """
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "user_membership_profiles"):
        profile_columns = _column_names(inspector, "user_membership_profiles")
        with op.batch_alter_table("user_membership_profiles") as batch_op:
            if "first_name" not in profile_columns:
                batch_op.add_column(sa.Column("first_name", sa.String(length=100), nullable=True))
            if "last_name" not in profile_columns:
                batch_op.add_column(sa.Column("last_name", sa.String(length=100), nullable=True))
            if "email" not in profile_columns:
                batch_op.add_column(sa.Column("email", sa.String(length=200), nullable=True))
            if "utilization_level" not in profile_columns:
                batch_op.add_column(sa.Column("utilization_level", sa.String(length=50), nullable=True))
            if "sessions_count" not in profile_columns:
                batch_op.add_column(sa.Column("sessions_count", sa.Integer(), nullable=False, server_default="0"))
            if "avg_improvement_pct" not in profile_columns:
                batch_op.add_column(sa.Column("avg_improvement_pct", sa.Integer(), nullable=True))
            if "last_activity_at" not in profile_columns:
                batch_op.add_column(sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True))

        if _table_exists(inspector, "auth_users"):
            bind.execute(
                text(
                    """
                    UPDATE user_membership_profiles AS ump
                    SET
                      email = COALESCE(ump.email, a.email),
                      first_name = COALESCE(
                        ump.first_name,
                        split_part(NULLIF(a.display_name, ''), ' ', 1)
                      ),
                      last_name = COALESCE(
                        ump.last_name,
                        NULLIF(substring(NULLIF(a.display_name, '') from position(' ' in NULLIF(a.display_name, '')) + 1), '')
                      )
                    FROM user_tenant_membership AS utm
                    JOIN auth_users AS a ON a.user_id_hash = utm.user_id_hash
                    WHERE ump.tenant_membership_id = utm.id
                    """
                )
            )
            bind.execute(
                text(
                    """
                    UPDATE user_membership_profiles AS ump
                    SET last_activity_at = COALESCE(ump.last_activity_at, conv.last_activity_at)
                    FROM user_tenant_membership AS utm
                    LEFT JOIN (
                      SELECT user_id_hash, count(*) AS sessions_count, max(updated_at) AS last_activity_at
                      FROM conversations
                      GROUP BY user_id_hash
                    ) AS conv ON conv.user_id_hash = utm.user_id_hash
                    WHERE ump.tenant_membership_id = utm.id
                    """
                )
            )
            bind.execute(
                text(
                    """
                    UPDATE user_membership_profiles AS ump
                    SET sessions_count = COALESCE(conv.sessions_count, 0),
                        avg_improvement_pct = CASE
                          WHEN fp.structure IS NOT NULL THEN round(fp.structure * 100)::int
                          ELSE ump.avg_improvement_pct
                        END,
                        utilization_level = CASE
                          WHEN fp.detail_level >= 0.7 THEN 'high'
                          WHEN fp.detail_level >= 0.4 THEN 'medium'
                          WHEN fp.detail_level IS NOT NULL THEN 'low'
                          ELSE ump.utilization_level
                        END
                    FROM user_tenant_membership AS utm
                    LEFT JOIN (
                      SELECT user_id_hash, count(*) AS sessions_count
                      FROM conversations
                      GROUP BY user_id_hash
                    ) AS conv ON conv.user_id_hash = utm.user_id_hash
                    LEFT JOIN final_profile AS fp ON fp.user_id_hash = utm.user_id_hash
                    WHERE ump.tenant_membership_id = utm.id
                    """
                )
            )

    if _table_exists(inspector, "reseller_tenant_defaults") and _table_exists(inspector, "platform_managed_llm_configs"):
        bind.execute(
            text(
                """
                UPDATE reseller_tenant_defaults AS d
                SET
                  default_provider_type = c.provider_type,
                  default_model_name = c.model_name,
                  default_endpoint_url = c.endpoint_url,
                  updated_at = CURRENT_TIMESTAMP
                FROM platform_managed_llm_configs AS c
                WHERE d.default_credential_mode = 'platform_managed'
                  AND d.default_platform_managed_config_id = c.id
                  AND d.default_platform_managed_config_id IS NOT NULL
                """
            )
        )
