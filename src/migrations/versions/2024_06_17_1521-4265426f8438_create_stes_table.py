"""create stes table

Revision ID: 4265426f8438
Revises: f84a0ed81bdc
Create Date: 2024-06-17 15:21:58.003045

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4265426f8438"
down_revision: Union[str, None] = "f84a0ed81bdc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # TODO : create an index ?
    op.create_table(
        "organization",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("role", sa.Enum("SDIS", "PARTICULIER", name="organizationtype"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Add the 'organization_id' column to the 'camera' and 'user' tables and create  foreign key constraints
    op.add_column("camera", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_camera_orga", "camera", "organization", ["organization_id"], ["id"])
    op.add_column("user", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_user_orga", "camera", "organization", ["organization_id"], ["id"])


def downgrade() -> None:
    # Remove the foreign key constraint and the 'organization_id' column from the 'camera' table
    op.drop_constraint("fk_camera_orga", "camera", type_="foreignkey")
    op.drop_constraint("fk_user_orga", "user", type_="foreignkey")
    op.drop_column("camera", "organization_id")
    op.drop_column("user", "organization_idation_id")
    op.drop_table("detection")
