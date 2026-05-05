"""Tighten admin authority and deprecate admin_profiles as an identity source.

This migration aligns the live shared schema with the new authority model:

- `auth_users` becomes the canonical source for admin identity fields
- `admin_users` remains the authoritative admin-entitlement table
- `admin_profiles` stays in place temporarily as a compatibility fallback only

The migration backfills canonical auth identity from `admin_profiles`, repairs
orphaned `admin_users` by creating placeholder auth rows, synchronizes the
legacy `auth_users.is_admin` mirror from active admin assignments, and adds a
foreign key from `admin_users.user_id_hash` to `auth_users.user_id_hash`.
"""

from __future__ import annotations

from datetime import datetime
import hashlib

from alembic import op
import sqlalchemy as sa

revision = "20260504_0008"
down_revision = "20260504_0007"
branch_labels = None
depends_on = None

ADMIN_USERS_AUTH_FK = "fk_admin_users_user_id_hash_auth_users"


def _foreign_key_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {foreign_key["name"] for foreign_key in inspector.get_foreign_keys(table_name) if foreign_key.get("name")}


def _orphan_admin_rows(bind: sa.Connection) -> list[dict[str, object]]:
    rows = bind.execute(
        sa.text(
            """
            SELECT
              au.id,
              au.user_id_hash,
              au.role,
              au.is_active,
              ap.display_name AS profile_display_name,
              ap.email AS profile_email
            FROM admin_users AS au
            LEFT JOIN auth_users AS auth
              ON auth.user_id_hash = au.user_id_hash
            LEFT JOIN admin_profiles AS ap
              ON ap.admin_user_id = au.id
            WHERE auth.user_id_hash IS NULL
            ORDER BY au.created_at, au.id
            """
        )
    ).mappings()
    return [dict(row) for row in rows]


def _matching_auth_user_id_hash_by_email(bind: sa.Connection, email: str | None) -> str | None:
    normalized_email = str(email).strip().lower() if email else None
    if not normalized_email:
        return None

    return bind.execute(
        sa.text(
            """
            SELECT user_id_hash
            FROM auth_users
            WHERE lower(email) = :email
            ORDER BY updated_at DESC, created_at DESC, id DESC
            LIMIT 1
            """
        ),
        {"email": normalized_email},
    ).scalar_one_or_none()


def _existing_admin_id_for_user_id_hash(bind: sa.Connection, *, user_id_hash: str, excluding_admin_id: str) -> str | None:
    return bind.execute(
        sa.text(
            """
            SELECT id
            FROM admin_users
            WHERE user_id_hash = :user_id_hash
              AND id != :excluding_admin_id
            ORDER BY created_at, id
            LIMIT 1
            """
        ),
        {"user_id_hash": user_id_hash, "excluding_admin_id": excluding_admin_id},
    ).scalar_one_or_none()


def _placeholder_email(user_id_hash: str) -> str:
    digest = hashlib.sha1(user_id_hash.encode("utf-8")).hexdigest()[:16]
    return f"legacy-admin-{digest}@herman.invalid"


