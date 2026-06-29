import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin
from .enums import RoleEnum

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true')
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    last_login: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    worker_profile: Mapped[Optional["Worker"]] = relationship("Worker", back_populates="user", uselist=False, cascade="all, delete-orphan")
    employer_profile: Mapped[Optional["Employer"]] = relationship("Employer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="uploader", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
