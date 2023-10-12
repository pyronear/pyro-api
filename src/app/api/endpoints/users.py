# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, Security, status
from typing_extensions import Annotated

from app.api import crud
from app.api.crud.authorizations import is_admin_access
from app.api.deps import get_current_access, get_current_user, get_db
from app.db import accesses, users
from app.models import Access, AccessType, User
from app.schemas import Cred, Login, UserAuth, UserCreation, UserRead

router = APIRouter()


@router.get("/me", response_model=UserRead, summary="Get information about the current user")
async def get_my_user(me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])):
    """
    Retrieves information about the current user
    """
    return me


@router.put("/update-info", response_model=UserRead, summary="Update information of the current user")
async def update_my_info(
    payload: Login, me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])
):
    """
    Updates information of the current user
    """
    return await crud.accesses.update_accessed_entry(users, accesses, me.id, payload)


@router.put("/update-pwd", response_model=Login, summary="Update password of the current user")
async def update_my_password(
    payload: Cred, me: UserRead = Security(get_current_user, scopes=[AccessType.admin, AccessType.user])
):
    """
    Updates the password of the current user
    """
    entry = await crud.get_entry(users, me.id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create a new user")
async def create_user(payload: UserAuth, _=Security(get_current_user, scopes=[AccessType.admin])):
    """
    Creates a new user based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.accesses.create_accessed_entry(users, accesses, payload, UserCreation)


@router.get("/{user_id}/", response_model=UserRead, summary="Get information about a specific user")
async def get_user(user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=[AccessType.admin])):
    """
    Based on a user_id, retrieves information about the specified user
    """
    return await crud.get_entry(users, user_id)


@router.get("/", response_model=List[UserRead], summary="Get the list of all users")
async def fetch_users(
    limit: Annotated[int, Query(description="maximum number of items", ge=1, le=1000)] = 50,
    offset: Annotated[Optional[int], Query(description="number of items to skip", ge=0)] = None,
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
    session=Depends(get_db),
):
    """
    Retrieves the list of all users and their information
    """
    return await crud.fetch_all(
        users,
        query=None
        if await is_admin_access(requester.id)
        else session.query(User).join(Access).filter(Access.group_id == requester.group_id),
        limit=limit,
        offset=offset,
    )


@router.put("/{user_id}/", response_model=UserRead, summary="Update information about a specific user")
async def update_user_login(
    payload: Login, user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=[AccessType.admin])
):
    """
    Based on a user_id, updates information about the specified user
    """
    return await crud.accesses.update_accessed_entry(users, accesses, user_id, payload)


@router.put("/{user_id}/pwd", response_model=UserRead, summary="Update the password of a specific user")
async def update_user_password(
    payload: Cred, user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=[AccessType.admin])
):
    """
    Based on a user_id, updates the password of the specified user
    """
    entry = await crud.get_entry(users, user_id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry


@router.delete("/{user_id}/", response_model=UserRead, summary="Delete a specific user")
async def delete_user(user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=[AccessType.admin])):
    """
    Based on a user_id, deletes the specified user
    """
    # TODO: Doesn't work when there is a owned device
    # It will yield an exception if the deleted user is the owner_id field of one device.
    return await crud.accesses.delete_accessed_entry(users, accesses, user_id)
