"""create wildifre table

Revision ID: 77abcf481de4
Revises: 4265426f8438
Create Date: 2024-06-24 11:10:26.737989

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "77abcf481de4"
down_revision: Union[str, None] = "4265426f8438"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wildfire",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("starting_time", sa.DateTime(), nullable=False),
        sa.Column("ending_time", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["wildifre_camera_id"],
            ["camera.id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("wildfire")
