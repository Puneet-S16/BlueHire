import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin

class Employer(TimestampMixin, Base):
    __tablename__ = "employers"

    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), index=True, nullable=True)
    
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    job_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="employer_profile")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="employers")
    posted_jobs: Mapped[List["Job"]] = relationship("Job", back_populates="posted_by")

    def __repr__(self) -> str:
        return f"<Employer {self.first_name} {self.last_name}>"
