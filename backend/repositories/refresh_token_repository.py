import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """
    Repository handling all database operations for refresh tokens.

    Provides stateful tracking of issued refresh tokens: storage, lookup,
    revocation (single token or all tokens for a user), and validity checks.
    Concurrency-safe rotation is supported via row-level locking
    (SELECT ... FOR UPDATE).
    """

    def __init__(self, db: Session):
        self.db = db

    def store(
        self,
        user_id: uuid.UUID,
        jti: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """
        Persist a newly issued refresh token.

        The caller is responsible for committing the transaction.
        """
        now = datetime.now(timezone.utc)
        token = RefreshToken(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
            revoked_at=None,
        )
        self.db.add(token)
        try:
            self.db.flush()
            self.db.refresh(token)
            return token
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        """Fetch a refresh token by its JTI without locking."""
        return self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

    def get_by_jti_for_update(self, jti: str) -> Optional[RefreshToken]:
        """
        Fetch a refresh token by JTI with a row-level lock.

        Uses SELECT ... FOR UPDATE so concurrent refresh requests using the
        same token serialize: only the first request proceeds; subsequent
        requests find the token already revoked and are rejected.
        """
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.jti == jti)
            .with_for_update()
            .first()
        )

    def revoke_by_jti(self, jti: str) -> bool:
        """
        Revoke a single refresh token by JTI.

        Sets revoked_at to the current time if the token exists and is not
        already revoked. Returns True if a row was revoked, False otherwise.
        Idempotent: revoking an already-revoked token returns False but is
        not an error.
        """
        now = datetime.now(timezone.utc)
        result = self.db.query(RefreshToken).filter(
            RefreshToken.jti == jti,
            RefreshToken.revoked_at.is_(None),
        ).update({RefreshToken.revoked_at: now}, synchronize_session=False)
        try:
            self.db.flush()
            return result > 0
        except Exception as e:
            self.db.rollback()
            raise e

    def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        """
        Revoke all active (unrevoked) refresh tokens for a user.

        Returns the number of tokens revoked. Used on password change and
        refresh-token reuse detection to force re-authentication across all
        devices.
        """
        now = datetime.now(timezone.utc)
        result = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        ).update({RefreshToken.revoked_at: now}, synchronize_session=False)
        try:
            self.db.flush()
            return result
        except Exception as e:
            self.db.rollback()
            raise e

    def is_valid(self, jti: str, now: Optional[datetime] = None) -> bool:
        """
        Return True if a refresh token exists, is not revoked, and is not expired.

        Used for lightweight validity checks without mutating state.
        """
        check = now or datetime.now(timezone.utc)
        token = self.get_by_jti(jti)
        if token is None:
            return False
        if token.is_revoked:
            return False
        if token.is_expired(now=check):
            return False
        return True

    def cleanup_expired(self) -> int:
        """
        Mark expired (but not yet revoked) tokens as revoked.

        Optional housekeeping. Returns the number of tokens marked revoked.
        """
        now = datetime.now(timezone.utc)
        result = self.db.query(RefreshToken).filter(
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at <= now,
        ).update({RefreshToken.revoked_at: now}, synchronize_session=False)
        try:
            self.db.flush()
            return result
        except Exception as e:
            self.db.rollback()
            raise e
