# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to the project maintainers. All security vulnerabilities will be promptly addressed.

Please do not report security vulnerabilities through public GitHub issues.

## Security Considerations

This application handles warehouse data and requires proper security measures:

1. **Environment Variables**: Never commit sensitive information like secret keys to version control
2. **File Uploads**: Only Excel files (.xlsx, .xls) are accepted for analysis
3. **Authentication**: JWT tokens are used for API authentication
4. **Database**: Use secure database connections in production
5. **HTTPS**: Always use HTTPS in production environments

## Development vs Production

### Development
- Uses SQLite database stored locally
- Accepts localhost CORS origins
- Debug mode may be enabled

### Production
- Should use PostgreSQL or similar production database
- Requires proper SSL/TLS certificates
- All environment variables must be set
- File uploads should be scanned and validated

## Required Environment Variables

See `.env.example` for a complete list of required environment variables.