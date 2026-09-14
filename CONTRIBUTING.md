# Contributing to BlueHire

Thank you for contributing! Whether you are a human developer or an AI assistant, these guidelines must be strictly followed to ensure the long-term maintainability of the project.

## 1. Architecture Rules (Clean Architecture)
BlueHire relies on strict boundary separations:
- **Router Layer** (`api/routes`): Only handles HTTP Requests, status codes, and injecting dependencies. **Never** put business logic or DB calls here.
- **Service Layer** (`services/`): Pure business logic. Orchestrates repositories, enforces rules, and raises custom Exceptions. **Never** import `fastapi` here.
- **Repository Layer** (`repositories/`): Only handles database operations (`db.query`, `db.add`). **Never** enforce business rules here.
- **Schemas** (`schemas/`): Pydantic validation only.
- **Models** (`models/`): SQLAlchemy definitions only.

## 2. Coding Style
- **Type Hints**: Explicitly type every function parameter and return type (`def foo(bar: str) -> bool:`).
- **Docstrings**: Include clear, concise Python docstrings on every class, schema, and function.
- **Pydantic**: Use Pydantic V2 constructs (`ConfigDict`, `model_validator`, `Field`).

## 3. Git Commit Format
We use **Conventional Commits**:
- `feat(auth): add login endpoint`
- `fix(db): resolve migration conflict`
- `docs(readme): update setup instructions`
- `test(auth): add auth integration tests`
- `chore(deps): update requirements.txt`

## 4. Pull Request Checklist
- [ ] Code follows the Layered Architecture rules.
- [ ] No database operations exist in the router.
- [ ] Domain exceptions are mapped to HTTP status codes properly.
- [ ] Secrets and credentials are not hardcoded.
- [ ] Code is fully typed.

## 5. Testing Requirements
- Every new Service method must be accompanied by integration or unit tests.
- Execute Pytest before pushing to guarantee nothing is broken.
- Verify edge cases (Invalid data, missing data, incorrect types).

## 6. Code Review Checklist
- Check for SQL injection vulnerabilities.
- Ensure transactions are properly wrapped in `try/except` with a `.rollback()`.
- Validate that all dependencies are injected via `Depends()`.
- Verify Swagger documentation accurately reflects the endpoints.
