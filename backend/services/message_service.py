import uuid
from typing import List, Tuple
from models.user import User
from models.message import Message
from schemas.message import MessageCreate
from repositories.message_repository import MessageRepository
from repositories.conversation_repository import ConversationRepository
from core.exceptions import (
    ConversationNotFoundError,
    InvalidConversationAccessError,
    MessageNotFoundError,
    InvalidMessageAccessError
)

class MessageService:
    def __init__(self, msg_repo: MessageRepository, conv_repo: ConversationRepository):
        self.msg_repo = msg_repo
        self.conv_repo = conv_repo

    def _verify_conversation_access(self, user: User, conversation_id: uuid.UUID):
        conv = self.conv_repo.get_by_id(conversation_id)
        if not conv:
            raise ConversationNotFoundError("Conversation not found")
        if conv.employer_id != user.id and conv.worker_id != user.id:
            raise InvalidConversationAccessError("You do not have access to this conversation")
        return conv

    def send_message(self, user: User, conversation_id: uuid.UUID, data: MessageCreate) -> Message:
        self._verify_conversation_access(user, conversation_id)
        msg = Message(
            conversation_id=conversation_id,
            sender_id=user.id,
            content=data.content
        )
        return self.msg_repo.create_message(msg)

    def get_conversation_messages(self, user: User, conversation_id: uuid.UUID, page: int = 1, page_size: int = 20) -> Tuple[int, List[Message]]:
        self._verify_conversation_access(user, conversation_id)
        return self.msg_repo.get_messages(conversation_id, page, page_size)

    def mark_message_read(self, user: User, message_id: uuid.UUID) -> Message:
        msg = self.msg_repo.get_message(message_id)
        if not msg:
            raise MessageNotFoundError("Message not found")
            
        # Verify access to the conversation first
        conv = self._verify_conversation_access(user, msg.conversation_id)
        
        # Only the receiver can mark a message as read
        if msg.sender_id == user.id:
            raise InvalidMessageAccessError("You cannot mark your own message as read")
            
        return self.msg_repo.mark_read(msg)

    def mark_all_messages_read(self, user: User, conversation_id: uuid.UUID) -> None:
        self._verify_conversation_access(user, conversation_id)
        self.msg_repo.mark_all_read(conversation_id, receiver_id=user.id)
