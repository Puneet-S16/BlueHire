import uuid
from typing import Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin
from .enums import VerificationStatusEnum

class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[VerificationStatusEnum] = mapped_column(default=VerificationStatusEnum.PENDING, server_default='PENDING')
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    employers: Mapped[List["Employer"]] = relationship("Employer", back_populates="company")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company {self.name}>"
