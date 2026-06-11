"""add temporal validation columns and job state to sequences

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
    # Validation job state: due marker (the queue), worker lease, final outcome, and
    # consecutive-error counter (dead-letter cap).
    op.add_column("sequences", sa.Column("validation_due_at", sa.DateTime(), nullable=True))
    op.add_column("sequences", sa.Column("validation_lease_until", sa.DateTime(), nullable=True))
    op.add_column("sequences", sa.Column("validation_status", sa.String(length=32), nullable=True))
    op.add_column(
        "sequences",
        sa.Column("validation_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    # Enforce the status value set in the DB (single source of truth lives in app.models;
    # NULL rows pass a CHECK by definition).
    op.create_check_constraint(
        "ck_sequences_validation_status",
        "sequences",
        "validation_status IN ('model', 'fail_open_unavailable', 'fail_open_stale', 'window_exhausted', 'failed')",
    )
    # The worker polls for due rows; keep that scan off the table with a partial index
    # (almost every row has validation_due_at IS NULL).
    op.create_index(
        "ix_sequences_validation_due_at",
        "sequences",
        ["validation_due_at"],
        postgresql_where=sa.text("validation_due_at IS NOT NULL"),
    )
    # Existing sequences predate the validation gate; treat them as already validated
    # so they keep triangulating and remain eligible as triangulation partners.
    bind = op.get_bind()
    bind.execute(sa.text("UPDATE sequences SET is_validated = true"))
    logger.info("Backfilled is_validated=true for existing sequences")


def downgrade() -> None:
    op.drop_index("ix_sequences_validation_due_at", table_name="sequences")
    op.drop_constraint("ck_sequences_validation_status", "sequences", type_="check")
    op.drop_column("sequences", "validation_attempts")
    op.drop_column("sequences", "validation_status")
    op.drop_column("sequences", "validation_lease_until")
    op.drop_column("sequences", "validation_due_at")
    op.drop_column("sequences", "is_validated")
    op.drop_column("sequences", "temporal_model_score")
