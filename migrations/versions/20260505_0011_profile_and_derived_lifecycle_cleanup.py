"""Implement the real replacement for stub 0009.

This migration resolves two audit findings:

1. profile-layer authority drift:
   - backfill missing foundational `type_detail` rows from surviving
     `final_profile` rows
   - rebuild `final_profile` as a purely derived effective layer from
     `type_detail` plus optional overlays

2. derived analytics orphan retention:
   - mark orphaned `conversation_prompt_scores` rows as retained history by
     setting `conversation_deleted_at`
   - annotate orphaned `prompt_transform_requests` rows in `metadata_json`
"""

from __future__ import annotations

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "20260505_0011"
down_revision = "20260505_0010"
branch_labels = None
depends_on = None


PROFILE_VALUE_FIELDS = (
    "structure",
    "answer_first",
    "tone_directness",
    "detail_level",
    "ambiguity_reduction",
    "exploration_level",
    "context_loading",
)

PROFILE_CONTROL_FIELDS = (
    "prompt_enforcement_level",
    "compliance_check_enabled",
    "pii_check_enabled",
)


def _coalesce_overlay_sql(field_name: str) -> str:
    return (
        f"coalesce(ba.{field_name}, ed.{field_name}, bc.{field_name}, t.{field_name})"
    )


def upgrade() -> None:
    bind = op.get_bind()
    now = datetime.now(timezone.utc)

    # Restore foundational authority for rows that only survived in final_profile.
    bind.execute(
        sa.text(
            """
            INSERT INTO type_detail (
              user_id_hash,
              structure,
              answer_first,
              tone_directness,
              detail_level,
              ambiguity_reduction,
              exploration_level,
              context_loading,
              prompt_enforcement_level,
              compliance_check_enabled,
              pii_check_enabled,
              profile_version,
              updated_at
            )
            SELECT
              f.user_id_hash,
              f.structure,
              f.answer_first,
              f.tone_directness,
              f.detail_level,
              f.ambiguity_reduction,
              f.exploration_level,
              f.context_loading,
              f.prompt_enforcement_level,
              f.compliance_check_enabled,
              f.pii_check_enabled,
              CASE
                WHEN f.profile_version IS NULL OR btrim(f.profile_version) = ''
                THEN 'backfilled_from_final_profile'
                ELSE left(f.profile_version, 50)
              END,
              coalesce(f.updated_at, :updated_at)
            FROM final_profile AS f
            LEFT JOIN type_detail AS t
              ON t.user_id_hash = f.user_id_hash
            WHERE t.user_id_hash IS NULL
            """
        ),
        {"updated_at": now},
    )

    # Rebuild the effective layer deterministically from foundational + overlays.
    bind.execute(
        sa.text(
            f"""
            INSERT INTO final_profile (
              user_id_hash,
              structure,
              answer_first,
              tone_directness,
              detail_level,
              ambiguity_reduction,
              exploration_level,
              context_loading,
              prompt_enforcement_level,
              compliance_check_enabled,
              pii_check_enabled,
              profile_version,
              updated_at
            )
            SELECT
              t.user_id_hash,
              {_coalesce_overlay_sql("structure")} AS structure,
              {_coalesce_overlay_sql("answer_first")} AS answer_first,
              {_coalesce_overlay_sql("tone_directness")} AS tone_directness,
              {_coalesce_overlay_sql("detail_level")} AS detail_level,
              {_coalesce_overlay_sql("ambiguity_reduction")} AS ambiguity_reduction,
              {_coalesce_overlay_sql("exploration_level")} AS exploration_level,
              {_coalesce_overlay_sql("context_loading")} AS context_loading,
              {_coalesce_overlay_sql("prompt_enforcement_level")} AS prompt_enforcement_level,
              {_coalesce_overlay_sql("compliance_check_enabled")} AS compliance_check_enabled,
              {_coalesce_overlay_sql("pii_check_enabled")} AS pii_check_enabled,
              CASE
                WHEN bc.user_id_hash IS NOT NULL
                  OR ed.user_id_hash IS NOT NULL
                  OR ba.user_id_hash IS NOT NULL
                THEN left(coalesce(nullif(t.profile_version, ''), 'type_detail') || '+layers', 50)
                ELSE t.profile_version
              END AS profile_version,
              greatest(
                coalesce(t.updated_at, :updated_at),
                coalesce(bc.updated_at, t.updated_at, :updated_at),
                coalesce(ed.updated_at, t.updated_at, :updated_at),
                coalesce(ba.updated_at, t.updated_at, :updated_at)
              ) AS updated_at
            FROM type_detail AS t
            LEFT JOIN brain_chemistry AS bc
              ON bc.user_id_hash = t.user_id_hash
            LEFT JOIN environment_details AS ed
              ON ed.user_id_hash = t.user_id_hash
            LEFT JOIN behaviorial_adj AS ba
              ON ba.user_id_hash = t.user_id_hash
            ON CONFLICT (user_id_hash) DO UPDATE
            SET
              structure = excluded.structure,
              answer_first = excluded.answer_first,
              tone_directness = excluded.tone_directness,
              detail_level = excluded.detail_level,
              ambiguity_reduction = excluded.ambiguity_reduction,
              exploration_level = excluded.exploration_level,
              context_loading = excluded.context_loading,
              prompt_enforcement_level = excluded.prompt_enforcement_level,
              compliance_check_enabled = excluded.compliance_check_enabled,
              pii_check_enabled = excluded.pii_check_enabled,
              profile_version = excluded.profile_version,
              updated_at = excluded.updated_at
            """
        ),
        {"updated_at": now},
    )

    # Any final_profile rows left without a foundational source are invalid.
    bind.execute(
        sa.text(
            """
            DELETE FROM final_profile AS f
            WHERE NOT EXISTS (
              SELECT 1
              FROM type_detail AS t
              WHERE t.user_id_hash = f.user_id_hash
            )
            """
        )
    )

    # Mark retained analytics rows whose conversations no longer exist.
    bind.execute(
        sa.text(
            """
            UPDATE conversation_prompt_scores AS s
            SET
              conversation_deleted_at = coalesce(
                s.conversation_deleted_at,
                s.conversation_ended_at,
                s.last_scored_at,
                s.updated_at,
                s.created_at
              ),
              updated_at = :updated_at
            WHERE NOT EXISTS (
              SELECT 1
              FROM conversations AS c
              WHERE c.id = s.conversation_id
            )
              AND s.conversation_deleted_at IS NULL
            """
        ),
        {"updated_at": now},
    )

    if bind.dialect.name == "postgresql":
        bind.execute(
            sa.text(
                """
                UPDATE prompt_transform_requests AS r
                SET
                  metadata_json = (
                    coalesce(r.metadata_json::jsonb, '{}'::jsonb)
                    || jsonb_build_object(
                      'retention_status', 'retained_orphan',
                      'conversation_present', false,
                      'retained_at', to_char(:updated_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"')
                    )
                  )::json
                WHERE nullif(btrim(coalesce(r.conversation_id, '')), '') IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1
                    FROM conversations AS c
                    WHERE c.id = r.conversation_id
                  )
                """
            ),
            {"updated_at": now},
        )


def downgrade() -> None:
    # This migration intentionally normalizes and annotates existing data.
    # The prior profile/analytics drift cannot be reconstructed safely.
    pass
