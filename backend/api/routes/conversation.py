import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from schemas.conversation import ConversationResponse, ConversationListResponse
from repositories.conversation_repository import ConversationRepository
from repositories.application_repository import ApplicationRepository
from repositories.employer_repository import EmployerRepository
from services.conversation_service import ConversationService
from core.exceptions import (
    ConversationAlreadyExistsError,
    ConversationNotFoundError,
    InvalidConversationAccessError,
    InvalidEmployerRoleError,
    ApplicationNotFoundError
)

from api.routes.auth import get_current_user

router = APIRouter()

def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(
        ConversationRepository(db),
        ApplicationRepository(db),
        EmployerRepository(db)
    )

@router.post("/application/{application_id}", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED, summary="Create a conversation")
def create_conversation(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    conv_service: ConversationService = Depends(get_conversation_service)
) -> Any:
    try:
        return conv_service.create_conversation(current_user, application_id)
    except InvalidEmployerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidConversationAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConversationAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/me", response_model=ConversationListResponse, summary="Get my conversations")
def get_my_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    conv_service: ConversationService = Depends(get_conversation_service)
) -> Any:
    total, results = conv_service.get_my_conversations(current_user, page, page_size)
    return ConversationListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results
    )

@router.get("/{conversation_id}", response_model=ConversationResponse, summary="Get conversation details")
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    conv_service: ConversationService = Depends(get_conversation_service)
) -> Any:
    try:
        return conv_service.get_conversation(current_user, conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidConversationAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
