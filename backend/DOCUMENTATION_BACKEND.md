# Backend Documentation

This document provides an overview of the backend application, including its API endpoints, database schema, and core logic.

## 1. API Overview

The backend is a Flask application that exposes a REST API under the `/api/v1` prefix. All API endpoints require a JSON Web Token (JWT) for authentication, which must be passed in the `Authorization` header as a Bearer token.

### Main Endpoints

- **Authentication:**
  - `POST /api/v1/auth/login`: Authenticates a user and returns a JWT.
  - `POST /api/v1/auth/register`: Creates a new user account.

- **Analysis Reports:**
  - `GET /api/v1/reports`: Retrieves a list of all analysis reports for the authenticated user.
  - `POST /api/v1/reports`: Creates a new analysis report by uploading an inventory file and specifying column mappings.
  - `GET /api/v1/reports/<report_id>/details`: Retrieves the detailed results of a specific analysis report, including a list of all anomalies.

- **Anomaly Management:**
  - `POST /api/v1/anomalies/<anomaly_id>/status`: Updates the status of a specific anomaly (e.g., from 'New' to 'Resolved').

- **Rule System:**
  - A comprehensive set of endpoints for managing the rule system is available under `/api/v1/rules`. See the `rule_system_documentation.txt` file for details.

- **Health & Admin:**
  - `GET /api/v1/health`: A health check endpoint that verifies the database connection and rule system status.
  - `GET /api/v1/admin/migrations`: Retrieves the status of database migrations.
  - `POST /api/v1/admin/migrations/run`: Manually triggers the execution of pending database migrations.

## 2. Database Schema

The application uses a PostgreSQL database (or SQLite in development) with the following core models defined in `core_models.py` and `models.py`:

### `User`
- **Purpose:** Stores user account information.
- **Key Columns:**
  - `id`: Primary key.
  - `username`: The user's unique username.
  - `password_hash`: The user's hashed password.

### `AnalysisReport`
- **Purpose:** Represents a single analysis run.
- **Key Columns:**
  - `id`: Primary key.
  - `report_name`: The name of the report.
  - `timestamp`: The date and time the report was created.
  - `user_id`: A foreign key linking the report to a `User`.
  - `location_summary`: A JSON string containing a summary of anomalies by location.

### `Anomaly`
- **Purpose:** Stores a single anomaly (rule violation) found in a report.
- **Key Columns:**
  - `id`: Primary key.
  - `description`: A brief description of the anomaly type.
  - `details`: A JSON string containing the full details of the anomaly.
  - `status`: The current status of the anomaly (e.g., 'New', 'Resolved').
  - `report_id`: A foreign key linking the anomaly to an `AnalysisReport`.

### `AnomalyHistory`
- **Purpose:** Tracks the status changes for an anomaly over time.
- **Key Columns:**
  - `id`: Primary key.
  - `old_status`: The previous status.
  - `new_status`: The new status.
  - `comment`: A user-provided comment about the status change.
  - `anomaly_id`: A foreign key linking to an `Anomaly`.
  - `user_id`: A foreign key linking to the `User` who made the change.

For details on the rule system tables (`Rule`, `RuleCategory`, `Location`, etc.), please refer to the `rule_system_documentation.txt` file.

## 3. Authentication Flow

1.  The user submits their `username` and `password` to the `POST /api/v1/auth/login` endpoint.
2.  The server validates the credentials.
3.  If the credentials are valid, the server generates a JWT that includes the `user_id` and an expiration time.
4.  The server sends the JWT back to the client.
5.  The client must then include this JWT in the `Authorization` header for all subsequent requests to protected endpoints (e.g., `Authorization: Bearer <token>`).
6.  The `token_required` decorator in `app.py` intercepts each request, validates the token, and retrieves the corresponding user from the database.

## 4. Core Logic: The Analysis Engine

The primary function of the backend is to analyze inventory data. This is handled by the `run_enhanced_engine` function in `enhanced_main.py`.

- **Input:** The engine takes a Pandas DataFrame of inventory data, a set of rules, and column mappings.
- **Process:** It uses the `RuleEngine` to evaluate the active rules against the inventory data.
- **Output:** It returns a list of anomaly dictionaries, which are then stored in the database as `Anomaly` records linked to a new `AnalysisReport`.
