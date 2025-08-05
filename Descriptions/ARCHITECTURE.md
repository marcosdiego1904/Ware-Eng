# Project Architecture Overview

This document provides a high-level overview of the project's architecture, technology stack, and development environment setup.

## 1. Core Philosophy

The project is a modern web application designed for warehouse management and optimization. It follows a classic client-server architecture with a distinct separation between the frontend and backend.

- **Backend:** A Python-based REST API responsible for business logic, data processing, and database interactions.
- **Frontend:** A modern TypeScript-based Single Page Application (SPA) that provides a rich, interactive user interface.

## 2. Technology Stack

### Backend (Python)

- **Framework:** Flask
- **Database:** PostgreSQL (using Flask-SQLAlchemy as the ORM)
- **Data Processing:** Pandas for handling and analyzing inventory data from Excel/CSV files.
- **Authentication:** JSON Web Tokens (JWT) for securing API endpoints.
- **Server:** Gunicorn is listed, intended for production deployments.

### Frontend (TypeScript)

- **Framework:** Next.js (with Turbopack) / React
- **State Management:** Zustand (a lightweight, modern state management library) and React Context API (`auth-context.tsx`).
- **Styling:** Tailwind CSS, with utility classes managed by `clsx` and `tailwind-merge`.
- **UI Components:** A mix of custom components and primitives from Radix UI (e.g., Dialog, Dropdown, Avatar), indicating a design system approach.
- **Data Fetching:** Axios for making HTTP requests to the backend API.
- **Charts/Visualizations:** Chart.js for rendering charts and graphs.
- **File Handling:** `react-dropzone` for file uploads and `xlsx` for client-side Excel file processing.

## 3. Project Structure

- **`/backend`**: Contains the Flask application.
  - **`/src`**: The main application source code.
    - **`app.py`**: The main Flask application entry point.
    - **`models.py`**: Defines the database schema.
    - **`rule_engine.py`**: The core logic for the warehouse rule system.
    - **`rules_api.py`**: The API endpoints for managing rules.
  - **`/data`**: Contains sample data files for testing.
  - **`requirements.txt`**: Lists the Python dependencies.

- **`/frontend`**: Contains the Next.js application.
  - **`/app`**: The main application source code, using the Next.js App Router.
  - **`/components`**: Reusable React components, organized by feature (e.g., `dashboard`, `rules`, `ui`).
  - **`/lib`**: Contains shared utilities, API interaction logic (`api.ts`, `rules-api.ts`), and state management stores (`rules-store.ts`, `auth-context.tsx`).
  - **`package.json`**: Lists the Node.js dependencies.

## 4. Communication Flow

1.  The **Frontend** application, running in the user's browser, makes API calls to the **Backend**.
2.  The **Backend** receives these requests, performs the necessary business logic (e.g., evaluating rules, querying the database), and sends a JSON response back to the frontend.
3.  For protected endpoints, the frontend includes a JWT in the `Authorization` header of its API requests.

## 5. Development Environment Setup

### Backend Setup

1.  Navigate to the `backend` directory: `cd backend`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Create a `.env` file (copy from `.env.example`) and configure the database connection string.
6.  Run the development server: `flask run`

### Frontend Setup

1.  Navigate to the `frontend` directory: `cd frontend`
2.  Install dependencies: `npm install`
3.  Run the development server: `npm run dev`
4.  The frontend will be available at `http://localhost:3000`.
