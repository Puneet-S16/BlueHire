import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from schemas.notification import NotificationResponse, NotificationListResponse
from repositories.notification_repository import NotificationRepository
from services.notification_service import NotificationService
from core.exceptions import NotificationNotFoundError, InvalidNotificationOwnershipError

from api.routes.auth import get_current_user

router = APIRouter()

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(NotificationRepository(db))

@router.get("", response_model=NotificationListResponse, summary="Get my notifications")
def get_my_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
) -> Any:
    total, results = notification_service.get_my_notifications(current_user, page, page_size)
    return NotificationListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results
    )

@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT, summary="Mark all notifications as read")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
) -> Any:
    notification_service.mark_all_as_read(current_user)

@router.patch("/{notification_id}/read", response_model=NotificationResponse, summary="Mark notification as read")
def mark_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
) -> Any:
    try:
        return notification_service.mark_as_read(current_user, notification_id)
    except NotificationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidNotificationOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
