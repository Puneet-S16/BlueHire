import uuid
from typing import List
from models.user import User
from models.document import Document
from models.enums import RoleEnum
from schemas.document import DocumentCreate, DocumentUpdate
from repositories.document_repository import DocumentRepository
from repositories.worker_repository import WorkerRepository
from core.exceptions import DocumentNotFoundError, InvalidDocumentOwnershipError, WorkerNotFoundError, InvalidWorkerRoleError

class DocumentService:
    def __init__(self, document_repo: DocumentRepository, worker_repo: WorkerRepository):
        self.document_repo = document_repo
        self.worker_repo = worker_repo

    def _verify_worker(self, user: User):
        if user.role != RoleEnum.WORKER:
            raise InvalidWorkerRoleError("Only users with WORKER role can manage documents")
        worker = self.worker_repo.get_by_user_id(user.id)
        if not worker:
            raise WorkerNotFoundError("Worker profile not found")
        return worker

    def create_document(self, user: User, request: DocumentCreate) -> Document:
        self._verify_worker(user)
        
        document = Document(
            uploader_id=user.id,
            document_type=request.document_type,
            file_url=request.file_url,
            file_name=request.file_name
        )
        return self.document_repo.create_document(document)

    def get_my_documents(self, user: User) -> List[Document]:
        self._verify_worker(user)
        return self.document_repo.get_by_worker_id(user.id)

    def update_document(self, user: User, document_id: uuid.UUID, request: DocumentUpdate) -> Document:
        self._verify_worker(user)
        
        document = self.document_repo.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError("Document not found")
            
        if document.uploader_id != user.id:
            raise InvalidDocumentOwnershipError("You do not have permission to modify this document")
            
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(document, key, value)
            
        return self.document_repo.update_document(document)

    def delete_document(self, user: User, document_id: uuid.UUID) -> None:
        self._verify_worker(user)
        
        document = self.document_repo.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError("Document not found")
            
        if document.uploader_id != user.id:
            raise InvalidDocumentOwnershipError("You do not have permission to modify this document")
            
        self.document_repo.delete_document(document)
