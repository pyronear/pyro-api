import os

import pytest
import requests

from app.services.slack import SlackClient


def test_failure_slack_client():
    client = SlackClient()

    # Expecting MissingSchema exception from requests
    with pytest.raises(requests.exceptions.MissingSchema, match=r"Invalid URL 'invalid-hook-url': No scheme supplied."):
        client.has_channel_access("invalid-hook-url")

    json = """{"sequence_id":3,"camera_id":2,"azimuth":45.6,"bucket_key":"2-20250516153957-d3aa94be.jpg","created_at":"2025-05-16T15:39:57.915328","id":7,"bboxes":"[(0.6,0.6,0.7,0.7,0.6)]"}"""
    with pytest.raises(requests.exceptions.MissingSchema, match=r"Invalid URL 'invalid-hook-url': No scheme supplied."):
        client.notify("invalid-hook-url", json, "url", "name")


def test_slack_client():
    hook: str = os.environ["SLACK_HOOK"]
    client = SlackClient()

    json = """{"sequence_id":3,"camera_id":2,"azimuth":45.6,"bucket_key":"2-20250516153957-d3aa94be.jpg","created_at":"2025-05-16T15:39:57.915328","id":7,"bboxes":"[(0.6,0.6,0.7,0.7,0.6)]"}"""
    response = client.notify(hook, json, None, "name")
    if hook is not None:
        assert response.status_code == 200
