"""add active column to poses

Revision ID: a1b2c3d4e5f6
Revises: 307a1d6d490d
Create Date: 2026-04-14 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "307a1d6d490d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "poses" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("poses")]
        if "active" not in columns:
            op.add_column("poses", sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "poses" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("poses")]
        if "active" in columns:
            op.drop_column("poses", "active")
