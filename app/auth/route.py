from fastapi import APIRouter, status, Depends
from typing import Annotated
from datetime import datetime
from fastapi.responses import JSONResponse


from app.auth.schema import CreateUserModel, TokenModel, UserLoginModel, UserModel, AccessTokenModel, \
    PasswordResetRequestModel, PasswordResetConfirm
from app.db.dependency import SessionDep
from app.auth.service import UserService
from app.auth.denpendency import get_current_user, RefreshTokenBearer, AccessTokenBearer
from app.utility.security import create_access_token
from app.db.redis import add_jti_blocklist

user_service = UserService()
oauth_route = APIRouter()


@oauth_route.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUserModel, session: SessionDep):
    new_user = await user_service.signup_user(user_data, session)
    return {
        "message": "Account created! Check email to verify your email",
        "user": new_user,
    }


@oauth_route.get("/verify/{token}")
async def verify_user_account(token: str, session: SessionDep):
    token_safe_url = await user_service.verify_user_account(token, session)
    return token_safe_url


@oauth_route.post("/login", response_model=TokenModel)
async def user_login(login_data: UserLoginModel, session: SessionDep):
    token_response = await user_service.login_user(login_data, session)
    return token_response

@oauth_route.get("/me", response_model=UserModel)
async def get_current_user(user: Annotated[UserModel, Depends(get_current_user)]):
    return user

@oauth_route.get("/refresh_token", response_model=AccessTokenModel)
async def get_new_access_token(token_details: Annotated[dict, Depends(RefreshTokenBearer())]):
    exp_time = token_details["exp"]

    if datetime.fromtimestamp(exp_time) > datetime.now():
        new_access_token = create_access_token(token_details["user"])
        return AccessTokenModel(access_token=new_access_token)

@oauth_route.get("/logout")
async def revoke_token(token_detail: Annotated[dict, Depends(AccessTokenBearer())]):
    jti = token_detail["jti"]
    await add_jti_blocklist(jti)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Logged out successfully"}
    )

@oauth_route.post("/reset-password-request")
async def password_reset_request(email: PasswordResetRequestModel, session: SessionDep):
    user_to_reset_password = await user_service.password_reset_request(email, session)
    return user_to_reset_password

@oauth_route.post("/reset-password-confirm/{token}")
async def reset_account_password(
    token: str,
    password: PasswordResetConfirm,
    session: SessionDep
):
    user_to_reset_password = await user_service.reset_account_password(token, password, session)
    return user_to_reset_password
