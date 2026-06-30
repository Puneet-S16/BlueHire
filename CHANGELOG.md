# Changelog

All notable changes to this project will be documented in this file.

## [v0.4.5] - 2026-06-30
### Added
- Authentication Service enforcing business logic without HTTP coupling.
- Repository Pattern implementation for the User domain.
- Authentication Router mapping REST endpoints securely to the service layer.
- JWT Dependencies for extracting and decoding tokens automatically.
- Protected Endpoints (`/auth/me`, `/auth/change-password`) ensuring secure authenticated interactions.
- OpenAPI Improvements mapping domain exceptions into meaningful HTTP status codes.

## [v0.4.3] - 2026-06-30
### Added
- Authentication Schemas using Pydantic V2 (`SignupRequest`, `LoginRequest`, `TokenResponse`, etc.).
- Robust validation rules for emails and strict password policies.
- Shared `RoleEnum` integrated directly into schemas for end-to-end consistency.

## [v0.4.2] - 2026-06-30
### Added
- Security Foundation for Authentication architecture.
- JWT Infrastructure for Access and Refresh tokens.
- Argon2 Integration via pwdlib for password hashing.
- Token Validation and payload verification logic.
- Production Hardening with custom exception masking.

## [v0.3.0] - 2026-06-30
### Added
- Alembic configuration for database migrations.
- Initial schema migration auto-generated from SQLAlchemy models.
- Database validation setup and testing.
- Rollback verification and PostgreSQL integration.

## [v0.2.0] - 2026-06-30
### Added
- Docker Compose setup for localized infrastructure.
- PostgreSQL database container.
- pgAdmin container for database management.
- Docker Network configuration for container communication.
- Docker Volumes for data persistence.
- Health Checks for ensuring PostgreSQL is ready before accepting connections.
