import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from models.notification import Notification

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, notification_id: uuid.UUID) -> Notification:
        return self.db.execute(select(Notification).where(Notification.id == notification_id)).scalar_one_or_none()

    def get_user_notifications(self, user_id: uuid.UUID, page: int = 1, page_size: int = 20) -> Tuple[int, List[Notification]]:
        query = select(Notification).where(Notification.user_id == user_id)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0
        
        # Order by unread first, then latest created
        query = query.order_by(Notification.is_read.asc(), Notification.created_at.desc())
        
        # Pagination
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        
        records = list(self.db.execute(query).scalars().all())
        return total, records

    def mark_as_read(self, notification: Notification) -> Notification:
        try:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception:
            self.db.rollback()
            raise

    def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        try:
            self.db.execute(
                update(Notification)
                .where(Notification.user_id == user_id, Notification.is_read == False)
                .values(is_read=True)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
