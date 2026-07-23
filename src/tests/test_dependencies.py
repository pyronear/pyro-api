from datetime import datetime

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from pydantic import BaseModel

from app.api.dependencies import dispatch_webhook, get_jwt
from app.core.security import create_access_token


@pytest.mark.parametrize(
    ("scopes", "token", "expires_minutes", "error_code", "expected_payload"),
    [
        (["admin"], "", None, 406, None),
        (["admin"], {"user_id": "123", "scopes": ["admin"]}, None, 422, None),
        (["admin"], {"sub": "123", "scopes": ["admin"]}, -1, 401, None),
        (
            ["admin"],
            {"sub": "123", "scopes": ["admin"], "organization_id": 1},
            None,
            None,
            {"sub": 123, "scopes": ["admin"], "organization_id": 1},
        ),
        (
            ["agent"],
            {"sub": "123", "scopes": ["agent"], "organization_id": 1},
            None,
            None,
            {"sub": 123, "scopes": ["agent"], "organization_id": 1},
        ),
        (
            ["camera"],
            {"sub": "123", "scopes": ["camera"], "organization_id": 1},
            None,
            None,
            {"sub": 123, "scopes": ["camera"], "organization_id": 1},
        ),
        (
            ["user"],
            {"sub": "123", "scopes": ["user"], "organization_id": 1},
            None,
            None,
            {"sub": 123, "scopes": ["user"], "organization_id": 1},
        ),
        (["admin"], {"sub": "123", "scopes": ["user"]}, None, 403, None),
        (["admin"], {"sub": "123", "scopes": ["agent"]}, None, 403, None),
        (["admin"], {"sub": "123", "scopes": ["camera"]}, None, 403, None),
    ],
)
def test_get_jwt(scopes, token, expires_minutes, error_code, expected_payload):
    token_ = create_access_token(token, expires_minutes) if isinstance(token, dict) else token
    if isinstance(error_code, int):
        with pytest.raises(HTTPException):
            get_jwt(SecurityScopes(scopes), token_)
    else:
        payload = get_jwt(SecurityScopes(scopes), token_)
        if expected_payload is not None:
            assert payload.model_dump() == expected_payload


@pytest.mark.asyncio
async def test_dispatch_webhook_sends_json_object(monkeypatch):
    captured = {}

    class _Response:
        def raise_for_status(self):
            return None

    async def _post(self, url, json=None):  # ruff:ignore[unused-async] - must match AsyncClient.post's async signature
        captured["json"] = json
        return _Response()

    monkeypatch.setattr("app.api.dependencies.AsyncClient.post", _post)

    class _Payload(BaseModel):
        id: int
        created_at: datetime

    await dispatch_webhook("https://example.com/hook", _Payload(id=1, created_at=datetime(2026, 6, 11, 15, 38, 6)))

    # The body must be a JSON object, not a double-encoded JSON string
    assert captured["json"] == {"id": 1, "created_at": "2026-06-11T15:38:06"}
