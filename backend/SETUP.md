# Backend Setup Guide

## Prerequisites

### Required Software
- **Python 3.13** or higher
- **PostgreSQL 18.0** or higher
- **Git** for version control

## Quick Start (5 minutes)

### 1. Install PostgreSQL

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql@18
brew services start postgresql@18
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create the development database
CREATE DATABASE ware_eng_dev;

# Exit PostgreSQL
\q
```

### 3. Clone and Configure

```bash
# Clone repository (if not already done)
git clone <your-repo-url>
cd backend

# Copy environment template
copy .env.example .env  # Windows
# OR
cp .env.example .env    # macOS/Linux

# Edit .env file and set your DATABASE_URL:
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ware_eng_dev
```

### 4. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate     # Windows
# OR
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Run migrations (creates all tables)
python src/migrate.py
```

### 6. Start Development Server

```bash
python run_server.py
```

The API will be available at: `http://localhost:5000`

## Verification

Test that everything is working:

```bash
# Run comprehensive tests
python comprehensive_test.py

# Expected output:
# [PASS] TEST 1: Database Connection & Configuration
# [PASS] TEST 2: Models and Basic Queries
# [PASS] TEST 3: JSON Field Storage and Retrieval
# [PASS] TEST 4: DateTime with Timezone Handling
# [PASS] TEST 5: Foreign Key Constraints
# [PASS] TEST 6: Boolean Field Handling
# [PASS] TEST 7: Database Indexes
# Results: 7/7 tests passed
```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/ware_eng_dev` |
| `FLASK_SECRET_KEY` | Secure random key for Flask sessions | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000,https://your-app.vercel.app` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_INIT_KEY` | Key for database initialization endpoint | - |
| `UPLOAD_MAX_SIZE` | Maximum file upload size in bytes | `10485760` (10MB) |

## Database Management

### Reset Database
```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE ware_eng_dev;"
psql -U postgres -c "CREATE DATABASE ware_eng_dev;"

# Re-run migrations
python src/migrate.py
```

### View Database
```bash
# Connect to database
psql -U postgres -d ware_eng_dev

# List all tables
\dt

# View table structure
\d table_name

# Exit
\q
```

### Backup Database
```bash
# Create backup
pg_dump -U postgres ware_eng_dev > backup.sql

# Restore backup
psql -U postgres ware_eng_dev < backup.sql
```

## Troubleshooting

### "DATABASE_URL environment variable is required"

**Solution:** Make sure you have a `.env` file in the `backend/` directory with `DATABASE_URL` set.

```bash
# Check if .env exists
ls -la .env

# If not, copy from template
cp .env.example .env
```

### "Connection refused" or "Could not connect to PostgreSQL"

**Solution:** Ensure PostgreSQL is running.

**Windows:**
```bash
# Check service status
sc query postgresql-x64-18

# Start service if stopped
net start postgresql-x64-18
```

**macOS:**
```bash
brew services list
brew services start postgresql@18
```

**Linux:**
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### "Password authentication failed"

**Solution:** Update your DATABASE_URL with the correct password.

```bash
# Reset PostgreSQL password (if needed)
psql -U postgres
ALTER USER postgres PASSWORD 'newpassword';
\q

# Update .env
DATABASE_URL=postgresql://postgres:newpassword@localhost:5432/ware_eng_dev
```

### "Database does not exist"

**Solution:** Create the database.

```bash
psql -U postgres -c "CREATE DATABASE ware_eng_dev;"
```

## Production Deployment

### Render.com

1. Create new Web Service
2. Connect your GitHub repository
3. Set environment variables:
   - `DATABASE_URL` - (automatically provided by Render PostgreSQL addon)
   - `FLASK_SECRET_KEY` - Generate securely
   - `ALLOWED_ORIGINS` - Your frontend URL

4. Deploy will happen automatically on push to main branch

### Other Platforms (Heroku, Railway, etc.)

1. Add PostgreSQL addon/service
2. Set environment variables (same as above)
3. Ensure `DATABASE_URL` is set
4. Deploy

## Why PostgreSQL Only?

Previously, this application supported both SQLite (development) and PostgreSQL (production). This created several issues:

- ❌ Dev/prod behavior differences
- ❌ SQLite-specific bugs discovered only in production
- ❌ Different JSON handling, DateTime timezone handling, boolean types
- ❌ Difficult to reproduce production issues locally

By using PostgreSQL everywhere:

- ✅ Dev = Prod parity (what you test is what you deploy)
- ✅ Catch issues early in development
- ✅ Simpler codebase (no database-specific conditionals)
- ✅ Better performance testing
- ✅ Easier debugging

## Next Steps

1. ✅ Backend is running on `http://localhost:5000`
2. 🔄 Set up frontend (see `/frontend/README.md`)
3. 📖 Read API documentation (see `DOCUMENTATION_BACKEND.md`)
4. 🧪 Explore test suite (see `comprehensive_test.py`)

## Getting Help

- **Documentation:** See `/backend/DOCUMENTATION_BACKEND.md`
- **Migration History:** See `/backend/MIGRATION_CHANGELOG.md`
- **Issues:** Create a GitHub issue with details

---

**Last Updated:** October 16, 2025
**PostgreSQL Version:** 18.0
**Python Version:** 3.13
