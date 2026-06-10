"""add temporal_model_score and is_validated columns to sequences

Revision ID: c5e2f7a8b1d0
Revises: 7f1c4d2a9b3e
Create Date: 2026-06-10 10:00:00.000000

"""

import logging
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5e2f7a8b1d0"
down_revision: Union[str, None] = "7f1c4d2a9b3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

logger = logging.getLogger("alembic.runtime.migration")


def upgrade() -> None:
    op.add_column("sequences", sa.Column("temporal_model_score", sa.Float(), nullable=True))
    op.add_column(
        "sequences",
        sa.Column("is_validated", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Existing sequences predate the validation gate; treat them as already validated
    # so they keep triangulating and remain eligible as triangulation partners.
    bind = op.get_bind()
    bind.execute(sa.text("UPDATE sequences SET is_validated = true"))
    logger.info("Backfilled is_validated=true for existing sequences")


def downgrade() -> None:
    op.drop_column("sequences", "is_validated")
    op.drop_column("sequences", "temporal_model_score")
