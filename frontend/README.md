# AI Dataset Labeling Marketplace

> A web-based marketplace for connecting dataset owners with annotators to organize datasets, create labeling jobs, and assign annotation work through a secure and persistent platform.

---

## 1. Overview

The AI Dataset Labeling Marketplace is a web application designed to simplify the process of preparing datasets for machine learning and artificial intelligence projects.

Dataset owners can manage datasets and create labeling jobs, while annotators can be assigned to available jobs. The platform provides a structured workflow for managing datasets, labeling jobs, and job assignments while maintaining persistent information in a PostgreSQL database.

The current implementation focuses on the core marketplace workflow and establishes the foundation for future annotation, review, authorization, testing, deployment, and AI-assisted features.

### Current Development Status

**Phase:** Phase 2 — Full Development  
**Week:** Week 3  
**Capstone Day:** Day 17  
**Status:** Core backend APIs and frontend integration in progress

---

## 2. Architecture Diagram

The system follows a layered web application architecture:

```text
Users
  |
  v
React Frontend
  |
  | REST API
  v
FastAPI Backend
  |
  +----------------------+
  |                      |
  v                      v
Service Layer       Authentication
  |                      |
  v                      v
Repository Layer      JWT
  |
  v
SQLAlchemy ORM
  |
  v
PostgreSQL Database