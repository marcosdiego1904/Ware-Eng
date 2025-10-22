# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Flask API)

**Prerequisites**: PostgreSQL 18.0+ must be installed and running. See `/backend/SETUP.md` for detailed setup.

```bash
# Navigate to backend directory
cd backend

# Setup virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (REQUIRED)
# Copy .env.example to .env and set DATABASE_URL
copy .env.example .env
# Edit .env and set: DATABASE_URL=postgresql://postgres:password@localhost:5432/ware_eng_dev

# Initialize database
python src/migrate.py

# Run development server
python run_server.py
# Server runs on http://localhost:5000
# API endpoints: http://localhost:5000/api/v1/
# Dashboard: http://localhost:5000/dashboard
```

### Frontend (Next.js)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server with Turbopack
npm run dev
# Frontend runs on http://localhost:3000

# Build for production
npm run build

# Lint code
npm run lint
```

## Project Architecture

### Core System
This is a **Warehouse Intelligence Engine** - a full-stack web application for analyzing warehouse inventory reports and detecting operational anomalies based on configurable business rules.

### Technology Stack
- **Backend**: Flask (Python) with SQLAlchemy ORM, JWT authentication, CORS-enabled REST API
- **Frontend**: Next.js 15 (React 19) with TypeScript, Tailwind CSS, Zustand state management
- **Database**: PostgreSQL (required for both development and production)
- **Data Processing**: Pandas for Excel/CSV analysis
- **UI**: Radix UI components with custom design system

**Important**: This application requires PostgreSQL for both development and production to ensure complete dev/prod parity. SQLite is no longer supported.

### Key Components

#### Backend Structure (`/backend/src/`)
- **`app.py`**: Main Flask application with CORS, JWT auth, and API blueprint
- **`rule_engine.py`**: Dynamic rule evaluation system - core business logic for anomaly detection
- **`models.py`**: SQLAlchemy models for users, rules, locations, and performance tracking
- **`rules_api.py`**: REST API endpoints for rule management
- **`main.py`**: Legacy analysis engine (being replaced by rule_engine.py)
- **`enhanced_main.py`**: Enhanced analysis capabilities with lazy loading

#### Frontend Structure (`/frontend/`)
- **`/app`**: Next.js App Router structure with pages for auth, dashboard, debug, and testing
- **`/components`**: Feature-organized components:
  - `dashboard/`: Main dashboard views, sidebar, charts, heatmaps
  - `rules/`: Rule management, visual builder, AI-powered rule creation
  - `analysis/`: File upload, column mapping, processing status
  - `ui/`: Reusable UI components (buttons, dialogs, forms)
- **`/lib`**: API clients (`api.ts`, `rules-api.ts`), auth context, state stores

### Authentication & API Communication
- **JWT-based authentication** with token storage in localStorage
- **CORS-enabled API** with support for multiple origins (localhost + Vercel)
- **API base URL**: `http://localhost:5000/api/v1` (development)
- **Axios interceptors** for automatic token attachment and auth error handling

### Rule System Architecture
The application features a **dynamic rule engine** that evaluates warehouse rules against inventory data:

1. **Rule Storage**: Rules are stored in database with JSON conditions
2. **Rule Evaluators**: Modular evaluators for different anomaly types:
   - Stagnant pallets, lot stragglers, overcapacity
   - Location mapping errors, temperature zone mismatches
   - Data integrity checks
3. **Rule Categories**: Rules are categorized with priority levels (Very High, High, Medium, Low)
4. **Performance Tracking**: Rule execution times and success rates are monitored

### State Management
- **Zustand stores**: `rules-store.ts`, `store.ts`, `store-enhanced.ts`
- **React Context**: `auth-context.tsx` for authentication state
- **Local storage**: Auth tokens and user preferences

### Development Patterns
- **TypeScript throughout frontend** with strict type checking
- **Component composition** using Radix UI primitives
- **Tailwind utility classes** with `clsx` for conditional styling
- **Error boundaries** and toast notifications for user feedback
- **File upload handling** with react-dropzone and server-side processing

### Testing & Debug Components
The project includes extensive debugging and testing infrastructure:
- Debug pages for API testing, auth verification, rule validation
- Visual rule builder with debug capabilities
- AI-powered rule creation with validation
- Hook isolation testing and nuclear testing options

### Data Flow
1. **File Upload**: Users upload Excel/CSV inventory reports
2. **Column Mapping**: Frontend guides users through mapping spreadsheet columns to expected fields
3. **Rule Processing**: Backend applies configured rules using the rule engine
4. **Anomaly Detection**: System identifies warehouse operational issues
5. **Prioritized Results**: Frontend displays categorized anomalies with priority levels

### Key Files to Understand
- `backend/src/app.py:92-110` - JWT authentication decorator
- `backend/src/rule_engine.py:30-50` - Core rule evaluation system
- `frontend/lib/api.ts:11-45` - API request/response interceptors
- `frontend/components/dashboard/warehouse-dashboard.tsx` - Main dashboard component
- `frontend/components/rules/enhanced-visual-builder.tsx` - Advanced rule creation interface