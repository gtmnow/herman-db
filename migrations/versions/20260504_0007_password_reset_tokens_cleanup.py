"""Align password_reset_tokens with the canonical portal contract.

The live shared schema currently stores `password_reset_tokens.user_id` as an
integer foreign-key-like pointer to `auth_users.id`, while herman_portal uses
`user_id_hash` in its ORM and password-reset service logic. This migration
converts the table to the canonical `user_id_hash` shape and preserves existing
tokens by backfilling through `auth_users`.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260504_0007"
down_revision = "20260504_0006"
branch_labels = None
depends_on = None


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _column_names(inspector, "password_reset_tokens")
    indexes = _index_names(inspector, "password_reset_tokens")

    if "user_id_hash" not in columns:
        op.add_column("password_reset_tokens", sa.Column("user_id_hash", sa.String(length=255), nullable=True))
        inspector = sa.inspect(bind)
        columns = _column_names(inspector, "password_reset_tokens")
        indexes = _index_names(inspector, "password_reset_tokens")

    if "user_id" in columns:
        if bind.dialect.name == "postgresql":
            bind.execute(
                sa.text(
                    """
                    UPDATE password_reset_tokens AS p
                    SET user_id_hash = a.user_id_hash
                    FROM auth_users AS a
                    WHERE p.user_id = a.id
                      AND p.user_id_hash IS NULL
                    """
                )
            )
        else:
            bind.execute(
                sa.text(
                    """
                    UPDATE password_reset_tokens
                    SET user_id_hash = (
                        SELECT auth_users.user_id_hash
                        FROM auth_users
                        WHERE auth_users.id = password_reset_tokens.user_id
                    )
                    WHERE user_id_hash IS NULL
                    """
                )
            )

    unresolved = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM password_reset_tokens
            WHERE user_id_hash IS NULL
            """
        )
    ).scalar_one()
    if unresolved:
        raise RuntimeError(
            f"Cannot upgrade password_reset_tokens: {unresolved} rows could not be mapped to auth_users.user_id_hash."
        )

    if "ix_password_reset_tokens_user_id_hash" not in indexes:
        op.create_index(
            "ix_password_reset_tokens_user_id_hash",
            "password_reset_tokens",
            ["user_id_hash"],
            unique=False,
        )

    with op.batch_alter_table("password_reset_tokens") as batch_op:
        batch_op.alter_column("user_id_hash", existing_type=sa.String(length=255), nullable=False)
        if "user_id" in columns:
            batch_op.drop_column("user_id")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = _column_names(inspector, "password_reset_tokens")
    indexes = _index_names(inspector, "password_reset_tokens")

    if "user_id" not in columns:
        op.add_column("password_reset_tokens", sa.Column("user_id", sa.Integer(), nullable=True))
        inspector = sa.inspect(bind)
        columns = _column_names(inspector, "password_reset_tokens")
        indexes = _index_names(inspector, "password_reset_tokens")

    if "user_id_hash" in columns:
        if bind.dialect.name == "postgresql":
            bind.execute(
                sa.text(
                    """
                    UPDATE password_reset_tokens AS p
                    SET user_id = a.id
                    FROM auth_users AS a
                    WHERE p.user_id_hash = a.user_id_hash
                      AND p.user_id IS NULL
                    """
                )
            )
        else:
            bind.execute(
                sa.text(
                    """
                    UPDATE password_reset_tokens
                    SET user_id = (
                        SELECT auth_users.id
                        FROM auth_users
                        WHERE auth_users.user_id_hash = password_reset_tokens.user_id_hash
                    )
                    WHERE user_id IS NULL
                    """
                )
            )

    unresolved = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM password_reset_tokens
            WHERE user_id IS NULL
            """
        )
    ).scalar_one()
    if unresolved:
        raise RuntimeError(
            f"Cannot downgrade password_reset_tokens: {unresolved} rows could not be mapped back to auth_users.id."
        )

    with op.batch_alter_table("password_reset_tokens") as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
        if "user_id_hash" in columns:
            batch_op.drop_column("user_id_hash")

    if "ix_password_reset_tokens_user_id_hash" in indexes:
        op.drop_index("ix_password_reset_tokens_user_id_hash", table_name="password_reset_tokens")
