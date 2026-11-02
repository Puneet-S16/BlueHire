import uuid
from typing import Any, List

from api.routes.auth import get_current_user
from core.exceptions import (
    DocumentNotFoundError,
    InvalidDocumentOwnershipError,
    InvalidWorkerRoleError,
    WorkerNotFoundError,
)
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.enums import RoleEnum
from models.user import User
from repositories.document_repository import DocumentRepository
from repositories.worker_repository import WorkerRepository
from schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from services.document_service import DocumentService
from sqlalchemy.orm import Session

router = APIRouter()


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    document_repo = DocumentRepository(db)
    worker_repo = WorkerRepository(db)
    return DocumentService(document_repo, worker_repo)


def require_worker_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != RoleEnum.WORKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with the WORKER role can access this endpoint",
        )
    return current_user


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
)
def create_document(
    request: DocumentCreate,
    current_user: User = Depends(require_worker_role),
    document_service: DocumentService = Depends(get_document_service),
) -> Any:
    """
    Create a new document linked to the authenticated worker. Requires WORKER role.
    """
    try:
        return document_service.create_document(current_user, request)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/me", response_model=List[DocumentResponse], summary="Get my documents")
def get_my_documents(
    current_user: User = Depends(require_worker_role),
    document_service: DocumentService = Depends(get_document_service),
) -> Any:
    """
    Retrieve all documents uploaded by the authenticated worker. Requires WORKER role.
    """
    try:
        return document_service.get_my_documents(current_user)
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{document_id}", response_model=DocumentResponse, summary="Update a document")
def update_document(
    document_id: uuid.UUID,
    request: DocumentUpdate,
    current_user: User = Depends(require_worker_role),
    document_service: DocumentService = Depends(get_document_service),
) -> Any:
    """
    Update a document. Requires WORKER role and document ownership.
    """
    try:
        return document_service.update_document(current_user, document_id, request)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDocumentOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document"
)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(require_worker_role),
    document_service: DocumentService = Depends(get_document_service),
) -> None:
    """
    Delete a document. Requires WORKER role and document ownership.
    """
    try:
        document_service.delete_document(current_user, document_id)
    except DocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDocumentOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
