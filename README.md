# AI Dataset Labeling Marketplace

An AI-ready web platform for managing dataset annotation projects, annotators, labeling tasks and annotation quality.

## Overview

AI Dataset Labeling Marketplace is a web-based platform designed to connect dataset owners with data annotators.

The platform allows dataset owners to create annotation projects, upload datasets, assign labeling tasks, monitor project progress, review submitted annotations and export completed labeled datasets.

Annotators receive assigned tasks through their workspace and submit labels through the platform.

The project also provides scope for AI-assisted annotation and quality-control capabilities.

## Current Status

Week 1 - Planning and Project Setup

## User Roles

- Dataset Owner
- Annotator
- Administrator

## Planned Core Features

- User Registration and Login
- Role-Based Access
- Dataset Management
- Annotation Project Management
- Annotator Assignment
- Annotation Task Management
- Annotation Workspace
- Annotation Review
- Project Progress Tracking
- Dataset Export
- Administration

## Technology Stack

### Frontend

- React
- HTML
- CSS
- JavaScript

### Backend

- Python
- FastAPI

### Database

- PostgreSQL

### ORM

- SQLAlchemy

### Validation

- Pydantic

### Testing

- Pytest

### Version Control

- Git
- GitHub

## Planned Backend Architecture

```text
Client
  |
  v
FastAPI Routers
  |
  v
Service Layer
  |
  v
Repository Layer
  |
  v
PostgreSQL