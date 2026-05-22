"""initial schema

Revision ID: 20260522_0001
Revises:
Create Date: 2026-05-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260522_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "voters",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("voter_id", sa.String(length=32), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("has_voted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_voters_voter_id", "voters", ["voter_id"])
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "vote_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("voter_id", sa.String(length=32), nullable=False, unique=True),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("ciphertext_hash", sa.String(length=64), nullable=False),
        sa.Column("signature", sa.LargeBinary(), nullable=False),
        sa.Column("verification_status", sa.String(length=32), nullable=True),
        sa.Column("manipulation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_vote_records_voter_id", "vote_records", ["voter_id"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "benchmark_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("operation_name", sa.String(length=80), nullable=False),
        sa.Column("duration_ms", sa.Numeric(12, 6), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("benchmark_records")
    op.drop_table("audit_logs")
    op.drop_index("ix_vote_records_voter_id", table_name="vote_records")
    op.drop_table("vote_records")
    op.drop_table("candidates")
    op.drop_index("ix_voters_voter_id", table_name="voters")
    op.drop_table("voters")
