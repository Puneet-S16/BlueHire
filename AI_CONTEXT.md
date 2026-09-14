# AI Context Memory

This file serves as the permanent memory and instruction manual for any AI coding assistant or future developer joining the **BlueHire** project. Read this entire document before writing any code.

## Project Overview
BlueHire is a premium job marketplace platform bridging the gap between blue-collar workers, contractors, and employers. It emphasizes modern aesthetics, extreme reliability, and AI-driven matching.

## Technology Stack
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui.
- **Backend**: FastAPI (Python), Pydantic V2, SQLAlchemy 2.0 (Sync).
- **Database**: PostgreSQL (Dockerized).
- **Security**: Argon2 (`pwdlib`), JWT (`python-jose`).
- **Migrations**: Alembic.

## Current Architecture
The backend strictly adheres to a layered **Clean Architecture** to decouple HTTP routing from business logic and database I/O.
1. **Models** (`backend/models/`): SQLAlchemy Declarative Base models defining the SQL schema.
2. **Schemas** (`backend/schemas/`): Pydantic V2 models for HTTP request validation and response serialization.
3. **Repositories** (`backend/repositories/`): Pure database interaction layer. Contains SQLAlchemy `Session` operations.
4. **Services** (`backend/services/`): Pure business logic. Orchestrates repositories, handles domain rules, and raises custom exceptions. No HTTP awareness (`fastapi` imports are forbidden here).
5. **API / Routers** (`backend/api/routes/`): FastAPI endpoints handling HTTP requests, mapping domain exceptions to HTTP status codes, and executing Dependency Injection.

## Folder Structure
```
bluehire/
├── frontend/             # Next.js UI
└── backend/              # FastAPI Application
    ├── alembic/          # Migration scripts
    ├── api/              # API routers and dependencies
    │   └── routes/       # Endpoint definitions
    ├── core/             # Config, security, domain exceptions
    ├── db/               # Database connection and session
    ├── models/           # SQLAlchemy models
    ├── repositories/     # Data access layer
    ├── schemas/          # Pydantic validation models
    └── services/         # Business logic
```

## Important Implementation Details
### Authentication Architecture
- **JWT Strategy**: Stateless authentication via `Bearer` tokens. 
  - Access Tokens (15m): Short-lived, used for API authorization.
  - Refresh Tokens (7d): Long-lived, used to obtain new access tokens. Contains a unique `jti`.
- **Password Hashing**: Argon2 (`pwdlib`) is the standard.
- **Protected Routes**: Use `Depends(get_current_user)` to automatically extract, validate, and inject the authenticated `User` object into the endpoint.

### Dependency Injection Rules
- Endpoints must NEVER manually instantiate Services or Repositories.
- Use FastAPI `Depends`: `get_db` -> `get_user_repository` -> `get_auth_service`.
- Keep DI localized to endpoints.

### Coding Standards
- Enforce full Python type hints (`-> Any`, `-> User`, etc.).
- Docstrings are required on all functions, classes, and Pydantic schemas.
- Pydantic V2 strict validation (`@model_validator(mode="after")`).
- Use the shared `models.enums.RoleEnum` directly inside Pydantic schemas to ensure DB-Schema parity.

### Error Handling
- Services raise custom domain errors (`DuplicateEmailError`, `InvalidCredentialsError`, etc.) found in `backend/core/exceptions.py`.
- Routers catch these and raise `HTTPException` with the correct status code (e.g., 401, 403, 409).
- Database operations wrap `commit()` and `refresh()` in `try/except` to trigger `rollback()` and prevent deadlocks on `IntegrityError`.

## Current Project Version
**v0.5.0**

## Milestones State
- **Completed**: Database Models, Docker Infrastructure, Alembic Setup, Authentication Module, Company Module.
- **Current / Next**: Employer Module.

# Completed Feature Modules

## Company Module

Implemented:
- Company Schemas
- Company Repository
- Company Service
- Company Router
- Domain Exceptions
- Validation Rules
- CRUD APIs

Architecture:
Model
↓
Schema
↓
Repository
↓
Service
↓
Router

Important Notes:
- Company ownership is not tracked directly.
- Employer model owns the relationship through company_id.
- Company creation requires authentication.
- Company names are unique.
- Validation rules added for name, industry, city, and state.

## Instructions for Future AI Sessions
1. **DO NOT deviate from the architecture.** If you need database access, write a Repository method. If you need business logic, write a Service method.
2. **DO NOT modify existing models/schemas** without explicit permission from the user.
3. **DO NOT expose internal logic.** Map all exceptions carefully in the router.
4. **Assume Docker is running PostgreSQL** on port `5432`.
5. **Always read this file first** to orient yourself to the codebase.
