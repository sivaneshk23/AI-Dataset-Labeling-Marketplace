# System Architecture

## Project Title

AI Dataset Labeling Marketplace

## 1. Architecture Overview

The AI Dataset Labeling Marketplace is a web-based platform that connects dataset owners with annotators.

Dataset owners can create labeling projects, upload datasets and create annotation tasks.

Annotators can access available tasks, label the assigned data and submit their annotations.

The system uses a layered architecture so that the frontend, API handling, business logic and database operations remain separated.

## 2. Main Users

### Dataset Owner

The Dataset Owner can:

- Register and login
- Create labeling projects
- Upload and manage datasets
- Create annotation tasks
- Monitor annotation progress
- View submitted annotations

### Annotator

The Annotator can:

- Register and login
- View available annotation tasks
- Accept or receive tasks
- View data items
- Submit labels
- View their annotation activity

## 3. Main Architecture Layers

### 3.1 Frontend Layer

Technology:

- React

Responsibilities:

- Display the user interface
- Accept user input
- Display projects and datasets
- Display annotation tasks
- Provide the labeling interface
- Communicate with the backend using REST APIs

### 3.2 API Layer

Technology:

- FastAPI

Responsibilities:

- Receive requests from the frontend
- Validate incoming requests
- Route requests to the correct service
- Return responses to the frontend

### 3.3 Service Layer

Responsibilities:

- Handle business logic
- Manage project operations
- Manage dataset operations
- Manage annotation tasks
- Process annotation submissions
- Apply application rules

### 3.4 Repository Layer

Responsibilities:

- Handle database operations
- Create records
- Retrieve records
- Update records
- Delete records
- Keep database logic separate from business logic

### 3.5 ORM Layer

Technology:

- SQLAlchemy

Responsibilities:

- Map Python objects to database tables
- Provide communication between the backend and PostgreSQL

### 3.6 Database Layer

Technology:

- PostgreSQL

Responsibilities:

- Store users
- Store projects
- Store datasets
- Store data items
- Store annotation tasks
- Store submitted annotations

## 4. High-Level Architecture Flow

The basic communication flow is:

User
→ React Frontend
→ REST API
→ FastAPI
→ Service Layer
→ Repository Layer
→ SQLAlchemy
→ PostgreSQL

The response travels back through the same layers to the user.

## 5. Authentication Flow

User
→ Login/Register Interface
→ FastAPI Authentication API
→ Authentication Service
→ User Repository
→ PostgreSQL

After successful authentication, the system provides access according to the user's role.

## 6. Dataset Owner Flow

Dataset Owner
→ React Frontend
→ FastAPI
→ Project/Dataset Service
→ Repository
→ PostgreSQL

The owner can create and manage labeling projects and datasets.

## 7. Annotator Flow

Annotator
→ React Frontend
→ FastAPI
→ Annotation Service
→ Repository
→ PostgreSQL

The annotator can access annotation tasks and submit labels for data items.

## 8. Proposed Backend Structure

The backend will follow a layered structure:

backend/
└── app/
    ├── api/
    ├── core/
    ├── models/
    ├── repositories/
    ├── schemas/
    └── services/

### api/

Contains API routes and endpoints.

### core/

Contains common application configuration such as database and security settings.

### models/

Contains SQLAlchemy database models.

### schemas/

Contains Pydantic request and response schemas.

### services/

Contains application business logic.

### repositories/

Contains database access operations.

## 9. Architecture Goals

The architecture is designed to provide:

- Separation of concerns
- Maintainable code
- Easier testing
- Clear database access
- Modular development
- Easier future expansion