import uuid
from typing import List, Tuple
from models.user import User
from models.conversation import Conversation
from models.enums import RoleEnum
from repositories.conversation_repository import ConversationRepository
from repositories.application_repository import ApplicationRepository
from repositories.employer_repository import EmployerRepository
from core.exceptions import (
    ConversationAlreadyExistsError,
    ConversationNotFoundError,
    InvalidConversationAccessError,
    InvalidEmployerRoleError,
    ApplicationNotFoundError
)

class ConversationService:
    def __init__(self, conv_repo: ConversationRepository, app_repo: ApplicationRepository, emp_repo: EmployerRepository):
        self.conv_repo = conv_repo
        self.app_repo = app_repo
        self.emp_repo = emp_repo

    def create_conversation(self, user: User, application_id: uuid.UUID) -> Conversation:
        if user.role != RoleEnum.EMPLOYER:
            raise InvalidEmployerRoleError("Only EMPLOYER may create conversations")

        employer = self.emp_repo.get_by_user_id(user.id)
        if not employer:
            raise InvalidEmployerRoleError("Employer profile not found")

        application = self.app_repo.get_by_id(application_id)
        if not application:
            raise ApplicationNotFoundError("Application not found")

        # Employer must own the application's job/company
        if application.job.company_id != employer.company_id:
            raise InvalidConversationAccessError("You do not own this application's job")

        existing_conv = self.conv_repo.get_by_application(application_id)
        if existing_conv:
            raise ConversationAlreadyExistsError("Conversation already exists for this application")

        conv = Conversation(
            application_id=application_id,
            employer_id=user.id,
            worker_id=application.worker_id
        )
        return self.conv_repo.create_conversation(conv)

    def get_my_conversations(self, user: User, page: int = 1, page_size: int = 20) -> Tuple[int, List[Conversation]]:
        return self.conv_repo.get_user_conversations(user.id, page, page_size)

    def get_conversation(self, user: User, conversation_id: uuid.UUID) -> Conversation:
        conv = self.conv_repo.get_by_id(conversation_id)
        if not conv:
            raise ConversationNotFoundError("Conversation not found")

        if conv.employer_id != user.id and conv.worker_id != user.id:
            raise InvalidConversationAccessError("You do not have access to this conversation")

        return conv
