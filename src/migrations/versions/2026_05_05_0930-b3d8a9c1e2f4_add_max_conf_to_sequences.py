"""add max_conf column to sequences and backfill from detections

Revision ID: b3d8a9c1e2f4
Revises: a1b2c3d4e5f6
Create Date: 2026-05-05 09:30:00.000000

"""

import logging
import re
from ast import literal_eval
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3d8a9c1e2f4"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

logger = logging.getLogger("alembic.runtime.migration")

_FLOAT = r"-?\d+(?:\.\d+)?|-?\.\d+"
_BOX_PATTERN = rf"\({_FLOAT},{_FLOAT},{_FLOAT},{_FLOAT},{_FLOAT}\)"


def _max_conf(*bbox_strings: Union[str, None]) -> Union[float, None]:
    best: Union[float, None] = None
    for raw in bbox_strings:
        if not raw:
            continue
        for match in re.finditer(_BOX_PATTERN, raw):
            try:
                bbox = literal_eval(match.group(0))
            except (SyntaxError, ValueError):
                continue
            if not isinstance(bbox, tuple) or len(bbox) != 5:
                continue
            conf = bbox[4]
            if not isinstance(conf, (int, float)):
                continue
            if best is None or conf > best:
                best = float(conf)
    return best


def upgrade() -> None:
    op.add_column("sequences", sa.Column("max_conf", sa.Float(), nullable=True))

    bind = op.get_bind()
    rows = bind.execute(
        sa.text("SELECT sequence_id, bbox, others_bboxes FROM detections WHERE sequence_id IS NOT NULL")
    ).fetchall()

    seq_max: dict[int, float] = {}
    for sequence_id, bbox, others in rows:
        conf = _max_conf(bbox, others)
        if conf is None:
            continue
        current = seq_max.get(sequence_id)
        if current is None or conf > current:
            seq_max[sequence_id] = conf

    if seq_max:
        bind.execute(
            sa.text("UPDATE sequences SET max_conf = :conf WHERE id = :sid"),
            [{"sid": sid, "conf": conf} for sid, conf in seq_max.items()],
        )
    logger.info("Backfilled max_conf for %d sequence(s)", len(seq_max))


def downgrade() -> None:
    op.drop_column("sequences", "max_conf")
