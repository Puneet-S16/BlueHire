import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.document import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        return self.db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()

    def get_by_worker_id(self, worker_id: uuid.UUID) -> List[Document]:
        return list(self.db.execute(select(Document).where(Document.uploader_id == worker_id)).scalars().all())

    def create_document(self, document: Document) -> Document:
        try:
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            return document
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_document(self, document: Document) -> Document:
        try:
            self.db.commit()
            self.db.refresh(document)
            return document
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_document(self, document: Document) -> None:
        try:
            self.db.delete(document)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
