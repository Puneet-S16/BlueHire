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
2. **Schemas** (`backend/schemas/`): Pydantic V2 models for HTTP request validation and response serialization. Use `ConfigDict(from_attributes=True)`.
3. **Repositories** (`backend/repositories/`): Pure database interaction layer. Contains SQLAlchemy `Session` operations (`select`, `add`, `commit`, `rollback` on `SQLAlchemyError`). Avoid N+1 queries.
4. **Services** (`backend/services/`): Pure business logic. Orchestrates repositories, handles domain rules, and raises custom exceptions. No HTTP awareness (`fastapi` imports are forbidden here). Validate roles and ownership explicitly.
5. **API / Routers** (`backend/api/routes/`): FastAPI endpoints handling HTTP requests, mapping domain exceptions to HTTP status codes, and executing Dependency Injection.

## Important Implementation Details
### Authentication Architecture
- **JWT Strategy**: Stateless authentication via `Bearer` tokens. 
  - Access Tokens (15m): Short-lived, used for API authorization.
  - Refresh Tokens (7d): Long-lived.
- **Protected Routes**: Use `Depends(get_current_user)` to automatically extract, validate, and inject the authenticated `User` object into the endpoint.

### Dependency Injection Rules
- Endpoints must NEVER manually instantiate Services or Repositories.
- Use FastAPI `Depends`: `get_db` -> `get_service` (injects repos).

### Error Handling
- Services raise custom domain errors found in `backend/core/exceptions.py`.
- Routers catch these and raise `HTTPException` with the correct status code (e.g., 401, 403, 404, 409).
- Database operations wrap `commit()` and `refresh()` in `try/except SQLAlchemyError` to trigger `rollback()`.

## Current Project Version
**v0.6.2** (Core Marketplace Finished)

## Milestones State
- **Completed**: Auth, Company, Employer, Worker, Skills, Categories, Education, Experience, Documents, Jobs, Applications, Job Search, Saved Jobs, Recommendations, Dashboards, Notifications, Messaging.
- **Current / Next Phase**: AI Matching Engine & Vector Search.

## Pending Database Migrations
Due to strict architectural adherence over several phases, the database schema has drifted from its initial Phase 1 deployment. An Alembic auto-migration is mandatory before server boot.
- **Education**: Restructured columns completely (institution, degree, start_date, end_date, etc.).
- **Experience**: Added `employment_type` and `currently_working` flags.
- **Notification**: Renamed `type` -> `notification_type`, `content` -> `message`; Added `title`.
- **Conversation / Message**: Created entirely new relational tables supporting the communication module.

## Instructions for Future AI Sessions
1. **DO NOT deviate from the architecture.** If you need database access, write a Repository method. If you need business logic, write a Service method.
2. **DO NOT modify existing models/schemas** without explicit permission from the user.
3. **DO NOT expose internal logic.** Map all exceptions carefully in the router.
4. **Assume Docker is running PostgreSQL** on port `5432`.
5. **Always read this file first** to orient yourself to the codebase.
