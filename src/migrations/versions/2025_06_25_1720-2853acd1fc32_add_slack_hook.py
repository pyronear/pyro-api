"""Add Slack Hook
Revision ID: 2853acd1fc32
Revises: 4265426f8438
Create Date: 2025-06-25 17:20:14.959429.
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2853acd1fc32"
down_revision: str | None = "42dzeg392dhu"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("organization", sa.Column("slack_hook", sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column("organization", "slack_hook")
