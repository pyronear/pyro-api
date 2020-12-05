from typing import List

from fastapi import APIRouter, Path, Security

from app.api import crud
from app.db import users, accesses
from app.api.schemas import UserInfo, UserCreation, Cred, UserRead, UserAuth
from app.api.deps import get_current_user


router = APIRouter()


@router.get("/me", response_model=UserRead, summary="Get information about the current user")
async def get_my_user(me: UserRead = Security(get_current_user, scopes=["admin", "me"])):
    """
    Retrieves information about the current user
    """
    return me


@router.put("/update-info", response_model=UserRead, summary="Update information of the current user")
async def update_my_info(payload: UserInfo, me: UserRead = Security(get_current_user, scopes=["admin", "me"])):
    """
    Updates information of the current user
    """
    return await crud.accesses.update_accessed_entry(users, accesses, me.id, payload)


@router.put("/update-pwd", response_model=UserInfo, summary="Update password of the current user")
async def update_my_password(payload: Cred, me: UserRead = Security(get_current_user, scopes=["admin", "me"])):
    """
    Updates the password of the current user
    """
    entry = await crud.get_entry(users, me.id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry


@router.post("/", response_model=UserRead, status_code=201, summary="Create a new user")
async def create_user(payload: UserAuth, _=Security(get_current_user, scopes=["admin"])):
    """
    Creates a new user based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    # Create a new access
    # access_entry = await post_access(payload.login, payload.password, payload.scopes)
    # return await crud.create_entry(users, UserCreation(login=payload.login, access_id=access_entry.id))
    return await crud.accesses.create_accessed_entry(users, accesses, payload, UserCreation)


@router.get("/{user_id}/", response_model=UserRead, summary="Get information about a specific user")
async def get_user(user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    """
    Based on a user_id, retrieves information about the specified user
    """
    return await crud.get_entry(users, user_id)


@router.get("/", response_model=List[UserRead], summary="Get the list of all users")
async def fetch_users(_=Security(get_current_user, scopes=["admin"])):
    """
    Retrieves the list of all users and their information
    """
    return await crud.fetch_all(users)


@router.put("/{user_id}/", response_model=UserRead, summary="Update information about a specific user")
async def update_user(
    payload: UserInfo,
    user_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    """
    Based on a user_id, updates information about the specified user
    """
    # origin_user = await crud.get(user_id, users)
    #
    # # Check for access login
    # if payload.login is not None:
    #     if origin_user is not None and origin_user["login"] != payload.login:
    #         await check_for_access_login_existence(payload.login)
    #         updated_acccess = await crud.fetch_one(accesses, {"login": origin_user["login"]})
    #         await update_access_login(payload.login, updated_acccess["id"])
    #
    # return await crud.update_entry(users, payload, user_id)

    return await crud.accesses.update_accessed_entry(users, accesses, user_id, payload)


@router.put("/{user_id}/pwd", response_model=UserInfo, summary="Update the password of a specific user")
async def update_user_password(
    payload: Cred,
    user_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    """
    Based on a user_id, updates the password of the specified user
    """
    # Check that user does exist
    entry = await crud.get_entry(users, user_id)
    await crud.accesses.update_access_pwd(accesses, payload, entry["access_id"])
    return entry


@router.delete("/{user_id}/", response_model=UserRead, summary="Delete a specific user")
async def delete_user(user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    """
    Based on a user_id, deletes the specified user
    """
    # Delete user entry
    # entry = await crud.delete_entry(users, user_id)
    # # Delete access
    # await crud.delete_entry(accesses, entry['access_id'])
    # return entry
    return await crud.accesses.delete_accessed_entry(users, accesses, user_id)
