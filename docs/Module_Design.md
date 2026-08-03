# Module Design

## Project Title

AI Dataset Labeling Marketplace

## 1. Overview

The backend of the AI Dataset Labeling Marketplace follows a modular layered architecture.

Each module has a specific responsibility so that API handling, business logic, database operations, data validation and configuration remain separated.

The main backend modules are:

1. API Layer
2. Service Layer
3. Repository Layer
4. Model Layer
5. Schema Layer
6. Core Layer

---

## 2. API Layer

Location:

`backend/app/api/`

### Responsibilities

- Define FastAPI routes
- Receive HTTP requests
- Validate request data using schemas
- Call the appropriate service
- Return HTTP responses

### Planned API Areas

- Authentication
- Users
- Projects
- Datasets
- Annotation Tasks
- Annotations

The API layer should not contain direct database access logic.

---

## 3. Service Layer

Location:

`backend/app/services/`

### Responsibilities

- Implement application business logic
- Coordinate operations between API and repository layers
- Apply application rules
- Handle project operations
- Handle dataset operations
- Handle annotation workflows

Example flow:

`API → Service → Repository`

---

## 4. Repository Layer

Location:

`backend/app/repositories/`

### Responsibilities

- Communicate with the database
- Create records
- Retrieve records
- Update records
- Delete records
- Execute database queries through SQLAlchemy

The repository layer separates database access from business logic.

---

## 5. Model Layer

Location:

`backend/app/models/`

### Responsibilities

- Define SQLAlchemy ORM models
- Represent database tables
- Define table relationships
- Define primary keys
- Define foreign keys

### Planned Models

- User
- Project
- Dataset
- DataItem
- AnnotationTask
- Annotation

These models correspond to the entities defined in the ER diagram.

---

## 6. Schema Layer

Location:

`backend/app/schemas/`

### Responsibilities

- Define Pydantic models
- Validate incoming API data
- Define request structures
- Define response structures
- Control data exchanged through the API

Database models and API schemas are kept separate.

---

## 7. Core Layer

Location:

`backend/app/core/`

### Responsibilities

The Core Layer contains common application configuration.

### Planned Components

#### Configuration

`config.py`

Responsible for:

- Application settings
- Environment variables
- Database URL
- Other configuration values

#### Database

`database.py`

Responsible for:

- SQLAlchemy engine creation
- Database session configuration
- Database connection management

Future security-related configuration may also be placed inside the Core Layer.

---

## 8. FastAPI Application Entry Point

Location:

`backend/app/main.py`

### Responsibilities

- Create the FastAPI application
- Configure the application
- Register API routers
- Provide initial application endpoints

The application will be started through this module.

---

## 9. Module Communication

The normal backend request flow is:

User

↓

React Frontend

↓

FastAPI API Layer

↓

Service Layer

↓

Repository Layer

↓

SQLAlchemy Model Layer

↓

PostgreSQL Database

The response returns through the same layers.

---

## 10. Proposed Backend Structure

```text
backend/
└── app/
    ├── __init__.py
    ├── main.py
    │
    ├── api/
    │   └── __init__.py
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py
    │   └── database.py
    │
    ├── models/
    │   └── __init__.py
    │
    ├── repositories/
    │   └── __init__.py
    │
    ├── schemas/
    │   └── __init__.py
    │
    └── services/
        └── __init__.py