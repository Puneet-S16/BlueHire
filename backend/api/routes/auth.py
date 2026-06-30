import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import decode_token, verify_token_type, InvalidTokenError, InvalidTokenTypeError
from core.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InactiveUserError,
    RefreshTokenNotFoundError
)
from db.session import SessionLocal
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ChangePasswordRequest
)
from models.user import User
from core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    try:
        payload = decode_token(token)
        verify_token_type(payload, "access")
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidTokenError()
        user_id = uuid.UUID(user_id_str)
        user = user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise InactiveUserError()
        return user
    except (InvalidTokenError, InvalidTokenTypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new user", tags=["auth"])
def signup(request: SignupRequest, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """
    Register a new user in the system.
    """
    try:
        return auth_service.register_user(request)
    except DuplicateEmailError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists")

@router.post("/login", response_model=TokenResponse, summary="Log in and obtain tokens", tags=["auth"])
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """
    Authenticate a user using email and password to receive access and refresh tokens.
    """
    try:
        return auth_service.authenticate_user(request.email, request.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    except InactiveUserError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token", tags=["auth"])
def refresh(request: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """
    Use a valid refresh token to obtain a new access token and a rotated refresh token.
    """
    try:
        return auth_service.refresh_access_token(request.refresh_token)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    except RefreshTokenNotFoundError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found or revoked")
    except InactiveUserError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

@router.post("/logout", status_code=status.HTTP_200_OK, summary="Log out a user", tags=["auth"])
def logout(request: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """
    Log out a user by revoking their refresh token.
    """
    auth_service.logout_user(request.refresh_token)
    return {"detail": "Successfully logged out"}

@router.post("/change-password", status_code=status.HTTP_200_OK, summary="Change user password", tags=["auth"])
def change_password(
    request: ChangePasswordRequest, 
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    Change the authenticated user's password.
    """
    try:
        auth_service.change_password(current_user.id, request)
        return {"detail": "Password successfully updated"}
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current password")

@router.get("/me", response_model=UserResponse, summary="Get current user", tags=["auth"])
def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Retrieve the profile of the currently authenticated user.
    """
    return current_user
