import uuid
from typing import Optional, List
from sqlalchemy import String, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin
from .enums import AvailabilityStatusEnum

class Worker(TimestampMixin, Base):
    __tablename__ = "workers"

    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    total_experience_years: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), nullable=True)
    expected_salary: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    availability_status: Mapped[AvailabilityStatusEnum] = mapped_column(default=AvailabilityStatusEnum.AVAILABLE, index=True, server_default='AVAILABLE')
    
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="worker_profile")
    worker_skills: Mapped[List["WorkerSkill"]] = relationship("WorkerSkill", back_populates="worker", cascade="all, delete-orphan")
    work_history: Mapped[List["WorkHistory"]] = relationship("WorkHistory", back_populates="worker", cascade="all, delete-orphan")
    education: Mapped[List["Education"]] = relationship("Education", back_populates="worker", cascade="all, delete-orphan")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="worker", cascade="all, delete-orphan")
    saved_jobs: Mapped[List["SavedJob"]] = relationship("SavedJob", back_populates="worker", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Worker {self.first_name} {self.last_name}>"
