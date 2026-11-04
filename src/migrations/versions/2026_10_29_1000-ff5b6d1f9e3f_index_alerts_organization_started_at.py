"""index alerts by organization and start time

Revision ID: ff5b6d1f9e3f
Revises: e7a4b9c3d5f2
Create Date: 2026-10-29 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "ff5b6d1f9e3f"
down_revision: Union[str, None] = "e7a4b9c3d5f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Deployment stops the backend before migration; transactional builds avoid invalid indexes.
    op.create_index("ix_alerts_organization_id_started_at", "alerts", ["organization_id", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_alerts_organization_id_started_at", table_name="alerts")
