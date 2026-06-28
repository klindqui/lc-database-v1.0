# Database Roles and Permissions

## Purpose

This document defines the role-based access control (RBAC) model for the LC Database project.

Rather than assigning permissions directly to individual users, permissions are assigned to roles. Users are then assigned to one or more roles based on their responsibilities.

This approach improves security, simplifies permission management, and makes the database easier to maintain as the project grows.

---

# Role Overview

The database currently defines four primary roles:

- Administrator
- Manager
- Data Uploader
- Data Analyst

---

# Administrator

## Purpose

Responsible for complete administration of the PostgreSQL database.

This role is intended for database administrators or trusted personnel responsible for maintaining the database infrastructure.

## Permissions

- Full database access
- Create users
- Delete users
- Create roles
- Modify roles
- Grant permissions
- Revoke permissions
- Create schemas
- Delete schemas
- Create tables
- Modify tables
- Delete tables
- Manage indexes
- Manage views
- Configure database settings
- Backup and restore the database
- Read, insert, update, and delete all data

## Typical Users

- Database Administrator
- Lead Developer (if responsible for administration)

---

# Manager

## Purpose

Responsible for managing project data and database structure without administering database security.

Managers have complete control over project tables but cannot manage database users or security settings.

## Permissions

- Read data
- Insert data
- Update data
- Delete data
- Delete tables
- Create views

## Restrictions

Managers cannot:

- Create users
- Delete users
- Create roles
- Modify roles
- Grant permissions
- Change database configuration

## Typical Users

- Project Manager
- Technical Lead
- Principal Investigator

---

# Data Uploader

## Purpose

Used by the automated ingestion pipelines.

This role is intended for service accounts rather than human users.

Examples include:

- Data_6_MEMS Pipeline
- Data_Multi_TICC Pipeline

## Permissions

- Read existing data
- Insert new records
- Use database schema

## Restrictions

Cannot:

- Update existing data
- Delete data
- Create tables
- Modify tables
- Delete tables
- Create users
- Change permissions

This follows the Principle of Least Privilege by allowing pipelines to upload data without giving them unnecessary administrative capabilities.

---

# Data Analyst

## Purpose

Allows team members to explore, analyze, and export project data while protecting database integrity.

## Permissions

- Read data
- Execute queries
- Export query results

## Restrictions

Cannot:

- Insert data
- Update data
- Delete data
- Create tables
- Modify tables
- Delete tables
- Create users
- Change permissions

## Typical Users

- Researchers
- Data Scientists
- Analysts
- Team Members performing data analysis

---

# Permission Matrix

| Permission | Administrator | Manager | Data Uploader | Data Analyst |
|------------|:-------------:|:-------:|:-------------:|:------------:|
| SELECT | ✅ | ✅ | ✅ | ✅ |
| INSERT | ✅ | ✅ | ✅ | ❌ |
| UPDATE | ✅ | ✅ | ❌ | ❌ |
| DELETE | ✅ | ✅ | ❌ | ❌ |
| CREATE TABLE | ✅ | ✅ | ❌ | ❌ |
| ALTER TABLE | ✅ | ✅ | ❌ | ❌ |
| DROP TABLE | ✅ | ✅ | ❌ | ❌ |
| CREATE INDEX | ✅ | ✅ | ❌ | ❌ |
| CREATE VIEW | ✅ | ✅ | ❌ | ❌ |
| CREATE USER | ✅ | ❌ | ❌ | ❌ |
| DELETE USER | ✅ | ❌ | ❌ | ❌ |
| CREATE ROLE | ✅ | ❌ | ❌ | ❌ |
| GRANT / REVOKE PRIVILEGES | ✅ | ❌ | ❌ | ❌ |
| DATABASE CONFIGURATION | ✅ | ❌ | ❌ | ❌ |

---

# Principle of Least Privilege

Each role is granted only the permissions required to perform its intended responsibilities.

For example:

- Automated ingestion pipelines operate using the **Data Uploader** role rather than an administrative account.
- Analysts receive read-only access to prevent accidental modification of project data.
- Administrative permissions are limited to trusted database administrators.

This approach reduces security risks while simplifying permission management.

---

# Future Expansion

Additional roles may be introduced as the project grows.

Possible future roles include:

- Application User
- Read-Only Guest
- Auditor
- API Service Account
- Database Backup Operator

New roles should follow the Principle of Least Privilege and be granted only the permissions necessary for their specific responsibilities.

---

# Current Implementation Plan

The initial deployment will include the following roles:

- Administrator
- Manager
- Data Uploader
- Data Analyst

Individual user accounts will be assigned to one or more of these roles based on project responsibilities.

This role-based model provides a scalable and maintainable foundation for future database growth.

# Current Implementation

Current roles:

- db_admin
- db_manager
- data_uploader
- data_analyst

Current users:

- katherine → db_admin
- pipeline_user → data_uploader

The automated ingestion pipelines execute using the dedicated
pipeline_user service account rather than an administrator account.

This follows the Principle of Least Privilege by granting only the
permissions required to upload new data.