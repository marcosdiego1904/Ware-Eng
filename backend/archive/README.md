# Archived Scripts

This directory contains legacy scripts that are no longer needed after the transition to PostgreSQL-only development.

## Archive Date
October 16, 2025

## Reason for Archive
These scripts were created during the SQLite → PostgreSQL migration period when we were maintaining dual database support. Now that we've fully transitioned to PostgreSQL for both development and production, these scripts are obsolete.

## Archived Scripts

### Migration Scripts (No Longer Needed)
- `simple_migration.py` - Initial migration attempt
- `simple_migration_script.py` - Alternative migration approach
- `fix_postgresql_migration.py` - Migration fix attempt
- `apply_smart_config_migration.py` - Smart config migration
- `test_database_migration.py` - Migration testing
- `direct_postgresql_migration.py` - Direct migration approach
- `web_postgresql_migration.py` - Web-based migration
- `setup_postgres_simple.py` - PostgreSQL setup script (replaced by SETUP.md)

### SQLite-Specific Test Files (No Longer Relevant)
- `test_all_fixes_sqlite.py` - SQLite-specific tests
- `debug_sqlite_virtual.py` - SQLite debugging tools
- `test_database_compatibility.py` - Dual database compatibility tests

## What Replaced These Scripts

**For Setup:** See `/backend/SETUP.md` for the current PostgreSQL setup guide.

**For Migrations:** Use the standard migration system:
```bash
python src/migrate.py
```

**For Testing:** Use the comprehensive test suite:
```bash
python comprehensive_test.py
```

## Recovery

If you need to access these scripts for historical reference, they are preserved in this archive folder and in git history:

```bash
# View git history
git log --all -- backend/archive/

# Restore a specific file (if needed)
git checkout <commit-hash> -- backend/archive/<filename>
```

## Why We Transitioned to PostgreSQL-Only

1. **Dev/Prod Parity**: Eliminate differences between development and production environments
2. **Simplified Codebase**: Remove database-specific conditional logic
3. **Better Testing**: Catch production issues early in development
4. **Consistent Behavior**: Same JSON handling, DateTime timezone handling, and boolean types everywhere
5. **Easier Debugging**: Reproduce production issues locally

---

**Note**: Do not use these archived scripts in new development. They are kept for historical reference only.
