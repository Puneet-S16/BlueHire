import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from sqlalchemy.exc import SQLAlchemyError
from models.conversation import Conversation

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, conversation_id: uuid.UUID) -> Conversation:
        return self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        ).scalar_one_or_none()

    def get_by_application(self, application_id: uuid.UUID) -> Conversation:
        return self.db.execute(
            select(Conversation).where(Conversation.application_id == application_id)
        ).scalar_one_or_none()

    def get_user_conversations(self, user_id: uuid.UUID, page: int = 1, page_size: int = 20) -> Tuple[int, List[Conversation]]:
        query = select(Conversation).where(
            or_(
                Conversation.employer_id == user_id,
                Conversation.worker_id == user_id
            )
        )
        
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0
        
        query = query.order_by(Conversation.updated_at.desc())
        
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)
        
        records = list(self.db.execute(query).scalars().all())
        return total, records

    def create_conversation(self, conversation: Conversation) -> Conversation:
        try:
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation
        except SQLAlchemyError:
            self.db.rollback()
            raise
