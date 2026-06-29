import uuid
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin

class SavedJob(TimestampMixin, Base):
    __tablename__ = "saved_jobs"

    worker_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.user_id", ondelete="CASCADE"), primary_key=True)
    job_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    worker: Mapped["Worker"] = relationship("Worker", back_populates="saved_jobs")
    job: Mapped["Job"] = relationship("Job", back_populates="saved_by_workers")

    def __repr__(self) -> str:
        return f"<SavedJob Worker: {self.worker_id} Job: {self.job_id}>"
