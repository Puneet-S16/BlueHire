# Engineering Decisions Log

This document records the architectural and technical decisions made during the development of BlueHire.

---

### 1. Repository Pattern
**Reason**: Coupling database queries directly to API endpoints or services makes testing difficult and ties business logic to SQLAlchemy.
**Benefits**: Ensures single-responsibility. Enables easy mocking of database I/O during unit testing. Protects the application layer from ORM changes.
**Future Notes**: If we switch from Sync SQLAlchemy to Async SQLAlchemy in the future, only the Repositories need modifying, leaving Services intact.

### 2. Service Layer Isolation
**Reason**: Complex workflows (like registration or token rotation) span multiple domains (Security, User Repo, Email).
**Benefits**: Services encapsulate pure business logic. They do not know about HTTP requests or FastAPI routers. They accept raw data/schemas, throw domain exceptions, and return schemas.

### 3. Argon2 Password Hashing
**Reason**: Required a highly secure, memory-hard hashing algorithm resistant to GPU brute-forcing.
**Benefits**: `pwdlib[argon2]` provides state-of-the-art security, significantly outperforming bcrypt in resistance to modern hardware attacks.

### 4. Dual JWT Strategy
**Reason**: Need stateless horizontal scaling for APIs but require a mechanism to securely revoke compromised sessions.
**Benefits**: 
- Access Tokens (15m) are fast and require no DB lookups.
- Refresh Tokens (7d) contain a `jti` and can be blacklisted or rotated, enforcing session control.

### 5. Shared RoleEnum
**Reason**: Mismatches between API validation layers and Database constraints cause silent bugs.
**Benefits**: Using the exact same `RoleEnum` inside the SQLAlchemy `User` model and the Pydantic `SignupRequest` guarantees structural parity end-to-end.

### 6. Clean Architecture Folder Structure
**Reason**: "Fat endpoints" lead to unmaintainable spaghetti code.
**Benefits**: By organizing folders by layer (`api/`, `core/`, `models/`, `repositories/`, `schemas/`, `services/`), developers instantly know where logic belongs.

### 7. Explicit Domain Exception Mapping
**Reason**: Exposing database errors or cryptographic decoding errors to clients poses a massive security threat.
**Benefits**: Services throw domain exceptions (`DuplicateEmailError`). Routers catch these and explicitly map them to standardized HTTP responses (`409 Conflict`), masking internal logic.

### 8. Transaction Try/Except Wrappers
**Reason**: Uncaught `IntegrityError` exceptions permanently break the active SQLAlchemy `Session`.
**Benefits**: By wrapping `.commit()` inside a `try/except` and triggering `.rollback()`, the application remains stable and the session is cleansed for subsequent requests.

### 9. Pydantic V2
**Reason**: Next-generation validation speed and stricter typing.
**Benefits**: Allowed the use of `@model_validator(mode="after")` to seamlessly validate complex, multi-field rules like password confirmation and strong regex complexity policies.
