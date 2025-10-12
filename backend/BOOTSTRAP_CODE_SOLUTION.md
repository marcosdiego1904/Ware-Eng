# Bootstrap Invitation Code - Automatic Creation

## Problem
Previously, when you deleted the database during development, the invitation code `BOOTSTRAP2025` would be lost, preventing new user registration.

## Solution
The application now **automatically creates** the bootstrap invitation code when the server starts, if it doesn't already exist.

## How It Works

### Files Modified/Created:

1. **`src/db_init.py`** - New file that handles database initialization
   - Automatically creates `BOOTSTRAP2025` invitation code
   - Idempotent (safe to run multiple times)
   - Will not duplicate the code if it already exists

2. **`src/app.py`** - Modified to call database initialization on startup
   - Added import: `from db_init import init_database`
   - Calls `init_database()` after migrations run

### Bootstrap Code Details:
- **Code**: `BOOTSTRAP2025`
- **Max Uses**: 999 (effectively unlimited for development)
- **Expires**: Never
- **Purpose**: Allow initial user registration during development

## Usage

### Normal Development Workflow:
1. Delete the database if needed: `del instance\database.db`
2. Start the backend server: `python run_server.py`
3. The `BOOTSTRAP2025` code is automatically created
4. Register users using this invitation code

### Verify Bootstrap Code Exists:
```bash
python test_bootstrap_code.py
```

### Test Database Reset Simulation:
```bash
python test_db_reset.py
```

## What Happens on Server Start:

```
=== Database Initialization ===
[OK] Created bootstrap invitation code: BOOTSTRAP2025
     Max uses: 999
     Never expires
=== Database Initialization Complete ===
```

Or if the code already exists:

```
=== Database Initialization ===
[OK] Bootstrap invitation code 'BOOTSTRAP2025' already exists
=== Database Initialization Complete ===
```

## Benefits:
✅ No need to manually create invitation codes after database deletion
✅ Consistent development experience
✅ Safe for production (only creates if missing)
✅ Works with both SQLite (development) and PostgreSQL (production)

## Production Considerations:
In production, you may want to:
1. Change the bootstrap code to something more secure
2. Reduce max_uses to a reasonable number
3. Set an expiration date
4. Create additional invitation codes for different users/teams

To customize, edit the values in `src/db_init.py`:
```python
BOOTSTRAP_CODE = 'BOOTSTRAP2025'  # Change this
max_uses=999,                      # Change this
expires_at=None,                   # Add expiration if needed
```
