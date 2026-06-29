import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Literal

from jose import jwt, JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from core.config import settings
import logging

logger = logging.getLogger(__name__)

class InvalidTokenError(Exception):
    pass

class InvalidTokenTypeError(Exception):
    pass

# Initialize password hasher with Argon2
password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using Argon2.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a hashed password securely.
    """
    return password_hash.verify(password, hashed_password)


def generate_jti() -> str:
    """
    Generates a unique JWT ID (JTI) for token tracking and revocation.
    """
    return str(uuid.uuid4())


def create_access_token(
    subject: str | uuid.UUID, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a short-lived JSON Web Token (JWT) for API access.
    
    The payload contains only the required claims, specifically omitting
    sensitive PII or role information.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | uuid.UUID, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a long-lived JSON Web Token (JWT) intended for refreshing access tokens.
    
    Includes a unique JTI (JWT ID) to enable cryptographic distinguishability 
    and support token revocation (e.g., via a denylist or database tracking).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "jti": generate_jti(),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises InvalidTokenError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decoding failed: {str(e)}")
        raise InvalidTokenError("Invalid or expired token")


def verify_token_type(payload: Dict[str, Any], expected_type: Literal["access", "refresh"]) -> bool:
    """
    Verifies that the decoded token payload matches the expected token type.
    Raises InvalidTokenTypeError if the token type does not match.
    """
    token_type = payload.get("type")
    if not token_type or token_type != expected_type:
        logger.warning(f"Token type mismatch. Expected '{expected_type}', got '{token_type}'")
        raise InvalidTokenTypeError("Invalid token type")
    return True
