# Development Log

## 04/08/2026 - Core Configuration and Database Foundation

### Work Completed

Implemented the Core Layer foundation for the AI Dataset Labeling Marketplace backend.

### Configuration Management

Created `backend/app/core/config.py`.

Implemented application configuration using Pydantic Settings.

The configuration currently supports:

- Database URL
- Secret key
- JWT algorithm
- Access-token expiration time
- Environment-based configuration using `.env`

The `.env.example` file remains the public configuration template, while real environment values can be stored separately in `.env`.

### Database Foundation

Created `backend/app/core/database.py`.

Implemented:

- SQLAlchemy engine
- PostgreSQL database dialect configuration
- Session factory using `sessionmaker`
- SQLAlchemy declarative base
- Database-session dependency using `get_db()`
- Automatic session closing

### Automated Tests

Created:

- `tests/__init__.py`
- `tests/test_config.py`
- `tests/test_database.py`

The configuration test verified:

- Database URL configuration
- JWT algorithm configuration
- Access-token expiration configuration

The database configuration test verified:

- SQLAlchemy engine creation
- PostgreSQL dialect recognition
- Session factory configuration
- Declarative ORM base configuration

### FastAPI Regression Testing

The FastAPI application was started successfully after the Core Layer changes.

Verified:

- `GET /`
- `GET /health`
- Swagger documentation at `/docs`

All existing API functionality continued to operate correctly.

### Important Note

The current database test verifies SQLAlchemy configuration and PostgreSQL dialect setup.

It does not yet verify a live connection to a PostgreSQL server.

### Current Backend Flow

FastAPI Application

↓

Core Configuration

↓

SQLAlchemy Engine / Session

↓

Future ORM Models

↓

PostgreSQL

### Next Milestone

Continue database development by introducing the required SQLAlchemy ORM models and relationships based on the approved ER design.

## 05/08/2026 - User ORM Model and Validation Schemas

### Work Completed

Implemented the initial User data layer for the AI Dataset Labeling Marketplace.

### User ORM Model

Created:

`backend/app/models/user.py`

The SQLAlchemy User model contains:

- id
- name
- email
- hashed_password
- is_active
- created_at

The model includes:

- Primary key configuration
- Unique email constraint
- Email indexing
- Required fields
- Active-user status
- Account creation timestamp

### User Pydantic Schemas

Created:

`backend/app/schemas/user.py`

Implemented:

- `UserBase`
- `UserCreate`
- `UserResponse`

Validation includes:

- Name length validation
- Email format validation
- Password length validation

The public `UserResponse` schema does not expose the user's hashed password.

### Dependency Update

Added:

`email-validator`

This dependency supports Pydantic email-address validation.

### Automated Testing

Created:

`tests/test_user_model.py`

The following behaviours were tested:

1. User ORM table structure
2. Valid user creation schema
3. Invalid email rejection
4. Short password rejection
5. Safe user response schema

Result:

**5/5 tests passed**

### Regression Testing

Previously implemented configuration and database foundation tests were executed again successfully.

This confirms that introducing the User model and schemas did not break the existing backend foundation.

### Current Backend Progress

FastAPI Application

↓

Core Configuration

↓

SQLAlchemy Database Foundation

↓

User ORM Model

↓

User Pydantic Schemas

↓

Future Repository and Service Layers

### Next Milestone

Continue the data-model layer by implementing the next required marketplace entity and its relationships according to the approved ER design.