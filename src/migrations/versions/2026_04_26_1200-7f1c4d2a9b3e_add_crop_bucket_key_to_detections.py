"""Add crop_bucket_key to detections

Revision ID: 7f1c4d2a9b3e
Revises: b3d8a9c1e2f4
Create Date: 2026-04-26 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f1c4d2a9b3e"
down_revision: Union[str, None] = "b3d8a9c1e2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("detections", sa.Column("crop_bucket_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column("detections", "crop_bucket_key")
