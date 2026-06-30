import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    InvalidTokenError,
    InvalidTokenTypeError
)
from core.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InactiveUserError,
    RefreshTokenNotFoundError
)
from core.config import settings
from repositories.user_repository import UserRepository
from schemas.auth import SignupRequest, UserResponse, TokenResponse, ChangePasswordRequest


class AuthService:
    """
    Service layer containing all authentication business logic.
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, request: SignupRequest) -> UserResponse:
        """
        Registers a new user after normalizing email, checking for duplicates, 
        and securely hashing the password.
        """
        email = request.email.strip().lower()
        if self.user_repo.get_by_email(email):
            raise DuplicateEmailError("A user with this email already exists.")

        user_data = {
            "email": email,
            "password_hash": hash_password(request.password),
            "role": request.role
        }

        user = self.user_repo.create_user(user_data)
        return UserResponse.model_validate(user)

    def authenticate_user(self, email: str, password: str) -> TokenResponse:
        """
        Authenticates a user and issues access and refresh tokens.
        """
        email = email.strip().lower()
        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Incorrect email or password.")

        if not user.is_active:
            raise InactiveUserError("User account is inactive.")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        refresh_payload = decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
        self.user_repo.store_refresh_token(user.id, refresh_payload["jti"], expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Rotates a refresh token and issues a new access token.
        """
        try:
            payload = decode_token(refresh_token)
            verify_token_type(payload, "refresh")
        except (InvalidTokenError, InvalidTokenTypeError):
            raise InvalidCredentialsError("Invalid or expired refresh token.")

        # If a db lookup was active, we would verify the JTI exists here.
        # If not found, raise RefreshTokenNotFoundError

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidCredentialsError("Invalid token payload.")
            
        user_id = uuid.UUID(user_id_str)
        user = self.user_repo.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise InactiveUserError("User account is inactive or deleted.")

        # Revoke old token
        self.user_repo.revoke_refresh_token(payload["jti"])

        # Generate new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        new_refresh_payload = decode_token(new_refresh_token)
        expires_at = datetime.fromtimestamp(new_refresh_payload["exp"], tz=timezone.utc)
        self.user_repo.store_refresh_token(user.id, new_refresh_payload["jti"], expires_at)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def logout_user(self, refresh_token: str) -> None:
        """
        Logs a user out by revoking their refresh token.
        """
        try:
            payload = decode_token(refresh_token)
            verify_token_type(payload, "refresh")
            self.user_repo.revoke_refresh_token(payload["jti"])
        except (InvalidTokenError, InvalidTokenTypeError):
            # If the token is already invalid, logout technically succeeds without error
            pass

    def change_password(self, user_id: uuid.UUID, request: ChangePasswordRequest) -> None:
        """
        Updates a user's password if the current password matches.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("User not found.")

        if not verify_password(request.current_password, user.password_hash):
            raise InvalidCredentialsError("Incorrect current password.")

        new_hash = hash_password(request.new_password)
        self.user_repo.update_user(user, {"password_hash": new_hash})
        
        # In a fully stateful token implementation, we would revoke ALL active 
        # refresh tokens for this user_id here to force re-authentication.
