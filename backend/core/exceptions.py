class DuplicateEmailError(Exception):
    def __init__(self, message="Email already registered"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsError(Exception):
    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class InactiveUserError(Exception):
    def __init__(self, message="User account is inactive"):
        self.message = message
        super().__init__(self.message)


class RefreshTokenNotFoundError(Exception):
    def __init__(self, message="Refresh token not found or revoked"):
        self.message = message
        super().__init__(self.message)


class CompanyAlreadyExistsError(Exception):
    def __init__(self, message="Company already exists"):
        self.message = message
        super().__init__(self.message)


class CompanyNotFoundError(Exception):
    def __init__(self, message="Company not found"):
        self.message = message
        super().__init__(self.message)

class EmployerAlreadyExistsError(Exception):
    def __init__(self, message="Employer profile already exists"):
        self.message = message
        super().__init__(self.message)

class EmployerNotFoundError(Exception):
    def __init__(self, message="Employer profile not found"):
        self.message = message
        super().__init__(self.message)

class InvalidEmployerRoleError(Exception):
    def __init__(self, message="User does not have the EMPLOYER role"):
        self.message = message
        super().__init__(self.message)

class WorkerAlreadyExistsError(Exception):
    def __init__(self, message="Worker profile already exists"):
        self.message = message
        super().__init__(self.message)

class WorkerNotFoundError(Exception):
    def __init__(self, message="Worker profile not found"):
        self.message = message
        super().__init__(self.message)

class InvalidWorkerRoleError(Exception):
    def __init__(self, message="User does not have the WORKER role"):
        self.message = message
        super().__init__(self.message)

class JobNotFoundError(Exception):
    def __init__(self, message="Job not found"):
        self.message = message
        super().__init__(self.message)

class InvalidJobOwnershipError(Exception):
    def __init__(self, message="You do not have permission to modify this job"):
        self.message = message
        super().__init__(self.message)

class ApplicationAlreadyExistsError(Exception):
    def __init__(self, message="You have already applied to this job"):
        self.message = message
        super().__init__(self.message)

class ApplicationNotFoundError(Exception):
    def __init__(self, message="Application not found"):
        self.message = message
        super().__init__(self.message)

class InvalidApplicationOwnershipError(Exception):
    def __init__(self, message="You do not have permission to modify this application"):
        self.message = message
        super().__init__(self.message)

class JobNotOpenError(Exception):
    def __init__(self, message="This job is not open for applications"):
        self.message = message
        super().__init__(self.message)

class DocumentNotFoundError(Exception):
    def __init__(self, message="Document not found"):
        self.message = message
        super().__init__(self.message)

class InvalidDocumentOwnershipError(Exception):
    def __init__(self, message="You do not have permission to modify this document"):
        self.message = message
        super().__init__(self.message)

class SkillAlreadyExistsError(Exception):
    def __init__(self, message="Skill already exists"):
        self.message = message
        super().__init__(self.message)

class SkillNotFoundError(Exception):
    def __init__(self, message="Skill not found"):
        self.message = message
        super().__init__(self.message)

class WorkerSkillAlreadyExistsError(Exception):
    def __init__(self, message="Worker already has this skill"):
        self.message = message
        super().__init__(self.message)

class WorkerSkillNotFoundError(Exception):
    def __init__(self, message="Worker does not have this skill"):
        self.message = message
        super().__init__(self.message)

class CategoryNotFoundError(Exception):
    def __init__(self, message="Category not found"):
        self.message = message
        super().__init__(self.message)

class EducationNotFoundError(Exception):
    def __init__(self, message="Education entry not found"):
        self.message = message
        super().__init__(self.message)

class InvalidEducationOwnershipError(Exception):
    def __init__(self, message="You do not have permission to modify this education entry"):
        self.message = message
        super().__init__(self.message)

class ExperienceNotFoundError(Exception):
    def __init__(self, message="Experience entry not found"):
        self.message = message
        super().__init__(self.message)

class InvalidExperienceOwnershipError(Exception):
    def __init__(self, message="You do not have permission to modify this experience entry"):
        self.message = message
        super().__init__(self.message)

class CategoryAlreadyExistsError(Exception):
    def __init__(self, message="Category already exists"):
        self.message = message
        super().__init__(self.message)

class NotificationNotFoundError(Exception):
    def __init__(self, message="Notification not found"):
        self.message = message
        super().__init__(self.message)

class InvalidNotificationOwnershipError(Exception):
    def __init__(self, message="You do not have permission to access this notification"):
        self.message = message
        super().__init__(self.message)

class SavedJobAlreadyExistsError(Exception):
    def __init__(self, message="Job is already saved"):
        self.message = message
        super().__init__(self.message)

class SavedJobNotFoundError(Exception):
    def __init__(self, message="Saved job not found"):
        self.message = message
        super().__init__(self.message)
