# BlueHire Task Tracker

## 🚀 High Priority (Next Phase)
- [ ] Implement AI Matching Engine (Phase 9.0).
- [ ] Implement Resume Vectorization (pgvector/OpenAI embeddings).
- [ ] Integrate Real-Time WebSockets for Live Messaging & Notifications (Phase 10.0).

## 🛠️ Medium Priority
- [ ] Implement Admin Panel & Moderation APIs (Phase 11.0).
- [ ] Analytics & Reporting APIs for Dashboards.
- [ ] Configure Pytest for the Backend and write Integration Tests.
- [ ] Create Database SQLAlchemy test fixtures and temporary test DB setup.

## 🔮 Future Improvements
- [ ] Global exception handlers.
- [ ] Implement a `refresh_tokens` database table for stateful active-session tracking.
- [ ] Comprehensive Application Logging.
- [ ] Add global FastAPI Rate Limiting (e.g., `slowapi`).
- [ ] Configure CI/CD GitHub Actions for automated pytest execution.
- [ ] Production DevOps scripts (Docker Swarm/K8s/Cloud).

## 🗄️ Pending Database Migrations
Due to model drifts, an Alembic autogenerate migration must be run covering:
- **Education Schema Migration**: Replaced initial columns with explicit (institution, degree, start/end dates, grade).
- **Experience Schema Migration**: Added `employment_type` and `currently_working` flag.
- **Notification Schema Migration**: Renamed `type` -> `notification_type`, `content` -> `message`; Added `title`.
- **Conversation Table Creation**: Created `conversations` with relations to `applications`, `employers`, `workers`.
- **Message Table Creation**: Created `messages` linked to `conversations` and `users`.

## ✅ Completed
- [x] Initial FastAPI Setup
- [x] SQLAlchemy Models implementation
- [x] Dockerization (PostgreSQL + pgAdmin)
- [x] Alembic Migrations
- [x] Authentication Architecture Design
- [x] Company Module
- [x] Employer Profile Module
- [x] Worker Profile Module
- [x] Skills & Categories Module
- [x] Education & Experience Module
- [x] Resume / Document Module
- [x] Job Management Module
- [x] Applications Module
- [x] Search & Discovery Engine
- [x] Saved Jobs & SQL Recommendation Engine
- [x] Dashboards & Notification Module
- [x] Conversations & Messaging System
