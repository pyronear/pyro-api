# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_jwt
from app.core.security import hash_password
from app.crud import UserCRUD
from app.db import get_session
from app.models import User, UserRole
from app.schemas.login import TokenPayload
from app.schemas.users import Cred, CredHash, UserCreate
from app.services.telemetry import telemetry_client

router = APIRouter()


async def _create_user(payload: UserCreate, session: AsyncSession, requester_id: int | None = None) -> User:
    # Check for unicity
    if (await UserCRUD(session=session).get_by_login(payload.login, strict=False)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Login already taken")

    # Create the entry
    user = await UserCRUD(session=session).create(
        User(
            login=payload.login,
            organization_id=payload.organization_id,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
    )

    # Enrich user data
    telemetry_client.alias(user.id, payload.login)

    # Assume the requester is the new user if none was specified
    telemetry_client.capture(
        requester_id if isinstance(requester_id, int) else user.id,
        event="user-creation",
        properties={"created_user_id": user.id},
    )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def create_user(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> User:
    return await _create_user(payload, session, token_payload.sub)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific user")
async def get_user(
    user_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> User:
    telemetry_client.capture(token_payload.sub, event="user-get", properties={"user_id": user_id})
    return cast(User, await UserCRUD(session=session).get(user_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the users")
async def fetch_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> list[User]:
    telemetry_client.capture(token_payload.sub, event="user-fetch")
    return [elt for elt in await UserCRUD(session=session).fetch_all()]


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, summary="Updates a user's password")
async def update_user_password(
    payload: Cred,
    user_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> User:
    telemetry_client.capture(token_payload.sub, event="user-pwd", properties={"user_id": user_id})
    pwd = hash_password(payload.password)
    return await UserCRUD(session=session).update(user_id, CredHash(hashed_password=pwd))


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, summary="Delete a user")
async def delete_user(
    user_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> None:
    telemetry_client.capture(token_payload.sub, event="user-deletion", properties={"user_id": user_id})
    await UserCRUD(session=session).delete(user_id)
