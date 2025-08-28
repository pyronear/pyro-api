"""Add Slack Hook
Revision ID: 2853acd1fc32
Revises: 4265426f8438
Create Date: 2025-06-25 17:20:14.959429
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2853acd1fc32"
down_revision: Union[str, None] = "42dzeg392dhu"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organization", sa.Column("slack_hook", sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column("organization", "slack_hook")
