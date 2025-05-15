import pytest

from app.core.config import settings
from app.services.slack import SlackClient
import requests
import os

def test_failure_slack_client():
    client = SlackClient()

    # Expecting MissingSchema exception from requests
    with pytest.raises(requests.exceptions.MissingSchema, match="Invalid URL 'invalid-hook-url': No scheme supplied."):
        client.has_channel_access("invalid-hook-url")

    with pytest.raises(requests.exceptions.MissingSchema, match="Invalid URL 'invalid-hook-url': No scheme supplied."):
        client.notify("invalid-hook-url", "test")

def test_slack_client():
    hook: str = os.environ["SLACK_HOOK"]
    client = SlackClient()
    print(hook)
    response =  client.notify(hook, "test")
    assert response.status_code == 400

    response = client.notify(hook, { "text": "test" })
    print(response.text)
    assert response.status_code == 200
