"""Baseline canonical schema stream at the current live shared DB revision.

Revision ID: 20260504_0006
Revises:
Create Date: 2026-05-04

This baseline intentionally matches the current live shared database revision
value so existing environments can adopt herman-db without an immediate stamp
operation. The migration is a no-op for already-provisioned shared databases.
"""

from __future__ import annotations

revision = "20260504_0006"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
