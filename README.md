# BlueHire

BlueHire is a premium marketplace for blue-collar workers and contractors.

## Tech Stack

- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy

## Project Structure

```
bluehire/
├── frontend/    # Next.js frontend
└── backend/     # FastAPI backend
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Setup

The project uses Docker to provide a localized PostgreSQL database and pgAdmin interface.

### Prerequisites
- **Docker Desktop**: Must be installed and running.
- **WSL2 Requirement**: Ensure WSL2 backend is enabled in Docker Desktop settings for optimal performance on Windows.

### Starting and Stopping Containers
- **Start Containers**: Run `docker compose up -d` in the root directory.
- **Stop Containers**: Run `docker compose down`.

### Accessing pgAdmin
1. Copy `backend/.env.example` to `.env` and `docker-compose`/root `.env.example` to `.env.docker` in the project root, then set real values for every `CHANGE_ME` placeholder.
2. Start the stack: `docker compose up -d`.
3. Open your browser and navigate to `http://localhost:5050`.
4. Login using the credentials you set in `.env.docker` (`PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD`).

### Ports Used
- **5432**: PostgreSQL Database
- **5050**: pgAdmin Web Interface

### PostgreSQL Database Details
- **Database Name**: `bluehire` (override via `POSTGRES_DB`)
- **Username**: `postgres` (override via `POSTGRES_USER`)
- **Password**: set via `POSTGRES_PASSWORD` (never commit this value)

### Backend environment variables
Copy `backend/.env.example` to `backend/.env` and set a strong `SECRET_KEY` (at least 32 characters):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Never use the `CHANGE_ME` placeholder in production.

## Alembic & Database Migrations

This project uses Alembic for database migrations, which allows us to safely modify the database schema over time without losing data.

### Project Migration Workflow
1. Modify SQLAlchemy models in `backend/models/`.
2. Generate a new migration script based on your changes.
3. Apply the migration to update the database.

### How to Create Migrations
To auto-generate a migration after changing your models, run:
```bash
cd backend
alembic revision --autogenerate -m "Describe your changes"
```

### How to Apply Migrations
To upgrade the database to the latest schema:
```bash
cd backend
alembic upgrade head
```

### How to Rollback Migrations
If you need to revert the last migration:
```bash
cd backend
alembic downgrade -1
```

### Development Notes
- When downgrading PostgreSQL databases, you may need to manually drop `ENUM` types using `DROP TYPE type_name CASCADE` if you intend to re-upgrade and recreate them, due to how Alembic handles ENUMs natively.

## Authentication Security Foundation

BlueHire implements a robust, production-ready security foundation using JSON Web Tokens (JWT) and Argon2 hashing.

### Security Architecture
- **Argon2 Password Hashing**: Passwords are hashed using `pwdlib` and Argon2, protecting against brute-force and rainbow table attacks.
- **JWT Authentication Strategy**: API routes are secured via stateless Bearer access tokens and stateful refresh tokens.
- **Access Tokens**: Short-lived (15 minutes) tokens containing a unique JWT ID (`jti`), `sub`, `type`, `iat`, and `exp`.
- **Refresh Tokens**: Long-lived (7 days) stateful tokens stored in the `refresh_tokens` table. Each refresh token is tracked by its JWT ID (`jti`), expiry, and revocation timestamp.
- **Refresh Token Rotation**: On `/auth/refresh`, the old refresh token is revoked and a new one issued atomically in a single database transaction. Row-level locking (`SELECT FOR UPDATE`) prevents concurrent double-rotation.
- **Refresh Token Reuse Detection**: If an already-revoked refresh token is presented, the request is rejected and all remaining active refresh tokens for that user are revoked, forcing re-authentication across all devices.
- **Logout Revocation**: `/auth/logout` revokes the presented refresh token. Idempotent: invalid or unknown tokens still return success without leaking state.
- **Password-Change Revocation**: `/auth/change-password` revokes every active refresh token for the user atomically with the password update, forcing re-authentication on all devices.
- **Rate Limiting**: `/auth/signup` and `/auth/login` are rate-limited (5 requests/minute per client) via `slowapi` to mitigate brute-force and credential-stuffing attacks. Local development uses in-memory storage; production should use Redis and trust `X-Forwarded-For` from a reverse proxy.
- **Email Enumeration Resistance**: Login returns the same generic error whether the email is unknown or the password is wrong.
- **Custom Security Exceptions**: Sanitized `InvalidTokenError` and `InvalidTokenTypeError` exceptions avoid leaking implementation details.

### Environment Variables Required
The security foundation relies on the following environment variables:
- `SECRET_KEY`: A cryptographically secure random string used to sign JWTs.
- `ALGORITHM`: The JWT signing algorithm (defaults to `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Lifespan of access tokens.
- `REFRESH_TOKEN_EXPIRE_DAYS`: Lifespan of refresh tokens.

## Authentication Schemas

The authentication system employs Pydantic V2 schemas to enforce strict data validation before any business logic is executed.

### Validation Rules & Policy
- **Email Validation**: Enforced via `EmailStr` adhering to standard RFCs.
- **Password Policy**: Enforced using custom validators. Passwords must be at least 8 characters long, and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.
- **Shared Enums**: The `SignupRequest` and `UserResponse` schemas share the `RoleEnum` with the SQLAlchemy models, ensuring complete consistency across the application layers.

### Key Schemas
- `SignupRequest`: Validates new registrations (email, password, role, term acceptance).
- `LoginRequest`: Validates standard JSON-based login payloads.
- `TokenResponse`: Structures the returned `access_token`, `refresh_token`, and token metadata.
- `RefreshTokenRequest`: Validates refresh token payloads.
- `UserResponse`: Defines the public profile format, purposefully omitting sensitive fields like `password_hash`.
- `ChangePasswordRequest`: Validates authenticated password resets and enforces strength and confirmation match checks.

## Authentication Module

The Authentication Module completes the backend security pipeline by integrating the data access layer, business logic layer, and HTTP routing securely.

### Architecture
- **Repository Pattern**: Extracted all database reads and writes to `UserRepository`.
- **Service Layer**: Placed all complex registration, login, and rotation logic in `AuthService` away from HTTP concerns.
- **Dependency Injection**: Seamlessly resolved the database session, repository, service, and current user models via FastAPI `Depends`.

### API Endpoints
- `POST /api/v1/auth/signup`: Accepts user credentials and creates a new account.
- `POST /api/v1/auth/login`: Authenticates credentials to dispense access and refresh JWTs.
- `POST /api/v1/auth/refresh`: Consumes a valid refresh token and performs token rotation securely.
- `POST /api/v1/auth/logout`: Revokes active refresh token sessions.
- `POST /api/v1/auth/change-password` **(Protected)**: Verifies the current active password hash before securely enforcing the new one.
- `GET /api/v1/auth/me` **(Protected)**: Unwraps the bearer token to automatically return the current active `UserResponse` payload.
