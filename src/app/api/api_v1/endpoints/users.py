# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import List, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_jwt, get_user_crud
from app.core.security import hash_password
from app.crud import UserCRUD
from app.models import User, UserRole
from app.schemas.login import TokenPayload
from app.schemas.users import Cred, CredHash, UserCreate
from app.services.telemetry import telemetry_client

router = APIRouter()


async def _create_user(payload: UserCreate, users: UserCRUD, requester_id: Union[int, None] = None) -> User:
    # Check for unicity
    if (await users.get_by_login(payload.login, strict=False)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Login already taken")

    # Create the entry
    user = await users.create(
        User(
            login=payload.login,
            hashed_password=hash_password(payload.password),
            scope=payload.scope,
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
    users: UserCRUD = Depends(get_user_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> User:
    return await _create_user(payload, users, token_payload.sub)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific user")
async def get_user(
    user_id: int = Path(..., gt=0),
    users: UserCRUD = Depends(get_user_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> User:
    telemetry_client.capture(token_payload.sub, event="user-get", properties={"user_id": user_id})
    return cast(User, await users.get(user_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the users")
async def fetch_users(
    users: UserCRUD = Depends(get_user_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> List[User]:
    telemetry_client.capture(token_payload.sub, event="user-fetch")
    return [elt for elt in await users.fetch_all()]


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, summary="Updates a user's password")
async def update_user_password(
    payload: Cred,
    user_id: int = Path(..., gt=0),
    users: UserCRUD = Depends(get_user_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> User:
    telemetry_client.capture(token_payload.sub, event="user-pwd", properties={"user_id": user_id})
    pwd = hash_password(payload.password)
    return await users.update(user_id, CredHash(hashed_password=pwd))


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, summary="Delete a user")
async def delete_user(
    user_id: int = Path(..., gt=0),
    users: UserCRUD = Depends(get_user_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="user-deletion", properties={"user_id": user_id})
    await users.delete(user_id)
