import enum

class RoleEnum(str, enum.Enum):
    WORKER = "WORKER"
    EMPLOYER = "EMPLOYER"
    ADMIN = "ADMIN"

class VerificationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class AvailabilityStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    HIRED = "HIRED"
    UNAVAILABLE = "UNAVAILABLE"

class DocumentTypeEnum(str, enum.Enum):
    RESUME = "RESUME"
    CERTIFICATE = "CERTIFICATE"
    LICENSE = "LICENSE"
    COMPANY_REGISTRATION = "COMPANY_REGISTRATION"
    OTHER = "OTHER"

class JobTypeEnum(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    ONE_OFF = "ONE_OFF"

class JobStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"

class PayTypeEnum(str, enum.Enum):
    HOURLY = "HOURLY"
    FIXED = "FIXED"
    NEGOTIABLE = "NEGOTIABLE"

class ApplicationStatusEnum(str, enum.Enum):
    APPLIED = "APPLIED"
    REVIEWING = "REVIEWING"
    INTERVIEW = "INTERVIEW"
    HIRED = "HIRED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
