import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.user import User


class UserRepository:
    """
    Repository handling all database operations for the User domain.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by their unique ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create and persist a new user in the database."""
        db_user = User(**user_data)
        self.db.add(db_user)
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            raise e

    def update_user(self, user: User, update_data: Dict[str, Any]) -> User:
        """Update an existing user's attributes."""
        for field, value in update_data.items():
            setattr(user, field, value)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise e

    def store_refresh_token(self, user_id: uuid.UUID, jti: str, expires_at: datetime) -> None:
        """
        Store a refresh token JTI in the database.
        Note: Bypassed for now as the schema for RefreshToken is not yet implemented.
        """
        pass

    def revoke_refresh_token(self, jti: str) -> None:
        """
        Revoke a specific refresh token by JTI.
        Note: Bypassed for now as the schema for RefreshToken is not yet implemented.
        """
        pass
