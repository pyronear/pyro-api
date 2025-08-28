"""create news columns in cameras table

Revision ID: 47005ff54a94
Revises: 307a1d6d490d
Create Date: 2025-08-28 11:05:46.058307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '47005ff54a94'
down_revision: Union[str, None] = '307a1d6d490d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("camera", sa.Column("ip_address", sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column("camera", sa.Column("livestream_activated", sa.Boolean(), nullable=False))

def downgrade() -> None:
    op.drop_column("camera", "ip_address")
    op.drop_column("camera", "livestream_activated")