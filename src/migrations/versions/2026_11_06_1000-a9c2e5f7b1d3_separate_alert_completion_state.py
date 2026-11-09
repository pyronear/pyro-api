"""separate alert completion state from the validation verdict

Revision ID: a9c2e5f7b1d3
Revises: ff5b6d1f9e3f
Create Date: 2026-11-06 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9c2e5f7b1d3"
down_revision: Union[str, None] = "ff5b6d1f9e3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sequences", sa.Column("completion_status", sa.String(length=16), nullable=True))
    op.add_column("sequences", sa.Column("completion_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column(
        "sequences",
        sa.Column("completion_suppress_notifications", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_check_constraint(
        "ck_sequences_completion_status", "sequences", "completion_status IN ('pending', 'completed', 'failed')"
    )
    # The old worker overwrote the verdict with 'failed' after attachment errors.
    # Preserve those rows as recoverable failures; the original reason is unknowable.
    op.execute(
        sa.text("""
        UPDATE sequences
        SET completion_status = CASE
                WHEN validation_status = 'failed' THEN 'failed'
                WHEN validation_due_at IS NOT NULL THEN 'pending'
                ELSE 'completed'
            END,
            completion_attempts = validation_attempts,
            validation_attempts = 0,
            validation_status = CASE WHEN validation_status = 'failed' THEN NULL ELSE validation_status END
        WHERE is_validated = true
    """)
    )
    op.create_index(
        "ix_sequences_failed_completion", "sequences", ["id"], postgresql_where=sa.text("completion_status = 'failed'")
    )


def downgrade() -> None:
    # Restore the old worker's shared counter and failure convention on rollback.
    op.execute(
        sa.text("""
        UPDATE sequences
        SET validation_attempts = completion_attempts,
            validation_status = CASE
                WHEN completion_status = 'failed' THEN 'failed' ELSE validation_status
            END
        WHERE is_validated = true
    """)
    )
    op.drop_index("ix_sequences_failed_completion", table_name="sequences")
    op.drop_constraint("ck_sequences_completion_status", "sequences", type_="check")
    op.drop_column("sequences", "completion_suppress_notifications")
    op.drop_column("sequences", "completion_attempts")
    op.drop_column("sequences", "completion_status")
