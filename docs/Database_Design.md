# Database Design

## Project

AI Dataset Labeling Marketplace

## 1. Overview

The database stores the core information required by the AI Dataset Labeling Marketplace.

The initial database design contains six main entities:

1. User
2. Project
3. Dataset
4. DataItem
5. AnnotationTask
6. Annotation

PostgreSQL will be used as the relational database.

---

## 2. User Entity

The User entity stores information about people using the platform.

A user can act as a Dataset Owner or an Annotator.

### Attributes

- user_id - Primary Key
- name
- email
- password_hash
- role
- created_at

### Role Values

Examples:

- owner
- annotator

---

## 3. Project Entity

The Project entity represents a dataset labeling project created by a Dataset Owner.

### Attributes

- project_id - Primary Key
- owner_id - Foreign Key referencing User
- title
- description
- status
- created_at

### Relationship

One User can own many Projects.

One Project belongs to one Dataset Owner.

---

## 4. Dataset Entity

The Dataset entity stores information about a dataset uploaded for a labeling project.

### Attributes

- dataset_id - Primary Key
- project_id - Foreign Key referencing Project
- name
- description
- data_type
- created_at

### Relationship

One Project can contain many Datasets.

One Dataset belongs to one Project.

---

## 5. DataItem Entity

A DataItem represents an individual item inside a dataset that needs to be labeled.

Examples include:

- One image
- One text record
- One document
- One data sample

### Attributes

- item_id - Primary Key
- dataset_id - Foreign Key referencing Dataset
- content_path
- status
- created_at

### Relationship

One Dataset can contain many DataItems.

One DataItem belongs to one Dataset.

---

## 6. AnnotationTask Entity

The AnnotationTask entity represents a labeling task assigned or made available to an annotator.

### Attributes

- task_id - Primary Key
- item_id - Foreign Key referencing DataItem
- annotator_id - Foreign Key referencing User
- status
- assigned_at
- completed_at

### Relationship

One DataItem can have multiple AnnotationTasks.

One Annotator can work on multiple AnnotationTasks.

---

## 7. Annotation Entity

The Annotation entity stores the actual label submitted by an annotator.

### Attributes

- annotation_id - Primary Key
- task_id - Foreign Key referencing AnnotationTask
- label
- confidence_score
- submitted_at

### Relationship

An Annotation belongs to an AnnotationTask.

An AnnotationTask produces an Annotation after the annotator completes the labeling work.

---

## 8. Main Relationships

The main relationships are:

User
→ creates
→ Project

Project
→ contains
→ Dataset

Dataset
→ contains
→ DataItem

DataItem
→ generates
→ AnnotationTask

User (Annotator)
→ works on
→ AnnotationTask

AnnotationTask
→ produces
→ Annotation

---

## 9. Relationship Summary

### User to Project

One-to-Many

One Dataset Owner can create multiple Projects.

### Project to Dataset

One-to-Many

One Project can contain multiple Datasets.

### Dataset to DataItem

One-to-Many

One Dataset can contain multiple DataItems.

### DataItem to AnnotationTask

One-to-Many

One DataItem can be assigned through multiple AnnotationTasks.

### User to AnnotationTask

One-to-Many

One Annotator can work on multiple AnnotationTasks.

### AnnotationTask to Annotation

The initial system treats a completed AnnotationTask as producing one Annotation.

---

## 10. Database Technology

Database:

PostgreSQL

ORM:

SQLAlchemy

The database schema will later be implemented using SQLAlchemy models in the FastAPI backend.