# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from app.services.sequence_confidence import max_conf_from_bboxes


def test_max_conf_from_single_bbox():
    assert max_conf_from_bboxes("[(.1,.1,.7,.8,.42)]") == 0.42


def test_max_conf_picks_max_across_bboxes_and_strings():
    bbox = "[(.1,.1,.7,.8,.3)]"
    others = "[(.1,.1,.5,.5,.7),(.2,.2,.6,.6,.55)]"
    assert max_conf_from_bboxes(bbox, others) == 0.7


def test_max_conf_handles_none_and_empty():
    assert max_conf_from_bboxes(None) is None
    assert max_conf_from_bboxes("") is None
    assert max_conf_from_bboxes(None, None) is None


def test_max_conf_skips_unparseable():
    assert max_conf_from_bboxes("[invalid]") is None
    assert max_conf_from_bboxes("[(.1,.1,.7,.8,.5)]", "[garbage]") == 0.5
