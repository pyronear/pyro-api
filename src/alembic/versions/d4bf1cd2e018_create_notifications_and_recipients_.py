"""Create notifications and recipients tables

Revision ID: d4bf1cd2e018
Revises: 92e49f7d80ae
Create Date: 2023-12-14 09:51:46.749939

"""
from alembic import op
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "d4bf1cd2e018"
down_revision = "92e49f7d80ae"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        Column("id", Integer, primary_key=True),
        Column("created_at", DateTime, default=func.now()),
        Column("alert_id", Integer, ForeignKey("alerts.id")),
        Column("recipient_id", Integer, ForeignKey("recipients.id")),
        Column("subject", String, nullable=False),
        Column("message", String, nullable=False),
        keep_existing=True
    )

    op.create_table(
        "recipients",
        Column("id", Integer, primary_key=True),
        Column("created_at", DateTime, default=func.now()),
        Column("alert_id", Integer, ForeignKey("alerts.id")),
        Column("recipient_id", Integer, ForeignKey("recipients.id")),
        Column("subject", String, nullable=False),
        Column("message", String, nullable=False),
        keep_existing=True
    )


def downgrade():
    pass
