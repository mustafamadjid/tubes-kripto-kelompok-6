"""rename voter_id columns to nim

Revision ID: 20260524_0002
Revises: 20260522_0001
Create Date: 2026-05-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260524_0002"
down_revision: Union[str, None] = "20260522_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_vote_records_voter_id", table_name="vote_records")
    op.drop_index("ix_voters_voter_id", table_name="voters")

    op.alter_column(
        "voters",
        "voter_id",
        new_column_name="nim",
        existing_type=sa.String(length=32),
        existing_nullable=False,
    )
    op.alter_column(
        "vote_records",
        "voter_id",
        new_column_name="nim",
        existing_type=sa.String(length=32),
        existing_nullable=False,
    )

    op.create_index("ix_voters_nim", "voters", ["nim"])
    op.create_index("ix_vote_records_nim", "vote_records", ["nim"])

    op.execute(
        """
        UPDATE voters
        SET nim = '12214' || lpad(substring(nim from 6), 4, '0')
        WHERE nim ~ '^VOTER[0-9]+$'
        """
    )
    op.execute(
        """
        UPDATE vote_records
        SET nim = '12214' || lpad(substring(nim from 6), 4, '0')
        WHERE nim ~ '^VOTER[0-9]+$'
        """
    )


def downgrade() -> None:
    op.drop_index("ix_vote_records_nim", table_name="vote_records")
    op.drop_index("ix_voters_nim", table_name="voters")

    op.alter_column(
        "vote_records",
        "nim",
        new_column_name="voter_id",
        existing_type=sa.String(length=32),
        existing_nullable=False,
    )
    op.alter_column(
        "voters",
        "nim",
        new_column_name="voter_id",
        existing_type=sa.String(length=32),
        existing_nullable=False,
    )

    op.create_index("ix_voters_voter_id", "voters", ["voter_id"])
    op.create_index("ix_vote_records_voter_id", "vote_records", ["voter_id"])
