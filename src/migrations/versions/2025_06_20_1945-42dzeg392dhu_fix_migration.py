from alembic import op
import sqlalchemy as sa
import sqlmodel

# Ajoute ton identifiant de révision et dépendance si besoin
revision = '42dzeg392dhu'
down_revision = '4265426f8438'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Créer la table sequences (doit précéder la FK)
    op.create_table(
        "sequences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("camera.id"), nullable=False),
        sa.Column("azimuth", sa.Float(), nullable=False),
        sa.Column("is_wildfire", sa.Boolean(), nullable=True),  # sera modifié par la 4e migration
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
    )

    # 2. Ajouter les colonnes manquantes
    op.add_column("camera", sa.Column("last_image", sa.String(), nullable=True))
    op.add_column("organization", sa.Column("telegram_id", sa.String(), nullable=True))
    op.add_column("detection", sa.Column("sequence_id", sa.Integer(), nullable=True))
    op.add_column("detection", sa.Column("bboxes", sa.String(length=5000), nullable=False))  # adapter à settings

    # 3. Ajouter la contrainte FK après la création de la table sequences
    op.create_foreign_key(
        "fk_detection_sequence",
        "detection",
        "sequences",
        ["sequence_id"],
        ["id"],
    )

    # 4. Créer la table webhooks
    op.create_table(
        "webhooks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.String(), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("webhooks")
    op.drop_constraint("fk_detection_sequence", "detection", type_="foreignkey")
    op.drop_column("detection", "bboxes")
    op.drop_column("detection", "sequence_id")
    op.drop_column("organization", "telegram_id")
    op.drop_column("camera", "last_image")
    op.drop_table("sequences")