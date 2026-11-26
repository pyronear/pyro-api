"""Add native crop key and window to detections

Revision ID: b7d1e4a2c9f6
Revises: 94a223eae6ac
Create Date: 2026-11-26 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7d1e4a2c9f6"
down_revision: Union[str, None] = "94a223eae6ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("detections", sa.Column("native_crop_bucket_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column("detections", sa.Column("native_crop_window", sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column("detections", "native_crop_window")
    op.drop_column("detections", "native_crop_bucket_key")
