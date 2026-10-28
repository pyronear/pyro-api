import base64
import hashlib
import hmac
import json

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, SecurityScopes

from app.api.dependencies import get_jwt
from app.core import keycloak
from app.core.config import settings
from app.core.keycloak import map_keycloak_roles
from app.core.security import create_access_token
from app.models import Role


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


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
            {"sub": "123", "scopes": ["admin"], "organization_id": 1, "auth_source": "api"},
        ),
        (
            ["agent"],
            {"sub": "123", "scopes": ["agent"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["agent"], "organization_id": 1, "auth_source": "api"},
        ),
        (
            ["camera"],
            {"sub": "123", "scopes": ["camera"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["camera"], "organization_id": 1, "auth_source": "api"},
        ),
        (
            ["user"],
            {"sub": "123", "scopes": ["user"], "organization_id": 1},
            None,
            None,
            {"sub": "123", "scopes": ["user"], "organization_id": 1, "auth_source": "api"},
        ),
        (["admin"], {"sub": "123", "scopes": ["user"], "organization_id": 1}, None, 403, None),
        (["admin"], {"sub": "123", "scopes": ["agent"], "organization_id": 1}, None, 403, None),
        (["admin"], {"sub": "123", "scopes": ["camera"], "organization_id": 1}, None, 403, None),
    ],
)
@pytest.mark.asyncio
async def test_get_jwt(scopes, token, expires_minutes, error_code, expected_payload):
    token_ = create_access_token(token, expires_minutes) if isinstance(token, dict) else token
    if isinstance(error_code, int):
        with pytest.raises(HTTPException) as exc_info:
            await get_jwt(SecurityScopes(scopes), _creds(token_))
        assert exc_info.value.status_code == error_code
    else:
        payload = await get_jwt(SecurityScopes(scopes), _creds(token_))
        if expected_payload is not None:
            assert payload.model_dump() == expected_payload


