"""Normalize shared RAG schema columns to the canonical Herman DB contract.

This repair migration exists because early RAG application code briefly defined
`rag_retrieval_events.score` as JSON while the canonical shared schema requires
it to be numeric. If a database was bootstrapped from the application metadata
instead of the shared migration stream, the live table shape can drift away
from the Herman DB contract.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "20260506_0016"
down_revision = "20260505_0015"
branch_labels = None
depends_on = None


NUMERIC_LITERAL_RE = r"^[+-]?([0-9]+(\.[0-9]+)?|\.[0-9]+)([eE][+-]?[0-9]+)?$"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _column_metadata(bind: sa.Connection, table_name: str, column_name: str) -> dict[str, object] | None:
    return bind.execute(
        text(
            """
            SELECT
              data_type,
              udt_name,
              is_nullable,
              character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).mappings().first()


def _alter_varchar_length(bind: sa.Connection, table_name: str, column_name: str, length: int) -> None:
    metadata = _column_metadata(bind, table_name, column_name)
    if metadata is None:
        return
    if metadata["data_type"] == "character varying" and metadata["character_maximum_length"] == length:
        return
    bind.execute(
        text(
            f"""
            ALTER TABLE {table_name}
            ALTER COLUMN {column_name} TYPE VARCHAR({length})
            """
        )
    )


def _drop_not_null(bind: sa.Connection, table_name: str, column_name: str) -> None:
    metadata = _column_metadata(bind, table_name, column_name)
    if metadata is None or metadata["is_nullable"] == "YES":
        return
    bind.execute(
        text(
            f"""
            ALTER TABLE {table_name}
            ALTER COLUMN {column_name} DROP NOT NULL
            """
        )
    )


def _normalize_retrieval_score(bind: sa.Connection) -> None:
    metadata = _column_metadata(bind, "rag_retrieval_events", "score")
    if metadata is None:
        return

    udt_name = str(metadata["udt_name"])
    if udt_name == "float8":
        return

    if udt_name in {"json", "jsonb"}:
        using_expression = f"""
            CASE
              WHEN score IS NULL THEN 0.0
              WHEN jsonb_typeof(score::jsonb) = 'number' THEN (score::jsonb #>> '{{}}')::double precision
              WHEN jsonb_typeof(score::jsonb) = 'string'
                   AND trim(both '"' from score::text) ~ '{NUMERIC_LITERAL_RE}'
                THEN trim(both '"' from score::text)::double precision
              ELSE 0.0
            END
        """
    elif udt_name in {"float4", "numeric", "int2", "int4", "int8"}:
        using_expression = "score::double precision"
    elif udt_name in {"varchar", "text", "bpchar"}:
        using_expression = f"""
            CASE
              WHEN score IS NULL THEN 0.0
              WHEN trim(score::text) ~ '{NUMERIC_LITERAL_RE}'
                THEN trim(score::text)::double precision
              ELSE 0.0
            END
        """
    else:
        using_expression = "0.0"

    bind.execute(
        text(
            f"""
            ALTER TABLE rag_retrieval_events
            ALTER COLUMN score DROP DEFAULT,
            ALTER COLUMN score TYPE DOUBLE PRECISION
            USING ({using_expression})
            """
        )
    )
    bind.execute(text("ALTER TABLE rag_retrieval_events ALTER COLUMN score SET NOT NULL"))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "rag_quota_policies") and _column_exists(inspector, "rag_quota_policies", "scope_target"):
        _alter_varchar_length(bind, "rag_quota_policies", "scope_target", 30)

    if _table_exists(inspector, "rag_collections") and _column_exists(inspector, "rag_collections", "tenant_id"):
        _drop_not_null(bind, "rag_collections", "tenant_id")

    if _table_exists(inspector, "rag_documents"):
        if _column_exists(inspector, "rag_documents", "tenant_id"):
            _drop_not_null(bind, "rag_documents", "tenant_id")
        if _column_exists(inspector, "rag_documents", "status"):
            _alter_varchar_length(bind, "rag_documents", "status", 30)

    if _table_exists(inspector, "rag_retrieval_events"):
        if _column_exists(inspector, "rag_retrieval_events", "tenant_id"):
            _drop_not_null(bind, "rag_retrieval_events", "tenant_id")
        if _column_exists(inspector, "rag_retrieval_events", "score"):
            _normalize_retrieval_score(bind)


def downgrade() -> None:
    # This is a one-way repair migration. Downgrading would reintroduce schema
    # drift and is intentionally left as a no-op.
    pass