def _insert_placeholder_auth_user(
    bind: sa.Connection,
    *,
    user_id_hash: str,
    display_name: str | None,
    email: str | None,
    is_active: bool,
    is_admin: bool,
    now: datetime,
) -> None:
    bind.execute(
        sa.text(
            """
            INSERT INTO auth_users (
              email,
              user_id_hash,
              display_name,
              tenant_id,
              is_active,
              is_admin,
              created_at,
              updated_at,
              last_login_at
            ) VALUES (
              :email,
              :user_id_hash,
              :display_name,
              :tenant_id,
              :is_active,
              :is_admin,
              :created_at,
              :updated_at,
              NULL
            )
            """
        ),
        {
            "email": str(email).strip() if email and str(email).strip() else _placeholder_email(user_id_hash),
            "user_id_hash": user_id_hash,
            "display_name": display_name.strip() if display_name else f"Legacy Admin {user_id_hash[:12]}",
            "tenant_id": "tenant_demo",
            "is_active": is_active,
            "is_admin": is_admin,
            "created_at": now,
            "updated_at": now,
        },
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = _foreign_key_names(inspector, "admin_users")
    now = datetime.utcnow()

    # Backfill canonical auth identity from admin_profiles where auth_users has
    # missing values. This preserves user-facing admin names/emails before the
    # table is deprecated as a primary source.
    bind.execute(
        sa.text(
            """
            UPDATE auth_users AS auth
            SET
              email = CASE
                WHEN (auth.email IS NULL OR btrim(auth.email) = '')
                 AND ap.email IS NOT NULL
                 AND btrim(ap.email) <> ''
                THEN ap.email
                ELSE auth.email
              END,
              display_name = CASE
                WHEN (auth.display_name IS NULL OR btrim(auth.display_name) = '')
                 AND ap.display_name IS NOT NULL
                 AND btrim(ap.display_name) <> ''
                THEN ap.display_name
                ELSE auth.display_name
              END,
              updated_at = :updated_at
            FROM admin_users AS au
            JOIN admin_profiles AS ap
              ON ap.admin_user_id = au.id
            WHERE auth.user_id_hash = au.user_id_hash
              AND (
                ((auth.email IS NULL OR btrim(auth.email) = '') AND ap.email IS NOT NULL AND btrim(ap.email) <> '')
                OR
                ((auth.display_name IS NULL OR btrim(auth.display_name) = '') AND ap.display_name IS NOT NULL AND btrim(ap.display_name) <> '')
              )
            """
        ),
        {"updated_at": now},
    )

    # Repair orphan admin entitlements by creating placeholder auth rows.
    # This preserves existing audit/session/invitation references while letting
    # us enforce a real FK from admin_users -> auth_users.
    for orphan in _orphan_admin_rows(bind):
        user_id_hash = str(orphan["user_id_hash"])
        profile_email = orphan.get("profile_email")
        profile_display_name = orphan.get("profile_display_name")

        matching_auth_user_id_hash = _matching_auth_user_id_hash_by_email(bind, str(profile_email) if profile_email else None)
        if matching_auth_user_id_hash is not None:
            existing_admin_id = _existing_admin_id_for_user_id_hash(
                bind,
                user_id_hash=matching_auth_user_id_hash,
                excluding_admin_id=str(orphan["id"]),
            )
            if existing_admin_id is not None:
                bind.execute(
                    sa.text(
                        """
                        UPDATE admin_users
                        SET
                          is_active = false,
                          updated_at = :updated_at
                        WHERE id = :admin_id
                        """
                    ),
                    {
                        "updated_at": now,
                        "admin_id": orphan["id"],
                    },
                )
                _insert_placeholder_auth_user(
                    bind,
                    user_id_hash=user_id_hash,
                    display_name=str(profile_display_name) if profile_display_name else None,
                    email=None,
                    is_active=False,
                    is_admin=False,
                    now=now,
                )
                continue

            bind.execute(
                sa.text(
                    """
                    UPDATE admin_users
                    SET user_id_hash = :matching_user_id_hash
                    WHERE id = :admin_id
                    """
                ),
                {
                    "matching_user_id_hash": matching_auth_user_id_hash,
                    "admin_id": orphan["id"],
                },
            )
            continue

        _insert_placeholder_auth_user(
            bind,
            user_id_hash=user_id_hash,
            display_name=str(profile_display_name) if profile_display_name else None,
            email=str(profile_email) if profile_email else None,
            is_active=bool(orphan["is_active"]),
            is_admin=bool(orphan["is_active"]),
            now=now,
        )

    # Keep the legacy auth_users.is_admin mirror aligned with authoritative
    # active admin assignments.
    bind.execute(
        sa.text(
            """
            UPDATE auth_users AS auth
            SET
              is_admin = EXISTS (
                SELECT 1
                FROM admin_users AS au
                WHERE au.user_id_hash = auth.user_id_hash
                  AND au.is_active = true
              ),
              updated_at = :updated_at
            WHERE EXISTS (
                SELECT 1
                FROM admin_users AS au
                WHERE au.user_id_hash = auth.user_id_hash
            )
            """
        ),
        {"updated_at": now},
    )

    inspector = sa.inspect(bind)
    foreign_keys = _foreign_key_names(inspector, "admin_users")
    if ADMIN_USERS_AUTH_FK not in foreign_keys:
        op.create_foreign_key(
            ADMIN_USERS_AUTH_FK,
            "admin_users",
            "auth_users",
            ["user_id_hash"],
            ["user_id_hash"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = _foreign_key_names(inspector, "admin_users")

    if ADMIN_USERS_AUTH_FK in foreign_keys:
        op.drop_constraint(ADMIN_USERS_AUTH_FK, "admin_users", type_="foreignkey")
