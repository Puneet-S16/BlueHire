import uuid
from typing import List, Tuple
from models.user import User
from models.notification import Notification
from repositories.notification_repository import NotificationRepository
from core.exceptions import NotificationNotFoundError, InvalidNotificationOwnershipError

class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    def get_my_notifications(self, user: User, page: int = 1, page_size: int = 20) -> Tuple[int, List[Notification]]:
        return self.notification_repo.get_user_notifications(user.id, page, page_size)

    def mark_as_read(self, user: User, notification_id: uuid.UUID) -> Notification:
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundError("Notification not found")
            
        if notification.user_id != user.id:
            raise InvalidNotificationOwnershipError("You do not have permission to access this notification")
            
        return self.notification_repo.mark_as_read(notification)

    def mark_all_as_read(self, user: User) -> None:
        self.notification_repo.mark_all_as_read(user.id)
