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
    InvalidTokenTypeError,
)
from core.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InactiveUserError,
    RefreshTokenNotFoundError,
)
from core.config import settings
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from schemas.auth import SignupRequest, UserResponse, TokenResponse, ChangePasswordRequest


class AuthService:
    """
    Service layer containing all authentication business logic.

    Refresh tokens are now stateful: every issued refresh token is persisted
    with its JTI, expiry, and revocation timestamp. Rotation revokes the old
    token and issues a new one atomically within a single database
    transaction. Reuse of an already-revoked token triggers revocation of all
    active tokens for that user (forced re-authentication).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        # Both repositories share the same SQLAlchemy Session (injected via
        # get_db in the router), so we can coordinate a single commit across
        # them for atomic operations.
        self.db = user_repo.db

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
            "role": request.role,
        }

        user = self.user_repo.create_user(user_data)
        return UserResponse.model_validate(user)

    def authenticate_user(self, email: str, password: str) -> TokenResponse:
        """
        Authenticates a user and issues access and refresh tokens.

        The same generic error message is returned whether the email does not
        exist or the password is wrong, preventing email enumeration.
        """
        email = email.strip().lower()
        user = self.user_repo.get_by_email(email)

        # Constant-failure shape: always verify the password hash when a user
        # exists so timing does not distinguish "unknown email" from "wrong
        # password". If the user is missing, we still return the same error.
        if user is not None:
            password_valid = verify_password(password, user.password_hash)
        else:
            password_valid = False

        if not user or not password_valid:
            raise InvalidCredentialsError("Incorrect email or password.")

        if not user.is_active:
            raise InactiveUserError("User account is inactive.")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        refresh_payload = decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(
            refresh_payload["exp"], tz=timezone.utc
        )
        self.refresh_token_repo.store(user.id, refresh_payload["jti"], expires_at)
        self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Rotates a refresh token and issues a new access token.

        The refresh token row is locked with SELECT ... FOR UPDATE so
        concurrent requests using the same token serialize. The old token is
        revoked and the new token stored in a single transaction. If the
        presented token is already revoked (reuse), all active tokens for
        that user are revoked and the request is rejected.
        """
        try:
            payload = decode_token(refresh_token)
            verify_token_type(payload, "refresh")
        except (InvalidTokenError, InvalidTokenTypeError):
            raise InvalidCredentialsError("Invalid or expired refresh token.")

        jti = payload.get("jti")
        user_id_str = payload.get("sub")
        if not jti or not user_id_str:
            raise InvalidCredentialsError("Invalid token payload.")

        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, AttributeError):
            raise InvalidCredentialsError("Invalid token payload.")

        # Lock the token row for the duration of this transaction so
        # concurrent rotation attempts serialize.
        token = self.refresh_token_repo.get_by_jti_for_update(jti)

        if token is None:
            # Unknown JTI: cannot determine the user, reject outright.
            raise RefreshTokenNotFoundError("Refresh token not found or revoked.")

        # Reuse detection: token already revoked or expired.
        if token.is_revoked or token.is_expired():
            # Force re-authentication across all devices by revoking every
            # remaining active token for this user.
            self.refresh_token_repo.revoke_all_for_user(token.user_id)
            self.db.commit()
            raise RefreshTokenNotFoundError("Refresh token not found or revoked.")

        # Valid token: atomically revoke the old token and store the new one.
        now = datetime.now(timezone.utc)
        token.revoked_at = now

        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        new_refresh_payload = decode_token(new_refresh_token)
        new_expires_at = datetime.fromtimestamp(
            new_refresh_payload["exp"], tz=timezone.utc
        )
        self.refresh_token_repo.store(
            user_id, new_refresh_payload["jti"], new_expires_at
        )

        # Single commit: revoke old + store new are atomic.
        self.db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def logout_user(self, refresh_token: str) -> None:
        """
        Logs a user out by revoking their refresh token.

        Idempotent: if the token is already invalid, expired, or unknown,
        logout still succeeds without error. No information is leaked about
        whether the token existed.
        """
        try:
            payload = decode_token(refresh_token)
            verify_token_type(payload, "refresh")
        except (InvalidTokenError, InvalidTokenTypeError):
            # If the token is already invalid, logout technically succeeds
            # without error. Do not distinguish "unknown token" from "valid
            # token" to avoid leaking state.
            return

        jti = payload.get("jti")
        if jti:
            self.refresh_token_repo.revoke_by_jti(jti)
            self.db.commit()

    def change_password(self, user_id: uuid.UUID, request: ChangePasswordRequest) -> None:
        """
        Updates a user's password if the current password matches.

        Password update and revocation of all active refresh tokens for the
        user happen atomically in a single transaction, forcing re-authentication
        on all devices.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("User not found.")

        if not verify_password(request.current_password, user.password_hash):
            raise InvalidCredentialsError("Incorrect current password.")

        new_hash = hash_password(request.new_password)
        user.password_hash = new_hash

        # Revoke every active refresh token for this user in the same
        # transaction as the password change.
        self.refresh_token_repo.revoke_all_for_user(user_id)
        self.db.commit()
