"""Add crop box and crop job queue to sequences

Revision ID: c8e2f5b3d0a7
Revises: b7d1e4a2c9f6
Create Date: 2026-11-26 11:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8e2f5b3d0a7"
down_revision: Union[str, None] = "b7d1e4a2c9f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sequences", sa.Column("crop_box", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column("sequences", sa.Column("crops_due_at", sa.DateTime(), nullable=True))
    op.add_column("sequences", sa.Column("crops_lease_until", sa.DateTime(), nullable=True))
    # Partial index: the crop worker polls for due rows, and almost every row has crops_due_at IS NULL.
    op.create_index(
        "ix_sequences_crops_due_at",
        "sequences",
        ["crops_due_at"],
        postgresql_where=sa.text("crops_due_at IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_sequences_crops_due_at", table_name="sequences")
    op.drop_column("sequences", "crops_lease_until")
    op.drop_column("sequences", "crops_due_at")
    op.drop_column("sequences", "crop_box")
