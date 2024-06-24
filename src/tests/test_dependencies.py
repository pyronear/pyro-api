import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes

from app.api.dependencies import get_jwt
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
    _token = create_access_token(token, expires_minutes) if isinstance(token, dict) else token
    if isinstance(error_code, int):
        with pytest.raises(HTTPException):
            get_jwt(SecurityScopes(scopes), _token)
    else:
        payload = get_jwt(SecurityScopes(scopes), _token)
        if expected_payload is not None:
            assert payload.model_dump() == expected_payload
