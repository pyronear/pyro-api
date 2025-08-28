"""modify is_wilfire column

Revision ID: 307a1d6d490d
Revises: 2853acd1fc32
Create Date: 2025-08-20 16:47:05.346210

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "307a1d6d490d"
down_revision: Union[str, None] = "2853acd1fc32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the new ENUM type
annotation_type_enum = sa.Enum(
    "WILDFIRE_SMOKE",
    "OTHER_SMOKE",
    "ANTENNA",
    "BUILDING",
    "CLIFF",
    "DARK",
    "DUST",
    "HIGH_CLOUD",
    "LOW_CLOUD",
    "LENS_FLARE",
    "LENS_DROPLET",
    "LIGHT",
    "RAIN",
    "TRAIL",
    "ROAD",
    "SKY",
    "TREE",
    "WATER_BODY",
    "DOUBT",
    "OTHER",
    name="annotationtype",
)


def upgrade():
    # Create the enum type in the database
    annotation_type_enum.create(op.get_bind(), checkfirst=True)

    # Use raw SQL with a CASE expression for the conversion
    op.execute("""
        ALTER TABLE sequences
        ALTER COLUMN is_wildfire
        TYPE annotationtype
        USING CASE
            WHEN is_wildfire = TRUE THEN 'WILDFIRE_SMOKE'::annotationtype
            ELSE 'OTHER'::annotationtype
        END
    """)


def downgrade():
    # Revert the column back to a boolean (or previous enum if applicable)
    op.execute("""
        ALTER TABLE sequences
        ALTER COLUMN is_wildfire
        TYPE boolean
        USING CASE
            WHEN is_wildfire = 'WILDFIRE_SMOKE' THEN TRUE
            ELSE FALSE
        END
    """)

    # Drop the enum type from the DB
    annotation_type_enum.drop(op.get_bind(), checkfirst=True)
