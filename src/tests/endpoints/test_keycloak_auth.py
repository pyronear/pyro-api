from typing import Dict, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


def _camera_auth(cam_idx: int) -> Dict[str, str]:
    return pytest.get_token(
        pytest.camera_table[cam_idx]["id"], ["camera"], pytest.camera_table[cam_idx]["organization_id"]
    )


@pytest.mark.parametrize(
    ("roles", "organization_id", "expected_scopes"),
    [
        (["viewer"], 2, ["user"]),
        (["operator", "offline_access"], 1, ["agent"]),
        (["admin"], 1, ["admin"]),
    ],
)
@pytest.mark.asyncio
async def test_validate_keycloak_token(async_client: AsyncClient, roles, organization_id, expected_scopes):
    auth = pytest.get_keycloak_token(roles, organization_id, sub="aa6ec0f1-bbbb-426e-b4fb-414b1c114fd1")
    response = await async_client.get("/login/validate", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert response.json() == {
        "sub": "aa6ec0f1-bbbb-426e-b4fb-414b1c114fd1",
        "scopes": expected_scopes,
        "organization_id": organization_id,
        "auth_source": "keycloak",
    }


@pytest.mark.parametrize(
    ("roles", "organization_id", "status_code"),
    [
        (["viewer"], 1, 200),
        (["viewer"], 2, 403),
        (["admin"], 2, 200),
        (["offline_access"], 1, 403),
    ],
)
@pytest.mark.asyncio
async def test_get_camera_with_keycloak_token(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    roles,
    organization_id: int,
    status_code: int,
):
    response = await async_client.get("/cameras/1", headers=pytest.get_keycloak_token(roles, organization_id))
    assert response.status_code == status_code, print(response.__dict__)
    if status_code == 200:
        assert response.json()["id"] == 1


@pytest.mark.parametrize(
    ("auth_kind", "roles", "organization_id", "payload", "status_code"),
    [
        ("keycloak", ["operator"], 1, {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1}, 201),
        ("keycloak", ["operator"], 2, {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1}, 403),
        ("keycloak", ["viewer"], 1, {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1}, 403),
        ("keycloak", ["admin"], 2, {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1}, 201),
        ("camera", None, None, {"camera_id": 1, "azimuth": 90.0, "patrol_id": 2}, 201),
        ("camera", None, None, {"camera_id": 2, "azimuth": 90.0, "patrol_id": 2}, 403),
    ],
)
@pytest.mark.asyncio
async def test_create_pose_accepts_both_auths(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    auth_kind: str,
    roles,
    organization_id: Union[int, None],
    payload,
    status_code: int,
):
    auth = pytest.get_keycloak_token(roles, organization_id) if auth_kind == "keycloak" else _camera_auth(0)
    response = await async_client.post("/poses/", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if status_code == 201:
        assert response.json()["camera_id"] == payload["camera_id"]


@pytest.mark.asyncio
async def test_legacy_user_tokens_disabled(async_client: AsyncClient, camera_session: AsyncSession, monkeypatch):
    monkeypatch.setattr(settings, "LEGACY_USER_TOKENS_ENABLED", False)
    legacy_user_auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    response = await async_client.get("/cameras/1", headers=legacy_user_auth)
    assert response.status_code == 401
    response = await async_client.patch("/cameras/heartbeat", headers=_camera_auth(0))
    assert response.status_code == 200, print(response.__dict__)
    response = await async_client.get("/cameras/1", headers=pytest.get_keycloak_token(["viewer"], 1))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_revoked_session_is_rejected_on_next_request(
    async_client: AsyncClient, camera_session: AsyncSession, keycloak_realm
):
    token = pytest.make_keycloak_token(["viewer"], 1)
    auth = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/cameras/1", headers=auth)
    assert response.status_code == 200
    keycloak_realm.revoked.add(token)
    response = await async_client.get("/cameras/1", headers=auth)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token is no longer active."
