# Domain Study

## 1. Introduction

Dataset labeling is the process of assigning meaningful labels or annotations to raw data so that the data can be used for training, validating and evaluating machine learning models.

High-quality labeled data is an important requirement for supervised machine learning applications.

## 2. Problem Domain

Organizations working with machine learning may have large amounts of raw data that need to be annotated before the data can be used for model development.

Managing this process manually can create problems such as:

- Difficulty distributing annotation work
- Difficulty monitoring progress
- Inconsistent annotations
- Lack of centralized quality review
- Difficulty managing multiple annotators
- Difficulty exporting completed labeled datasets

## 3. Dataset Owner

A Dataset Owner is a user or organization that owns raw data requiring annotation.

The Dataset Owner can create projects, upload datasets, define labeling requirements, assign work, monitor progress and review completed annotations.

## 4. Annotator

An Annotator performs labeling tasks.

The annotator receives assigned tasks, examines the provided data and submits the required labels through the platform.

## 5. Administrator

The Administrator manages platform-level activities.

Administrative responsibilities may include user management, project monitoring and maintaining platform operations.

## 6. Basic Workflow

Dataset Owner
→ Creates Annotation Project
→ Uploads Dataset
→ Creates Annotation Tasks
→ Tasks are Assigned to Annotators
→ Annotators Perform Labeling
→ Labels are Submitted
→ Dataset Owner Reviews Annotations
→ Approved Annotations Become Part of the Final Dataset
→ Dataset is Exported

## 7. Main Functional Areas

The planned system contains the following functional areas:

1. User Authentication
2. User and Role Management
3. Dataset Management
4. Annotation Project Management
5. Project Assignment
6. Annotation Task Management
7. Annotation Workspace
8. Annotation Review
9. Progress Monitoring
10. Dataset Export
11. Administration

## 8. Business Logic

The system contains business rules beyond basic CRUD operations.

Examples include:

- Only authorized Dataset Owners can manage their own projects.
- Annotators can access only tasks assigned to them.
- Annotation tasks move through defined statuses.
- Submitted annotations can be reviewed before approval.
- Project progress depends on completed and approved tasks.
- Completed datasets can be exported only after required annotation work is finished.

## 9. Future AI Enhancement Scope

AI will assist the labeling workflow rather than attempting to completely replace human annotators.

Possible enhancement areas include:

- AI-assisted label suggestions
- Annotation consistency checking
- Dataset quality analysis
- Detection of potentially incorrect annotations

The final enhancement will be selected according to the Capstone enhancement requirements.