@pytest.mark.asyncio
async def test_get_jwt_missing_credentials():
    with pytest.raises(HTTPException) as exc_info:
        await get_jwt(SecurityScopes(["user"]), None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


@pytest.mark.asyncio
async def test_camera_id():
    payload = await get_jwt(
        SecurityScopes(["camera"]),
        _creds(create_access_token({"sub": "7", "scopes": ["camera"], "organization_id": 1})),
    )
    assert payload.camera_id == 7
    user_payload = await get_jwt(
        SecurityScopes(["user"]), _creds(pytest.make_keycloak_token(roles=["viewer"], organization_id=1))
    )
    with pytest.raises(ValueError, match="camera tokens"):
        _ = user_payload.camera_id


@pytest.mark.parametrize(
    ("roles", "required", "expected_scopes"),
    [
        (["viewer"], ["user"], ["user"]),
        (["operator"], ["agent"], ["agent"]),
        (["admin"], ["admin"], ["admin"]),
        (["offline_access", "default-roles-pyronear", "operator"], ["agent"], ["agent"]),
        (["operator", "viewer"], ["user"], ["agent", "user"]),
    ],
)
@pytest.mark.asyncio
async def test_get_jwt_keycloak(roles, required, expected_scopes):
    token = pytest.make_keycloak_token(roles=roles, organization_id=2, sub="aa6ec0f1-bbbb-426e-b4fb-414b1c114fd1")
    payload = await get_jwt(SecurityScopes(required), _creds(token))
    assert payload.model_dump() == {
        "sub": "aa6ec0f1-bbbb-426e-b4fb-414b1c114fd1",
        "scopes": expected_scopes,
        "organization_id": 2,
        "auth_source": "keycloak",
    }


def _hs256_signed_with_realm_public_key() -> str:
    public_pem = pytest.keycloak_private_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64(json.dumps({"sub": "1", "scopes": ["admin"], "organization_id": 1}).encode())
    signature = _b64(hmac.new(public_pem, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


@pytest.mark.parametrize(
    ("token_factory", "error_code", "detail"),
    [
        (lambda: pytest.make_keycloak_token(expires_in=-120), 401, "Token has expired."),
        (lambda: pytest.make_keycloak_token(iss="http://evil.test/realms/pyronear"), 401, "Invalid token."),
        (lambda: pytest.make_keycloak_token(aud="account"), 401, "Invalid token."),
        (lambda: pytest.make_keycloak_token(headers={"kid": "rotated-away"}), 401, "Invalid token."),
        (
            lambda: pytest.make_keycloak_token(
                signing_key=rsa.generate_private_key(public_exponent=65537, key_size=2048)
            ),
            401,
            "Invalid token.",
        ),
        (lambda: pytest.make_keycloak_token(sub=None), 401, "Invalid token."),
        (lambda: pytest.make_keycloak_token(organization_id=None), 401, "Invalid token payload."),
        (lambda: pytest.make_keycloak_token(organization_id="not-an-org"), 401, "Invalid token payload."),
        (lambda: pytest.make_keycloak_token(organization_id=0), 401, "Invalid token payload."),
        (
            lambda: jwt.encode(
                {"sub": "1", "roles": ["admin"], "organization_id": 1, "iss": pytest.keycloak_issuer},
                None,
                algorithm="none",
            ),
            401,
            "Invalid token.",
        ),
        (_hs256_signed_with_realm_public_key, 401, "Invalid token."),
        (lambda: pytest.make_keycloak_token(roles=["offline_access", "camera"]), 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_get_jwt_keycloak_rejected(token_factory, error_code, detail):
    with pytest.raises(HTTPException) as exc_info:
        await get_jwt(SecurityScopes(["admin", "agent", "user", "camera"]), _creds(token_factory()))
    assert exc_info.value.status_code == error_code
    assert exc_info.value.detail == detail


@pytest.mark.asyncio
async def test_get_jwt_keycloak_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "KEYCLOAK_ISSUER", None)
    with pytest.raises(HTTPException) as exc_info:
        await get_jwt(SecurityScopes(["user"]), _creds(pytest.make_keycloak_token()))
    assert exc_info.value.status_code == 401


@pytest.mark.parametrize(
    "fetch_error",
    [
        jwt.PyJWKClientConnectionError("Fail to fetch data from the url"),
        json.JSONDecodeError("Expecting value", "<html>", 0),
    ],
)
@pytest.mark.asyncio
async def test_get_jwt_keycloak_unreachable(monkeypatch, fetch_error):
    calls = []

    class UnreachableJWKSClient:
        def get_signing_key(self, kid):
            calls.append(kid)
            raise fetch_error

    monkeypatch.setattr(keycloak, "get_jwks_client", UnreachableJWKSClient)
    for _ in range(3):
        with pytest.raises(HTTPException) as exc_info:
            await get_jwt(SecurityScopes(["user"]), _creds(pytest.make_keycloak_token()))
        assert exc_info.value.status_code == 503
    assert len(calls) == 1
    camera_token = create_access_token({"sub": "1", "scopes": ["camera"], "organization_id": 1})
    assert (await get_jwt(SecurityScopes(["camera"]), _creds(camera_token))).camera_id == 1


@pytest.mark.asyncio
async def test_get_jwt_keycloak_backoff_expires(monkeypatch):
    class FlakyJWKSClient:
        fail = True

        def get_signing_key(self, kid):
            if FlakyJWKSClient.fail:
                raise jwt.PyJWKClientConnectionError("Fail to fetch data from the url")
            return pytest.StaticJWKSClient().get_signing_key(kid)

    clock = [1000.0]
    monkeypatch.setattr(keycloak.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(keycloak, "get_jwks_client", FlakyJWKSClient)
    with pytest.raises(HTTPException):
        await get_jwt(SecurityScopes(["user"]), _creds(pytest.make_keycloak_token()))
    FlakyJWKSClient.fail = False
    with pytest.raises(HTTPException):
        await get_jwt(SecurityScopes(["user"]), _creds(pytest.make_keycloak_token()))
    clock[0] += keycloak.KEYCLOAK_FAILURE_BACKOFF_SECONDS + 1
    assert (await get_jwt(SecurityScopes(["user"]), _creds(pytest.make_keycloak_token()))).auth_source == "keycloak"


@pytest.mark.asyncio
async def test_malformed_token_does_not_trip_backoff():
    with pytest.raises(HTTPException) as exc_info:
        await get_jwt(SecurityScopes(["user"]), _creds("eyJhbGciOiJSUzI1NiJ9.!!!.sig"))
    assert exc_info.value.status_code == 401
    assert keycloak.time.monotonic() >= keycloak._unavailable_until


@pytest.mark.parametrize(
    ("roles", "expected"),
    [
        (["admin", "operator", "viewer"], [Role.ADMIN, Role.AGENT, Role.USER]),
        (["offline_access", "uma_authorization", "default-roles-pyronear"], []),
        (["camera", "agent", "user"], []),
        ("admin", []),
        (None, []),
        ([1, None, "viewer"], [Role.USER]),
    ],
)
def test_map_keycloak_roles(roles, expected):
    assert map_keycloak_roles(roles) == expected


@pytest.mark.asyncio
async def test_keycloak_token_is_introspected(keycloak_realm):
    token = pytest.make_keycloak_token(roles=["viewer"], organization_id=2)
    payload = await get_jwt(SecurityScopes(["user"]), _creds(token))
    assert payload.auth_source == "keycloak"
    assert len(keycloak_realm.calls) == 1
    assert keycloak_realm.calls[0]["token"] == token
    assert keycloak_realm.calls[0]["token_type_hint"] == "access_token"  # ruff:ignore[hardcoded-password-string]


@pytest.mark.asyncio
async def test_revoked_keycloak_token_is_rejected(keycloak_realm):
    token = pytest.make_keycloak_token()
    assert (await get_jwt(SecurityScopes(["user"]), _creds(token))).auth_source == "keycloak"
    keycloak_realm.revoked.add(token)
    with pytest.raises(HTTPException) as exc_info:
        await get_jwt(SecurityScopes(["user"]), _creds(token))
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token is no longer active."


@pytest.mark.parametrize(
    "token_factory",
    [
        lambda: pytest.make_keycloak_token(expires_in=-120),
        lambda: pytest.make_keycloak_token(aud="account"),
        lambda: pytest.make_keycloak_token(headers={"kid": "rotated-away"}),
        lambda: pytest.make_keycloak_token(organization_id=None),
    ],
)
@pytest.mark.asyncio
async def test_locally_rejected_tokens_skip_introspection(keycloak_realm, token_factory):
    with pytest.raises(HTTPException) as exc_info:
        await get_jwt(SecurityScopes(["user"]), _creds(token_factory()))
    assert exc_info.value.status_code == 401
    assert keycloak_realm.calls == []


@pytest.mark.asyncio
async def test_api_tokens_skip_introspection(keycloak_realm):
    camera_token = create_access_token({"sub": "1", "scopes": ["camera"], "organization_id": 1})
    assert (await get_jwt(SecurityScopes(["camera"]), _creds(camera_token))).camera_id == 1
    assert keycloak_realm.calls == []


def _raise_connect_error(request):
    raise httpx.ConnectError("Connection refused", request=request)


@pytest.mark.parametrize(
    "handler",
    [
        _raise_connect_error,
        lambda _request: httpx.Response(401, json={"error": "invalid_client"}),
        lambda _request: httpx.Response(502, text="Bad Gateway"),
        lambda _request: httpx.Response(200, text="<html>maintenance</html>"),
        lambda _request: httpx.Response(200, json=["not", "an", "object"]),
    ],
)
@pytest.mark.asyncio
async def test_introspection_failure_is_unavailable(monkeypatch, handler):
    calls = []

    def counting_handler(request):
        calls.append(request)
        return handler(request)

    monkeypatch.setattr(keycloak, "_http_transport", httpx.MockTransport(counting_handler))
    for _ in range(3):
        with pytest.raises(HTTPException) as exc_info:
            await get_jwt(SecurityScopes(["user"]), _creds(pytest.make_keycloak_token()))
        assert exc_info.value.status_code == 503
    assert len(calls) == 1
    camera_token = create_access_token({"sub": "1", "scopes": ["camera"], "organization_id": 1})
    assert (await get_jwt(SecurityScopes(["camera"]), _creds(camera_token))).camera_id == 1
