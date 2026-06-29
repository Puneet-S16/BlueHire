import uuid
from typing import Optional
from sqlalchemy import Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin
from .enums import ApplicationStatusEnum

class Application(TimestampMixin, Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False)
    worker_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.user_id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[ApplicationStatusEnum] = mapped_column(default=ApplicationStatusEnum.APPLIED, index=True, server_default='APPLIED')
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('job_id', 'worker_id', name='uq_job_worker_application'),
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="applications")
    worker: Mapped["Worker"] = relationship("Worker", back_populates="applications")

    def __repr__(self) -> str:
        return f"<Application Job: {self.job_id} Worker: {self.worker_id} Status: {self.status.name}>"
