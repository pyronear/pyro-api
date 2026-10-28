import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes

from app.api.dependencies import get_jwt
from app.core.security import create_access_token


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.mark.parametrize(
    ("scopes", "token", "expires_minutes", "error_code", "expected_payload"),
    [
        (["admin"], "", None, 401, None),
        (["admin"], "not-a-jwt", None, 401, None),
        (["admin"], {"user_id": "123", "scopes": ["admin"]}, None, 401, None),
        (["admin"], {"sub": "123", "scopes": ["admin"]}, -1, 401, None),
        (["camera"], {"sub": "0", "scopes": ["camera"], "organization_id": 1}, None, 401, None),
        (["camera"], {"sub": "cam-1", "scopes": ["camera"], "organization_id": 1}, None, 401, None),
        (
            ["admin"],
            {"sub": "123", "scopes": ["admin"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["admin"], "organization_id": 1},
        ),
        (
            ["agent"],
            {"sub": "123", "scopes": ["agent"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["agent"], "organization_id": 1},
        ),
        (
            ["camera"],
            {"sub": "123", "scopes": ["camera"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["camera"], "organization_id": 1},
        ),
        (
            ["user"],
            {"sub": "123", "scopes": ["user"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["user"], "organization_id": 1},
        ),
        (["admin"], {"sub": "123", "scopes": ["user"], "organization_id": 1}, None, 403, None),
        (["admin"], {"sub": "123", "scopes": ["agent"], "organization_id": 1}, None, 403, None),
        (["admin"], {"sub": "123", "scopes": ["camera"], "organization_id": 1}, None, 403, None),
    ],
)
def test_get_jwt(scopes, token, expires_minutes, error_code, expected_payload):
    token_ = create_access_token(token, expires_minutes) if isinstance(token, dict) else token
    if isinstance(error_code, int):
        with pytest.raises(HTTPException) as exc_info:
            get_jwt(SecurityScopes(scopes), _creds(token_))
        assert exc_info.value.status_code == error_code
    else:
        payload = get_jwt(SecurityScopes(scopes), _creds(token_))
        if expected_payload is not None:
            assert payload.model_dump() == expected_payload


def test_get_jwt_missing_credentials():
    with pytest.raises(HTTPException) as exc_info:
        get_jwt(SecurityScopes(["user"]), None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


def test_camera_id():
    payload = get_jwt(
        SecurityScopes(["camera"]),
        _creds(create_access_token({"sub": "7", "scopes": ["camera"], "organization_id": 1})),
    )
    assert payload.camera_id == 7
    user_payload = get_jwt(
        SecurityScopes(["user"]), _creds(create_access_token({"sub": "7", "scopes": ["user"], "organization_id": 1}))
    )
    with pytest.raises(ValueError, match="camera tokens"):
        _ = user_payload.camera_id
