import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from schemas.message import MessageCreate, MessageResponse, MessageListResponse
from repositories.message_repository import MessageRepository
from repositories.conversation_repository import ConversationRepository
from services.message_service import MessageService
from core.exceptions import (
    ConversationNotFoundError,
    InvalidConversationAccessError,
    MessageNotFoundError,
    InvalidMessageAccessError
)

from api.routes.auth import get_current_user

router = APIRouter()

def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(
        MessageRepository(db),
        ConversationRepository(db)
    )

@router.post("/{conversation_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Send a message")
def send_message(
    conversation_id: uuid.UUID,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    msg_service: MessageService = Depends(get_message_service)
) -> Any:
    try:
        return msg_service.send_message(current_user, conversation_id, message_in)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidConversationAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/{conversation_id}", response_model=MessageListResponse, summary="Get messages in conversation")
def get_messages(
    conversation_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    msg_service: MessageService = Depends(get_message_service)
) -> Any:
    try:
        total, results = msg_service.get_conversation_messages(current_user, conversation_id, page, page_size)
        return MessageListResponse(
            total=total,
            page=page,
            page_size=page_size,
            results=results
        )
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidConversationAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.patch("/{conversation_id}/read-all", status_code=status.HTTP_204_NO_CONTENT, summary="Mark all messages as read")
def mark_all_messages_read(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    msg_service: MessageService = Depends(get_message_service)
) -> Any:
    try:
        msg_service.mark_all_messages_read(current_user, conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidConversationAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.patch("/{message_id}/read", response_model=MessageResponse, summary="Mark message as read")
def mark_message_read(
    message_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    msg_service: MessageService = Depends(get_message_service)
) -> Any:
    try:
        return msg_service.mark_message_read(current_user, message_id)
    except MessageNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidConversationAccessError, InvalidMessageAccessError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
