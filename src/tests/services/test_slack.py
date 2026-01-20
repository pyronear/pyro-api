import os

import httpx
import pytest

from app.services.slack import SlackClient


@pytest.mark.asyncio
async def test_failure_slack_client():
    client = SlackClient()

    # Expecting UnsupportedProtocol exception from httpx
    with pytest.raises(httpx.UnsupportedProtocol):
        await client.has_channel_access("invalid-hook-url")

    json = """{"sequence_id":3,"camera_id":2,"azimuth":45.6,"bucket_key":"2-20250516153957-d3aa94be.jpg","created_at":"2025-05-16T15:39:57.915328","id":7,"bboxes":"[(0.6,0.6,0.7,0.7,0.6)]"}"""
    with pytest.raises(httpx.UnsupportedProtocol):
        await client.notify("invalid-hook-url", json, "url", "name")


@pytest.mark.asyncio
async def test_slack_client():
    hook: str = os.environ.get("SLACK_HOOK", "")
    client = SlackClient()

    json = """{"sequence_id":3,"camera_id":2,"azimuth":45.6,"bucket_key":"2-20250516153957-d3aa94be.jpg","created_at":"2025-05-16T15:39:57.915328","id":7,"bboxes":"[(0.6,0.6,0.7,0.7,0.6)]"}"""
    if hook != "":
        response = await client.notify(hook, json, None, "name")
        assert response.status_code == 200
