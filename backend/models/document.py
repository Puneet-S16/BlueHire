import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin
from .enums import DocumentTypeEnum

class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploader_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    document_type: Mapped[DocumentTypeEnum] = mapped_column(nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    uploader: Mapped["User"] = relationship("User", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.document_type} - {self.file_name or self.id}>"
