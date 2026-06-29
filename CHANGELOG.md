# Changelog

All notable changes to this project will be documented in this file.

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
