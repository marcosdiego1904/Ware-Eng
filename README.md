## Ware Intelligence Platform

An end-to-end warehouse intelligence platform that analyzes inventory spreadsheets to detect operational anomalies, enforce configurable business rules, and provide actionable insights through a modern web UI.

### Highlights
- Intelligent anomaly detection: floating pallets, lot stragglers, over-capacity, unknown/missing locations, product-location mismatches
- Dynamic rules engine: Excel rules support plus database-driven, template-based rules with performance tracking
- JWT authentication, report history, and status workflows
- Health checks, monitoring, and deployment diagnostics
- Production-ready: CORS, auto-migrations, Postgres in prod, SQLite in dev


## Architecture

- `backend/` — Flask API (Python), SQLAlchemy models, enhanced rule engine, migrations, monitoring, debug tooling
- `frontend/` — Next.js App Router (React), UI components, rule builders and dashboards, Axios client
- `instance/` — Local SQLite database for development
- `backend/data/` — Sample inventory and rules spreadsheets

Tech stack
- Backend: Python 3.x, Flask, SQLAlchemy, Pandas, PyJWT
- Frontend: Next.js 15, React 19, TypeScript, Tailwind, Radix UI
- Database: SQLite (dev), PostgreSQL (prod)


## Quick Start

Prerequisites
- Python 3.10+ (3.11 recommended)
- Node.js 20+ (LTS)

1) Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Create .env
echo FLASK_SECRET_KEY=change-me-super-secret > .env
echo ALLOWED_ORIGINS=http://localhost:3000 >> .env
# Optionally: DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Start API (http://localhost:5000)
python run_server.py
```

2) Frontend
```bash
cd frontend
npm install

# Create .env.local
echo NEXT_PUBLIC_API_URL=http://localhost:5000/api/v1 > .env.local

npm run dev  # http://localhost:3000
```

Smoke test
```bash
# Health check
curl http://localhost:5000/api/v1/health | jq

# Register and login
curl -X POST http://localhost:5000/api/v1/auth/register -H "Content-Type: application/json" -d '{"username":"tester","password":"secret123"}'
curl -X POST http://localhost:5000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"tester","password":"secret123"}'
```


## Configuration

Backend environment
- `FLASK_SECRET_KEY` (required): Secret key for JWT signing
- `ALLOWED_ORIGINS` (optional): Comma-separated origins for CORS. Defaults include localhost and Vercel domains
- `DATABASE_URL` (optional): PostgreSQL URL in production; falls back to SQLite in dev
- `RENDER`/`VERCEL` (optional): Set by platform to adjust paths and DB handling
- `UPLOAD_MAX_SIZE` (optional): Max upload size in bytes (default 10MB)
- `DB_INIT_KEY` (optional): Secret for legacy maintenance routes

Frontend environment
- `NEXT_PUBLIC_API_URL`: API base URL, e.g., `http://localhost:5000/api/v1`


## Core Flows

Analyze an inventory spreadsheet
1. Upload `.xlsx` inventory file in the UI (Column Mapping will guide field alignment)
2. Optionally upload a custom rules file; otherwise default rules are used
3. The backend runs the enhanced rules engine and persists an Analysis Report
4. Review prioritized anomalies and location summaries

Rules engine
- Legacy mode: Excel-driven rules (`backend/data/warehouse_rules.xlsx`)
- Enhanced mode: Database-driven rules via `RuleEngine` with templates, categories, priorities, and performance tracking


## API Overview

Base URL: `/api/v1`

- Health: `GET /health`
- Auth:
  - `POST /auth/register` { username, password }
  - `POST /auth/login` { username, password } → { token }
- Reports:
  - `GET /reports` (JWT) → user reports
  - `POST /reports` (JWT, multipart/form-data)
    - fields: `inventory_file` (required), `rules_file` (optional), `column_mapping` (JSON string)
  - `GET /reports/{report_id}/details` (JWT)
- Anomalies:
  - `POST /anomalies/{id}/status` (JWT) { status, comment }

Note: Additional endpoints exist for locations, rules, templates, monitoring, and deployment diagnostics.


## Data Requirements

Inventory file (.xlsx) should include or map to typical fields:
- `pallet_id`, `location`, `creation_date`, `receipt_number`, `description`

Column mapping is handled by the UI; the backend accepts a `column_mapping` JSON that maps UI fields to source columns.


## Deployment

Frontend (Vercel)
- Standard Next.js deployment; ensure `NEXT_PUBLIC_API_URL` points to your backend URL

Backend
- Postgres in production: set `DATABASE_URL`
- CORS: set `ALLOWED_ORIGINS` to include your frontend domains
- Auto-migrations run on startup; health at `GET /api/v1/health`

Operational endpoints (for diagnostics; restrict in production)
- `GET /api/v1/deployment/health`
- `GET /api/v1/debug/dashboard`


## Repository Structure

```text
backend/
  src/
    app.py                # Flask app, API routes, health, CORS
    main.py               # Legacy Excel rules engine
    enhanced_main.py      # Enhanced DB rules engine and tooling
    rules_api.py, ...     # Rules, templates, locations, warehouse APIs
  requirements.txt
  run_server.py
frontend/
  app/                    # Next.js App Router pages
  components/             # UI modules (rules, locations, dashboard)
  lib/api.ts              # Axios client (uses NEXT_PUBLIC_API_URL)
```


## Troubleshooting

- 401 from API in UI: token missing/expired. Login again; frontend removes token and redirects to `/auth`
- CORS errors: verify `ALLOWED_ORIGINS` and that frontend points to the correct `NEXT_PUBLIC_API_URL`
- Excel parsing: ensure `.xlsx` format; keep `creation_date` parseable; validate column mapping
- DB initialization: check `GET /api/v1/health`; the app auto-runs migrations on startup


## Documentation

- Backend: `backend/README.md`, `backend/README_DEPLOYMENT.md`, `backend/DOCUMENTATION_BACKEND.md`
- Frontend: `frontend/DOCUMENTATION_FRONTEND.md`
- Advanced templates/builders: `ENHANCED_TEMPLATE_SYSTEM.md`, `Descriptions/`


## License

Proprietary. All rights reserved.


