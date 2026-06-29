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
1. Open your browser and navigate to `http://localhost:5050`.
2. Login using the default development credentials:
   - **Email**: `admin@bluehire.com`
   - **Password**: `admin123`

### Ports Used
- **5432**: PostgreSQL Database
- **5050**: pgAdmin Web Interface

### PostgreSQL Database Details
- **Database Name**: `bluehire`
- **Username**: `postgres`
- **Password**: `postgres`

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
