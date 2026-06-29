import re
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

from models.enums import RoleEnum

def validate_password_strength(password: str) -> str:
    """
    Helper function to enforce the password policy.
    - Minimum 8 characters
    - One uppercase
    - One lowercase
    - One digit
    - One special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r"[@$!%*?&#^_-]", password):
        raise ValueError("Password must contain at least one special character.")
    return password


class SignupRequest(BaseModel):
    """
    Schema for validating new user registration data.
    """
    email: EmailStr = Field(..., description="A valid email address.")
    password: str = Field(..., description="Strong password meeting complexity requirements.")
    confirm_password: str = Field(..., description="Must match the password field.")
    role: RoleEnum = Field(..., description="Role selected during signup.")
    accept_terms: bool = Field(..., description="Must be true to accept the terms of service.")

    @model_validator(mode="after")
    def validate_signup(self) -> 'SignupRequest':
        if self.accept_terms is not True:
            raise ValueError("You must accept the terms of service.")
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        validate_password_strength(self.password)
        return self


class LoginRequest(BaseModel):
    """
    Schema for validating standard JSON login credentials.
    """
    email: EmailStr = Field(..., description="User's email address.")
    password: str = Field(..., description="User's password.")


class TokenResponse(BaseModel):
    """
    Schema for returning authentication tokens to the client.
    """
    access_token: str = Field(..., description="The JWT access token.")
    refresh_token: str = Field(..., description="The JWT refresh token.")
    token_type: str = Field(default="bearer", description="The token type, always 'bearer'.")
    expires_in: int = Field(..., description="Number of seconds until the access token expires.")


class RefreshTokenRequest(BaseModel):
    """
    Schema for requesting a new access token using a refresh token.
    """
    refresh_token: str = Field(..., description="The JWT refresh token.")


class UserResponse(BaseModel):
    """
    Schema for returning safe public user data.
    Explicitly strips out sensitive fields like password_hash.
    """
    id: UUID = Field(..., description="The user's unique identifier.")
    email: EmailStr = Field(..., description="The user's email address.")
    role: RoleEnum = Field(..., description="The user's assigned role (e.g. worker, employer, admin).")
    is_active: bool = Field(..., description="Whether the user account is active.")
    is_verified: bool = Field(..., description="Whether the user's email has been verified.")
    created_at: datetime = Field(..., description="Timestamp of when the user was created.")

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """
    Schema for validating a password change request for authenticated users.
    """
    current_password: str = Field(..., description="The user's current password.")
    new_password: str = Field(..., description="The new strong password.")
    confirm_password: str = Field(..., description="Must match the new_password field.")

    @model_validator(mode="after")
    def validate_change_password(self) -> 'ChangePasswordRequest':
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match.")
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from the current password.")
        validate_password_strength(self.new_password)
        return self
