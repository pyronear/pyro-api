# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
import time
from typing import Any, Dict, List, Union

import httpx
import jwt
from jwt import PyJWK, PyJWKClient, PyJWKClientError, PyJWKSetError
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.models import Role

__all__ = [
    "KEYCLOAK_ROLE_MAPPING",
    "KeycloakUnavailableError",
    "close_http_client",
    "decode_keycloak_token",
    "introspect_keycloak_token",
    "map_keycloak_roles",
]

KEYCLOAK_TIMEOUT_SECONDS = 5
KEYCLOAK_FAILURE_BACKOFF_SECONDS = 10

KEYCLOAK_ROLE_MAPPING: Dict[str, Role] = {
    "admin": Role.ADMIN,
    "operator": Role.AGENT,
    "viewer": Role.USER,
}


class KeycloakUnavailableError(Exception):
    """Keycloak couldn't be reached or answered unexpectedly, so the token's validity is unknown."""


_unavailable_until = 0.0


def _check_backoff() -> None:
    if time.monotonic() < _unavailable_until:
        raise KeycloakUnavailableError("Keycloak unavailable, retrying shortly")


def _start_backoff() -> None:
    global _unavailable_until
    _unavailable_until = time.monotonic() + KEYCLOAK_FAILURE_BACKOFF_SECONDS


class _RealmJWKSClient(PyJWKClient):
    """Tells a Keycloak outage apart from an invalid token.

    PyJWT reports a malformed key set with the same exceptions as an unknown `kid`, and lets socket errors
    raised while reading the response escape. Fetching the key set never involves the token, so every
    failure here means Keycloak answered badly; an unknown `kid` is raised afterwards and stays a PyJWKClientError.
    """

    def get_signing_keys(self, refresh: bool = False) -> List[PyJWK]:
        try:
            return super().get_signing_keys(refresh)
        except (PyJWKClientError, PyJWKSetError, OSError, ValueError) as e:
            raise KeycloakUnavailableError(f"Unable to fetch the Keycloak signing keys: {e}") from e


_jwks_client: Union[PyJWKClient, None] = None


def get_jwks_client() -> PyJWKClient:
    """Realm signing keys, cached for JWKS_CACHE_SECONDS.

    An unknown `kid` triggers a refetch (key rotation), at most once per PyJWT's 30s cooldown.
    """
    global _jwks_client
    if _jwks_client is None:
        if settings.keycloak_jwks_url is None:
            raise RuntimeError("KEYCLOAK_ISSUER is not configured")
        _jwks_client = _RealmJWKSClient(
            settings.keycloak_jwks_url,
            cache_jwk_set=True,
            lifespan=settings.JWKS_CACHE_SECONDS,
            timeout=KEYCLOAK_TIMEOUT_SECONDS,
        )
    return _jwks_client


_fetch_lock = asyncio.Lock()


async def _get_signing_key(token: str) -> PyJWK:
    """PyJWKClient fetches under its own lock with no failure backoff, so during a Keycloak outage every
    RS256 request would queue for a 5s timeout. They queue on an asyncio lock instead, so waiting requests
    don't hold the threadpool that camera requests share; only the request fetching uses a thread.
    The backoff is checked after acquiring the lock, so requests queued behind a failed fetch fail fast too.
    """
    kid = jwt.get_unverified_header(token).get("kid")
    if not isinstance(kid, str):
        raise jwt.InvalidTokenError("Token has no key id")
    client = get_jwks_client()
    async with _fetch_lock:
        _check_backoff()
        try:
            return await run_in_threadpool(client.get_signing_key, kid)  # ty: ignore[invalid-argument-type]
        except KeycloakUnavailableError:
            _start_backoff()
            raise


async def decode_keycloak_token(token: str) -> Dict[str, Any]:
    """Verify a Keycloak access token's signature and claims locally, without asking Keycloak.

    The first call, and the hourly key refresh, fetch the realm keys over the network.

    Raises:
        KeycloakUnavailableError: the realm signing keys could not be fetched
        jwt.PyJWTError: the token is invalid or expired
    """
    signing_key = await _get_signing_key(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.KEYCLOAK_CLIENT_ID,
        issuer=settings.KEYCLOAK_ISSUER,
        leeway=settings.JWT_LEEWAY_SECONDS,
        options={"require": ["exp", "iat", "iss", "aud", "sub"]},
    )


_http_client: Union[httpx.AsyncClient, None] = None


def _get_http_client() -> httpx.AsyncClient:
    """One client per process, so introspection reuses its connections to Keycloak."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=KEYCLOAK_TIMEOUT_SECONDS)
    return _http_client


async def close_http_client() -> None:
    """Close the introspection client on shutdown."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


async def introspect_keycloak_token(token: str) -> bool:
    """Ask Keycloak whether the token is still active.

    Keycloak answers inactive as soon as the session is revoked, the user is disabled or logs out, even if the
    token is not expired yet. Called on every request, after the local checks have passed.

    Raises:
        KeycloakUnavailableError: Keycloak could not answer
    """
    if settings.keycloak_introspection_url is None or settings.KEYCLOAK_CLIENT_SECRET is None:
        raise RuntimeError("KEYCLOAK_ISSUER and KEYCLOAK_CLIENT_SECRET are not configured")
    _check_backoff()
    try:
        response = await _get_http_client().post(
            settings.keycloak_introspection_url,
            data={
                "token": token,
                "token_type_hint": "access_token",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("introspection response is not a JSON object")
    except (httpx.HTTPError, ValueError) as e:
        _start_backoff()
        raise KeycloakUnavailableError(f"Token introspection failed: {e}") from e
    return payload.get("active") is True


def map_keycloak_roles(roles: object) -> List[Role]:
    """Translate the `roles` claim into API roles, ignoring Keycloak built-ins (offline_access, ...)."""
    if not isinstance(roles, list):
        return []
    return [KEYCLOAK_ROLE_MAPPING[role] for role in roles if isinstance(role, str) and role in KEYCLOAK_ROLE_MAPPING]
