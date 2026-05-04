"""Cleanup stub: invitation lifecycle, admin integrity, and admin_profiles deprecation."""

from __future__ import annotations

revision = "20260504_0008"
down_revision = "20260504_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # TODO: normalize user_invitations lifecycle, tighten admin_users integrity,
    # and introduce the admin_profiles deprecation path.
    pass


def downgrade() -> None:
    pass
