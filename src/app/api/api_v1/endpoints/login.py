# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_jwt, get_user_crud
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud import UserCRUD
from app.models import Role
from app.schemas.login import Token, TokenPayload
from app.services.telemetry import telemetry_client

router = APIRouter(redirect_slashes=True)


@router.post("/creds", status_code=status.HTTP_200_OK, summary="Request an access token using credentials")
async def login_with_creds(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users: UserCRUD = Depends(get_user_crud),
) -> Token:
    """This API follows the OAuth 2.0 specification.

    If the credentials are valid, creates a new access token.

    By default, the token expires after 1 year.
    """
    # Verify credentials
    user = await users.get_by_login(form_data.username)
    if user is None or user.hashed_password is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    telemetry_client.capture(user.id, event="user-login", properties={"method": "credentials"})
    # create access token using user user_id/user_scopes
    token_data = {"sub": str(user.id), "scopes": user.role.split(), "organization_id": user.organization_id}
    token = create_access_token(token_data, settings.JWT_UNLIMITED)

    return Token(access_token=token, token_type="bearer")  # noqa S106


@router.get("/validate", status_code=status.HTTP_200_OK, summary="Check token validity")
def check_token_validity(
    payload: TokenPayload = Security(get_jwt, scopes=[Role.USER, Role.CAMERA, Role.AGENT, Role.ADMIN]),
) -> TokenPayload:
    return payload
