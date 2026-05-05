"""Add shared RAG storage and quota policy tables.

This revision introduces the first shared schema foundation for organization-
level knowledge repositories and user-level personal context repositories.
Quota policy is DB-backed so the runtime can resolve limits by default,
service tier, and tenant override without hard-coded environment values.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "20260505_0015"
down_revision = "20260505_0014"
branch_labels = None
depends_on = None


GLOBAL_DEFAULT_POLICY_KEY = "global_default_v1"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _table_exists(inspector, "rag_quota_policies"):
        op.create_table(
            "rag_quota_policies",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("policy_key", sa.String(length=100), nullable=False),
            sa.Column("scope_target", sa.String(length=30), nullable=False),
            sa.Column("service_tier_definition_id", sa.String(length=36), nullable=True),
            sa.Column("tenant_id", sa.String(length=36), nullable=True),
            sa.Column("user_type", sa.Integer(), nullable=True),
            sa.Column("org_max_file_bytes", sa.BigInteger(), nullable=False),
            sa.Column("user_max_file_bytes", sa.BigInteger(), nullable=False),
            sa.Column("org_max_document_count", sa.Integer(), nullable=False),
            sa.Column("user_max_document_count", sa.Integer(), nullable=False),
            sa.Column("org_max_total_bytes", sa.BigInteger(), nullable=False),
            sa.Column("user_max_total_bytes", sa.BigInteger(), nullable=False),
            sa.Column("org_max_extracted_text_bytes", sa.BigInteger(), nullable=False),
            sa.Column("user_max_extracted_text_bytes", sa.BigInteger(), nullable=False),
            sa.Column("org_max_chunks_per_document", sa.Integer(), nullable=False),
            sa.Column("user_max_chunks_per_document", sa.Integer(), nullable=False),
            sa.Column("org_max_retrieved_chunks", sa.Integer(), nullable=False),
            sa.Column("user_max_retrieved_chunks", sa.Integer(), nullable=False),
            sa.Column("max_retrieved_chunks_total", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["service_tier_definition_id"], ["service_tier_definitions.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("policy_key"),
        )
        op.create_index("ix_rag_quota_policies_scope_target", "rag_quota_policies", ["scope_target"])
        op.create_index("ix_rag_quota_policies_service_tier_definition_id", "rag_quota_policies", ["service_tier_definition_id"])
        op.create_index("ix_rag_quota_policies_tenant_id", "rag_quota_policies", ["tenant_id"])

    if not _table_exists(inspector, "rag_collections"):
        op.create_table(
            "rag_collections",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("scope_type", sa.String(length=20), nullable=False),
            sa.Column("tenant_id", sa.String(length=36), nullable=True),
            sa.Column("user_id_hash", sa.String(length=255), nullable=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("retrieval_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("max_results", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_rag_collections_scope_type", "rag_collections", ["scope_type"])
        op.create_index("ix_rag_collections_tenant_id", "rag_collections", ["tenant_id"])
        op.create_index("ix_rag_collections_user_id_hash", "rag_collections", ["user_id_hash"])

    if not _table_exists(inspector, "rag_documents"):
        op.create_table(
            "rag_documents",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("collection_id", sa.String(length=36), nullable=False),
            sa.Column("scope_type", sa.String(length=20), nullable=False),
            sa.Column("tenant_id", sa.String(length=36), nullable=True),
            sa.Column("user_id_hash", sa.String(length=255), nullable=True),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("media_type", sa.String(length=120), nullable=True),
            sa.Column("size_bytes", sa.BigInteger(), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
            sa.Column("status_message", sa.Text(), nullable=True),
            sa.Column("sha256", sa.String(length=64), nullable=False),
            sa.Column("source_kind", sa.String(length=30), nullable=False, server_default="database_blob"),
            sa.Column("uploaded_by_admin_user_id", sa.String(length=36), nullable=True),
            sa.Column("uploaded_by_user_id_hash", sa.String(length=255), nullable=True),
            sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["collection_id"], ["rag_collections.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["uploaded_by_admin_user_id"], ["admin_users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_rag_documents_collection_id", "rag_documents", ["collection_id"])
        op.create_index("ix_rag_documents_scope_type", "rag_documents", ["scope_type"])
        op.create_index("ix_rag_documents_tenant_id", "rag_documents", ["tenant_id"])
        op.create_index("ix_rag_documents_user_id_hash", "rag_documents", ["user_id_hash"])
        op.create_index("ix_rag_documents_status", "rag_documents", ["status"])

    if not _table_exists(inspector, "rag_document_blobs"):
        op.create_table(
            "rag_document_blobs",
            sa.Column("document_id", sa.String(length=36), nullable=False),
            sa.Column("content_bytes", sa.LargeBinary(), nullable=False),
            sa.ForeignKeyConstraint(["document_id"], ["rag_documents.id"]),
            sa.PrimaryKeyConstraint("document_id"),
        )

    if not _table_exists(inspector, "rag_chunks"):
        op.create_table(
            "rag_chunks",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("document_id", sa.String(length=36), nullable=False),
            sa.Column("chunk_index", sa.Integer(), nullable=False),
            sa.Column("chunk_text", sa.Text(), nullable=False),
            sa.Column("token_count", sa.Integer(), nullable=False),
            sa.Column("embedding_vector", sa.JSON(), nullable=False),
            sa.Column("embedding_model", sa.String(length=100), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["document_id"], ["rag_documents.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("document_id", "chunk_index"),
        )
        op.create_index("ix_rag_chunks_document_id", "rag_chunks", ["document_id"])

    if not _table_exists(inspector, "rag_retrieval_events"):
        op.create_table(
            "rag_retrieval_events",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("conversation_id", sa.String(length=255), nullable=False),
            sa.Column("user_id_hash", sa.String(length=255), nullable=False),
            sa.Column("tenant_id", sa.String(length=36), nullable=True),
            sa.Column("scope_type", sa.String(length=20), nullable=False),
            sa.Column("document_id", sa.String(length=36), nullable=False),
            sa.Column("chunk_id", sa.String(length=36), nullable=False),
            sa.Column("rank", sa.Integer(), nullable=False),
            sa.Column("score", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["document_id"], ["rag_documents.id"]),
            sa.ForeignKeyConstraint(["chunk_id"], ["rag_chunks.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_rag_retrieval_events_conversation_id", "rag_retrieval_events", ["conversation_id"])
        op.create_index("ix_rag_retrieval_events_tenant_id", "rag_retrieval_events", ["tenant_id"])
        op.create_index("ix_rag_retrieval_events_user_id_hash", "rag_retrieval_events", ["user_id_hash"])

    if _table_exists(inspector, "tenant_onboarding_status"):
        onboarding_columns = _column_names(inspector, "tenant_onboarding_status")
        with op.batch_alter_table("tenant_onboarding_status") as batch_op:
            if "knowledge_configured" not in onboarding_columns:
                batch_op.add_column(sa.Column("knowledge_configured", sa.Boolean(), nullable=False, server_default=sa.text("false")))
            if "knowledge_ready" not in onboarding_columns:
                batch_op.add_column(sa.Column("knowledge_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    bind.execute(
        text(
            """
            INSERT INTO rag_quota_policies (
              id,
              policy_key,
              scope_target,
              service_tier_definition_id,
              tenant_id,
              user_type,
              org_max_file_bytes,
              user_max_file_bytes,
              org_max_document_count,
              user_max_document_count,
              org_max_total_bytes,
              user_max_total_bytes,
              org_max_extracted_text_bytes,
              user_max_extracted_text_bytes,
              org_max_chunks_per_document,
              user_max_chunks_per_document,
              org_max_retrieved_chunks,
              user_max_retrieved_chunks,
              max_retrieved_chunks_total,
              is_active,
              created_at,
              updated_at
            )
            SELECT
              'rag-policy-global-default-v1',
              :policy_key,
              'global_default',
              NULL,
              NULL,
              NULL,
              :org_max_file_bytes,
              :user_max_file_bytes,
              :org_max_document_count,
              :user_max_document_count,
              :org_max_total_bytes,
              :user_max_total_bytes,
              :org_max_extracted_text_bytes,
              :user_max_extracted_text_bytes,
              :org_max_chunks_per_document,
              :user_max_chunks_per_document,
              :org_max_retrieved_chunks,
              :user_max_retrieved_chunks,
              :max_retrieved_chunks_total,
              true,
              CURRENT_TIMESTAMP,
              CURRENT_TIMESTAMP
            WHERE NOT EXISTS (
              SELECT 1
              FROM rag_quota_policies
              WHERE policy_key = :policy_key
            )
            """
        ),
        {
            "policy_key": GLOBAL_DEFAULT_POLICY_KEY,
            "org_max_file_bytes": 25 * 1024 * 1024,
            "user_max_file_bytes": 10 * 1024 * 1024,
            "org_max_document_count": 100,
            "user_max_document_count": 20,
            "org_max_total_bytes": 250 * 1024 * 1024,
            "user_max_total_bytes": 50 * 1024 * 1024,
            "org_max_extracted_text_bytes": 1024 * 1024,
            "user_max_extracted_text_bytes": 512 * 1024,
            "org_max_chunks_per_document": 500,
            "user_max_chunks_per_document": 200,
            "org_max_retrieved_chunks": 4,
            "user_max_retrieved_chunks": 2,
            "max_retrieved_chunks_total": 6,
        },
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "rag_quota_policies"):
        bind.execute(text("DELETE FROM rag_quota_policies WHERE policy_key = :policy_key"), {"policy_key": GLOBAL_DEFAULT_POLICY_KEY})

    if _table_exists(inspector, "tenant_onboarding_status"):
        onboarding_columns = _column_names(inspector, "tenant_onboarding_status")
        with op.batch_alter_table("tenant_onboarding_status") as batch_op:
            if "knowledge_ready" in onboarding_columns:
                batch_op.drop_column("knowledge_ready")
            if "knowledge_configured" in onboarding_columns:
                batch_op.drop_column("knowledge_configured")

    for table_name in (
        "rag_retrieval_events",
        "rag_chunks",
        "rag_document_blobs",
        "rag_documents",
        "rag_collections",
        "rag_quota_policies",
    ):
        if _table_exists(inspector, table_name):
            op.drop_table(table_name)
