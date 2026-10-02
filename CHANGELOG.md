# Changelog

All notable changes to this project will be documented in this file.

## [v0.6.2] - 2026-10-02
### Added
- **Conversations Module**: Endpoints mapping 1:1 job application chats.
- **Messaging Module**: Secure, paginated threads between Employers and Workers.
- **Dashboard Unread Message Integration**: Aggregated count injections preventing N+1 queries.
- **Notification Integration**: Cross-module unread status delivery.
## [v0.6.1] - 2026-10-02
### Added
- Saved Jobs Module
- Job Recommendation Engine (SQL-based Scoring)
- Cross-field compatibility checking
## [v0.6.0] - 2026-10-02
### Added
- Employer & Worker Profile Modules
- Job & Applications Modules
- Resume / Document Module
- Skills & Categories Modules
- Education & Experience Modules
- Job Discovery & Search Module (Marketplace complete)
## v0.5.0
### Added
- Company Management Module
- Company CRUD APIs
- Company Repository Layer
- Company Service Layer
- Company Schemas
- Domain Exceptions
- Validation Rules

### Notes
- Company ownership handled through Employer relationships.

## [v0.4.5] - 2026-06-30
### Added
- **Authentication Service**: Enforcing business logic without HTTP coupling.
- **Repository Pattern**: Extracted data access layer for the User domain.
- **Authentication Router**: REST API mapping securely to the service layer.
- **JWT Dependencies**: OAuth2 DI for extracting and decoding tokens automatically.
- **Protected Endpoints**: `/auth/me`, `/auth/change-password` secured by Bearer token parsing.
- **Exception Mapping**: Internal domain exceptions correctly translated to HTTP status codes.

## [v0.4.3] - 2026-06-30
### Added
- **Pydantic Schemas**: Created `SignupRequest`, `LoginRequest`, `TokenResponse`, etc.
- **Complex Validation**: Implemented strict password policies and standard RFC email validation.
- **Shared Enums**: Integrated `RoleEnum` directly into API schemas for DB consistency.

## [v0.4.2] - 2026-06-30
### Added
- **Security Foundation**: JWT generation/decoding architecture.
- **Password Hashing**: Implemented Argon2 via `pwdlib`.
- **Custom Exceptions**: Defined `InvalidTokenError` to mask cryptographic internal errors.
- **Configuration**: Added `.env` auth variables (`SECRET_KEY`, `ALGORITHM`).

## [v0.3.0] - 2026-06-30
### Added
- **Alembic Environment**: Configured `alembic.ini` and environment for SQLAlchemy.
- **Initial Migration**: Auto-generated the full relational schema.
- **Validation**: Tested rollback and upgrade reliability.

## [v0.2.0] - 2026-06-30
### Added
- **Docker Infrastructure**: `docker-compose.yml` for unified development.
- **PostgreSQL**: Local isolated database.
- **pgAdmin**: GUI for database exploration and management.
- **Networking/Volumes**: Persistent volumes and mapped ports for safe container restarts.

## [v0.1.0] - 2026-06-30
### Added
- **Database Architecture**: Core base setup.
- **SQLAlchemy Models**: Created models for Users, Profiles (Worker/Employer/Company), Jobs, Reviews, Documents, and Experiences.
- **Relationships**: Configured one-to-one and one-to-many ORM mappings.



