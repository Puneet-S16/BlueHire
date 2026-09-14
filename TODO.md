# BlueHire Task Tracker

## 🔴 High Priority
- [ ] Implement Employer Module.

## 🟡 Medium Priority
- [ ] Configure Pytest for the Backend.
- [ ] Create Database SQLAlchemy test fixtures and temporary test DB setup.
- [ ] Write Integration Tests for `POST /auth/signup`.
- [ ] Write Integration Tests for `POST /auth/login` and Token Rotation.
- [ ] Define Worker Profile schemas.
- [ ] Implement Worker Profile Repository & Service.
- [ ] Expose Profile REST API routes.
- [ ] Create Job Posting schema and DB interaction layers.

## 🔵 Future Improvements
- [ ] Shared dependency module
- [ ] Global exception handlers
- [ ] Implement a `refresh_tokens` database table for stateful active-session tracking.
- [ ] Logging
- [ ] Add global FastAPI Rate Limiting (e.g., `slowapi`).
- [ ] Pytest
- [ ] Configure CI/CD GitHub Actions for automated pytest execution.
- [ ] Integrate Elasticsearch or pgvector for job matching.
- [ ] Design AI Resume Parser.

## ✅ Completed
- [x] Initial FastAPI Setup
- [x] SQLAlchemy Models implementation
- [x] Dockerization (PostgreSQL + pgAdmin)
- [x] Alembic Migrations
- [x] Authentication Architecture Design
- [x] Argon2 Security Foundation
- [x] Pydantic Auth Schemas
- [x] Auth Service and UserRepository
- [x] FastApi Auth Router and Exception Mapping
- [x] QA Integration Testing of Auth Module (100% Pass Rate)
- [x] Implement Company Module
