# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from fastapi import APIRouter, Depends, Path, Security, status

from app.api import crud
from app.api.crud.authorizations import is_admin_access
from app.api.deps import get_current_access, get_current_user, get_db
from app.db import accesses, users
from app.models import Access, AccessType, User
from app.schemas import Cred, Login, UserAuth, UserCreation, UserRead
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.get("/me", response_model=UserRead, summary="Get information about the current user")
async def get_my_user(me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])):
    """
    Retrieves information about the current user
    """
    telemetry_client.capture(me.id, event="users-get-me")
    return me


@router.put("/update-info", response_model=UserRead, summary="Update information of the current user")
async def update_my_info(
    payload: Login, me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])
):
    """
    Updates information of the current user
    """
    telemetry_client.capture(me.id, event="users-update-my-info")
    return await crud.accesses.update_accessed_entry(users, accesses, me.id, payload)


@router.put("/update-pwd", response_model=Login, summary="Update password of the current user")
async def update_my_password(
    payload: Cred, me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])
):
    """
    Updates the password of the current user
    """
    telemetry_client.capture(me.id, event="users-update-my-pwd")
    entry = await crud.get_entry(users, me.id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create a new user")
async def create_user(payload: UserAuth, access=Security(get_current_user, scopes=[AccessType.admin])):
    """
    Creates a new user based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    telemetry_client.capture(access.id, event="users-create")
    return await crud.accesses.create_accessed_entry(users, accesses, payload, UserCreation)


@router.get("/{user_id}/", response_model=UserRead, summary="Get information about a specific user")
async def get_user(user_id: int = Path(..., gt=0), access=Security(get_current_user, scopes=[AccessType.admin])):
    """
    Based on a user_id, retrieves information about the specified user
    """
    telemetry_client.capture(access.id, event="users-get", properties={"user_id": user_id})
    return await crud.get_entry(users, user_id)


@router.get("/", response_model=List[UserRead], summary="Get the list of all users")
async def fetch_users(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all users and their information
    """
    telemetry_client.capture(requester.id, event="users-fetch")
    if await is_admin_access(requester.id):
        return await crud.fetch_all(users)
    else:
        retrieved_users = session.query(User).join(Access).filter(Access.group_id == requester.group_id).all()
        retrieved_users = [x.__dict__ for x in retrieved_users]
        return retrieved_users


@router.put("/{user_id}/", response_model=UserRead, summary="Update information about a specific user")
async def update_user_login(
    payload: Login, user_id: int = Path(..., gt=0), access=Security(get_current_user, scopes=[AccessType.admin])
):
    """
    Based on a user_id, updates information about the specified user
    """
    telemetry_client.capture(access.id, event="users-update-login", properties={"user_id": user_id})
    return await crud.accesses.update_accessed_entry(users, accesses, user_id, payload)


@router.put("/{user_id}/pwd", response_model=UserRead, summary="Update the password of a specific user")
async def update_user_password(
    payload: Cred, user_id: int = Path(..., gt=0), access=Security(get_current_user, scopes=[AccessType.admin])
):
    """
    Based on a user_id, updates the password of the specified user
    """
    telemetry_client.capture(access.id, event="users-update-pwd", properties={"user_id": user_id})
    entry = await crud.get_entry(users, user_id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry


@router.delete("/{user_id}/", response_model=UserRead, summary="Delete a specific user")
async def delete_user(user_id: int = Path(..., gt=0), access=Security(get_current_user, scopes=[AccessType.admin])):
    """
    Based on a user_id, deletes the specified user
    """
    telemetry_client.capture(access.id, event="users-delete", properties={"user_id": user_id})
    # TODO: Doesn't work when there is a owned device
    # It will yield an exception if the deleted user is the owner_id field of one device.
    return await crud.accesses.delete_accessed_entry(users, accesses, user_id)
