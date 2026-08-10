# Portfolio Web Application Backend

Production-style backend API powering my personal software engineering portfolio.

The backend is responsible for managing portfolio projects, technologies, skills, project images, and the relationships between these resources. It is designed using layered architecture and provides a RESTful API for the portfolio frontend.

---

## Overview

This project is the backend service for my personal portfolio web application.

The application is built with Python and FastAPI and uses PostgreSQL for persistent data storage. The backend follows a layered architecture that separates API routing, request validation, business logic, database access, and persistence models.

The goal of this project is to demonstrate practical backend software engineering rather than simply creating a collection of API endpoints.

Key areas demonstrated include:

- REST API development
- Layered application architecture
- Database design and relational modeling
- SQLAlchemy ORM
- Pydantic validation
- Repository pattern
- Service layer architecture
- Dependency injection
- Custom exception handling
- CRUD operations
- Database migrations with Alembic
- PostgreSQL database management
- API documentation through FastAPI
- Seed data management

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Uvicorn
- Alembic

### Database

- PostgreSQL
- pgAdmin 4

### Development

- Git
- GitHub
- VS Code

---

## Architecture

The backend uses a layered architecture to separate responsibilities within the application.

```text
Client
  │
  ▼
FastAPI API Routes
  │
  ▼
Schemas / Validation
  │
  ▼
Service Layer
  │
  ▼
Repository Layer
  │
  ▼
SQLAlchemy ORM
  │
  ▼
PostgreSQL