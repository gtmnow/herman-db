"""Cleanup stub: align password_reset_tokens with canonical portal contract."""

from __future__ import annotations

revision = "20260504_0007"
down_revision = "20260504_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # TODO: replace integer user_id linkage with canonical user_id_hash contract,
    # preserving active reset token semantics and backward-compatible rollout.
    pass


def downgrade() -> None:
    pass
