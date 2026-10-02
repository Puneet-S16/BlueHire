import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from models.message import Message

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_message(self, message_id: uuid.UUID) -> Message:
        return self.db.execute(
            select(Message).where(Message.id == message_id)
        ).scalar_one_or_none()

    def get_messages(self, conversation_id: uuid.UUID, page: int = 1, page_size: int = 20) -> Tuple[int, List[Message]]:
        query = select(Message).where(Message.conversation_id == conversation_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0
        
        # Newest first for pagination, clients usually reverse
        query = query.order_by(Message.created_at.desc())
        
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        
        records = list(self.db.execute(query).scalars().all())
        return total, records

    def create_message(self, message: Message) -> Message:
        try:
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def mark_read(self, message: Message) -> Message:
        try:
            message.is_read = True
            self.db.commit()
            self.db.refresh(message)
            return message
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def mark_all_read(self, conversation_id: uuid.UUID, receiver_id: uuid.UUID) -> None:
        try:
            self.db.execute(
                update(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != receiver_id,
                    Message.is_read == False
                )
                .values(is_read=True)
            )
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
