"""Add send_image to recipient and media_id to notification tables

Revision ID: 788a8c14f191
Revises: 92e49f7d80ae
Create Date: 2023-12-05 16:50:59.178742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '788a8c14f191'
down_revision = '92e49f7d80ae'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notifications', sa.Column('media_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'notifications', 'media', ['media_id'], ['id'])
    op.add_column('recipients', sa.Column('send_image', sa.Boolean(), nullable=True))


def downgrade():
    pass
