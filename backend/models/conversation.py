import uuid
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin

class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False, unique=True)
    employer_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("employers.user_id", ondelete="CASCADE"), index=True, nullable=False)
    worker_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.user_id", ondelete="CASCADE"), index=True, nullable=False)

    # Relationships
    application: Mapped["Application"] = relationship("Application")
    employer: Mapped["Employer"] = relationship("Employer")
    worker: Mapped["Worker"] = relationship("Worker")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Conversation {self.id}>"
