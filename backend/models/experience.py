import uuid
from typing import Optional
from datetime import date
from sqlalchemy import String, Text, ForeignKey, Date, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin

class WorkHistory(TimestampMixin, Base):
    __tablename__ = "work_history"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.user_id", ondelete="CASCADE"), index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    currently_working: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    worker: Mapped["Worker"] = relationship("Worker", back_populates="work_history")

    def __repr__(self) -> str:
        return f"<WorkHistory {self.job_title} at {self.company_name}>"

class Education(TimestampMixin, Base):
    __tablename__ = "education"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.user_id", ondelete="CASCADE"), index=True, nullable=False)
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(150), nullable=False)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    worker: Mapped["Worker"] = relationship("Worker", back_populates="education")

    def __repr__(self) -> str:
        return f"<Education {self.degree} at {self.institution_name}>"
