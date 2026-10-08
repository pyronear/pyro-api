import pytest

from app.models import Detection, Sequence


@pytest.mark.parametrize(
    ("model", "name", "columns", "predicate"),
    [
        (Detection, "ix_detections_sequence_id_created_at", ["sequence_id", "created_at"], None),
        (Detection, "ix_detections_bucket_key", ["bucket_key"], None),
        (
            Detection,
            "ix_detections_unassigned_camera_pose_created_at",
            ["camera_id", "pose_id", "created_at"],
            "sequence_id IS NULL",
        ),
        (Sequence, "ix_sequences_camera_pose_last_seen", ["camera_id", "pose_id", "last_seen_at"], None),
        (Sequence, "ix_sequences_validation_due_at", ["validation_due_at"], "validation_due_at IS NOT NULL"),
    ],
)
def test_lookup_index_columns_and_predicates(model, name, columns, predicate):
    index = next(index for index in model.__table__.indexes if index.name == name)
    assert [column.name for column in index.columns] == columns
    where = index.dialect_options["postgresql"]["where"]
    assert (str(where) if where is not None else None) == predicate
