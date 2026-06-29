import uuid
from typing import Optional
from sqlalchemy import Text, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin

class Review(TimestampMixin, Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reviewee_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), index=True, nullable=True)
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='chk_rating_range'),
    )

    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewer_id])
    reviewee: Mapped["User"] = relationship("User", foreign_keys=[reviewee_id])
    job: Mapped[Optional["Job"]] = relationship("Job")

    def __repr__(self) -> str:
        return f"<Review From: {self.reviewer_id} To: {self.reviewee_id} Rating: {self.rating}>"
