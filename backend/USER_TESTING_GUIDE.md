# User Testing Guide - Database Efficiency Features

## Overview
This guide walks you through testing all the new database efficiency features as a **normal user** (not a developer). You'll test template limits, invitation-only registration, and monitoring endpoints.

---

## Prerequisites

### Start the Backend Server:
```bash
cd backend
python src\app.py
```

Wait for the message: `Running on http://127.0.0.1:5000`

### Tools You'll Need:
- **Browser**: For some tests (Chrome/Firefox)
- **Postman** or **Thunder Client** (VS Code extension) - Recommended for API testing
- **OR curl** (command line) - For advanced users

---

## Test 1: Invitation-Only Registration 🎫

### Goal: Verify that new users CANNOT register without an invitation code

#### Step 1: Try to register WITHOUT invitation code (Should FAIL)

**Using Postman/Thunder Client:**
1. Create new request: `POST http://localhost:5000/api/v1/auth/register`
2. Set Headers: `Content-Type: application/json`
3. Body (JSON):
```json
{
  "username": "testuser1",
  "password": "password123"
}
```
4. Click "Send"

**Expected Result**: ❌ Error
```json
{
  "message": "Invitation code is required",
  "error": "invitation_required"
}
```

**Using curl:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser1\",\"password\":\"password123\"}"
```

---

#### Step 2: Try with INVALID invitation code (Should FAIL)

**Body (JSON):**
```json
{
  "username": "testuser1",
  "password": "password123",
  "invitation_code": "INVALID123"
}
```

**Expected Result**: ❌ Error
```json
{
  "message": "Invalid invitation code",
  "error": "invalid_invitation"
}
```

---

#### Step 3: Register with VALID invitation code (Should SUCCEED)

**Body (JSON):**
```json
{
  "username": "testuser1",
  "password": "password123",
  "invitation_code": "BOOTSTRAP2025"
}
```

**Expected Result**: ✅ Success
```json
{
  "message": "Account created successfully!",
  "invitation_used": "BOOTSTRAP2025"
}
```

**✅ TEST PASSED IF**:
- Step 1 failed with "invitation required"
- Step 2 failed with "invalid invitation"
- Step 3 succeeded with "account created"

---

## Test 2: Template Limit Enforcement 📦

### Goal: Verify that users can only create 5 templates

#### Setup: Login to get authentication token

**Request: `POST http://localhost:5000/api/v1/auth/login`**

**Body:**
```json
{
  "username": "testuser1",
  "password": "password123"
}
```

**Response (save the token):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Copy the token** - you'll use it in all following requests!

---

#### Step 1: Create 5 templates (Should all SUCCEED)

For each template (1-5), make this request:

**Request: `POST http://localhost:5000/api/v1/standalone-templates/create`**

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer YOUR_TOKEN_HERE` ⚠️ Replace with your actual token!

**Body for Template #1:**
```json
{
  "name": "Test Warehouse 1",
  "description": "Testing template limits",
  "num_aisles": 2,
  "racks_per_aisle": 2,
  "positions_per_rack": 10,
  "levels_per_position": 4
}
```

**Repeat 5 times**, changing the name:
- "Test Warehouse 1"
- "Test Warehouse 2"
- "Test Warehouse 3"
- "Test Warehouse 4"
- "Test Warehouse 5"

**Expected Result for each**: ✅ Success
```json
{
  "message": "Template created successfully",
  "template": {
    "id": 1,
    "name": "Test Warehouse 1",
    ...
  }
}
```

---

#### Step 2: Try to create 6th template (Should FAIL)

**Body for Template #6:**
```json
{
  "name": "Test Warehouse 6",
  "description": "This should fail",
  "num_aisles": 2,
  "racks_per_aisle": 2,
  "positions_per_rack": 10,
  "levels_per_position": 4
}
```

**Expected Result**: ❌ HTTP 403 Error
```json
{
  "error": "Maximum template limit reached",
  "message": "You have reached the maximum limit of 5 active templates per user.",
  "current_count": 5,
  "limit": 5
}
```

**✅ TEST PASSED IF**:
- First 5 templates created successfully
- 6th template was rejected with limit error

---

## Test 3: Database Monitoring 📊

### Goal: View database statistics and health

#### Step 1: Check Overall Database Statistics

**Request: `GET http://localhost:5000/api/v1/admin/db-stats`**

**Headers:**
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Expected Response:**
```json
{
  "database": {
    "type": "SQLite",
    "estimated_storage_mb": 0.5
  },
  "totals": {
    "users": 1,
    "reports": 0,
    "templates": {
      "total": 5,
      "active": 5,
      "inactive": 0
    },
    "locations": {
      "total": 100,
      "active": 100
    }
  },
  "per_user": {
    "reports": [
      {"username": "testuser1", "count": 0}
    ],
    "templates": [
      {"username": "testuser1", "count": 5}
    ]
  },
  "limits_check": {
    "users_at_report_limit": 0,
    "users_with_5plus_templates": 1
  },
  "timestamp": "2025-01-07T..."
}
```

**What to check:**
- ✅ "users": should show 1 (your new user)
- ✅ "templates.total": should show 5
- ✅ "users_with_5plus_templates": should show 1 (you!)

---

#### Step 2: Check Database Health

**Request: `GET http://localhost:5000/api/v1/admin/db-health`**

**Headers:**
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Expected Response:**
```json
{
  "status": "warnings",
  "issues": [],
  "warnings": [
    {
      "type": "template_limit_exceeded",
      "message": "1 users have more than 5 templates",
      "users": [
        {"username": "testuser1", "count": 5}
      ]
    }
  ],
  "checks_performed": 5,
  "timestamp": "2025-01-07T..."
}
```

**What to check:**
- ✅ Status shows "warnings" (because you're at the limit)
- ✅ Your username appears in warnings

---

#### Step 3: Check Your Personal Statistics

**Request: `GET http://localhost:5000/api/v1/admin/user-stats/1`**
(Replace `1` with your user ID if different)

**Headers:**
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Expected Response:**
```json
{
  "user": {
    "id": 1,
    "username": "testuser1"
  },
  "reports": {
    "total": 0,
    "last_30_days": 0,
    "limit": 3,
    "remaining": 3
  },
  "templates": {
    "total": 5,
    "limit": 5,
    "remaining": 0
  },
  "warehouses": 0,
  "activity": {
    "daily": []
  },
  "timestamp": "2025-01-07T..."
}
```

**What to check:**
- ✅ templates.total: 5
- ✅ templates.remaining: 0 (you've hit the limit!)
- ✅ reports.remaining: 3 (you haven't created reports yet)

---

## Test 4: Invitation Management 🎟️

### Goal: Create and manage invitation codes

#### Step 1: Generate a New Invitation Code

**Request: `POST http://localhost:5000/api/v1/invitations/generate`**

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Body:**
```json
{
  "max_uses": 3,
  "expires_in_days": 7,
  "notes": "Invitation for my friends"
}
```

**Expected Response:**
```json
{
  "message": "Invitation code created successfully",
  "invitation": {
    "id": 2,
    "code": "ABC123XYZ456",
    "is_active": true,
    "max_uses": 3,
    "current_uses": 0,
    "notes": "Invitation for my friends",
    "created_at": "2025-01-07T..."
  }
}
```

**Save the code** (e.g., "ABC123XYZ456") - you'll use it next!

---

#### Step 2: Validate Your Invitation Code (No Auth Required)

**Request: `GET http://localhost:5000/api/v1/invitations/validate/ABC123XYZ456`**
(Replace with your actual code)

**No headers needed** (this is a public endpoint)

**Expected Response:**
```json
{
  "valid": true,
  "message": "Valid",
  "invitation": {
    "code": "ABC123XYZ456",
    "is_active": true,
    "max_uses": 3,
    "current_uses": 0
  }
}
```

---

#### Step 3: List All Your Invitation Codes

**Request: `GET http://localhost:5000/api/v1/invitations/my-codes`**

**Headers:**
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Expected Response:**
```json
{
  "invitations": [
    {
      "id": 2,
      "code": "ABC123XYZ456",
      "is_active": true,
      "max_uses": 3,
      "current_uses": 0,
      "notes": "Invitation for my friends"
    }
  ],
  "total": 1,
  "active": 1
}
```

---

#### Step 4: Use the Invitation Code (Register New User)

**Request: `POST http://localhost:5000/api/v1/auth/register`**

**Body:**
```json
{
  "username": "frienduser",
  "password": "password123",
  "invitation_code": "ABC123XYZ456"
}
```

**Expected Response:**
```json
{
  "message": "Account created successfully!",
  "invitation_used": "ABC123XYZ456"
}
```

---

#### Step 5: Verify Invitation Was Used

**Request: `GET http://localhost:5000/api/v1/invitations/my-codes`**

**Expected Response:**
```json
{
  "invitations": [
    {
      "code": "ABC123XYZ456",
      "current_uses": 1,
      "max_uses": 3,
      "is_active": true
    }
  ]
}
```

**What to check:**
- ✅ current_uses increased from 0 to 1

---

#### Step 6: Get Invitation Statistics

**Request: `GET http://localhost:5000/api/v1/invitations/stats`**

**Headers:**
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Expected Response:**
```json
{
  "total_created": 1,
  "active_codes": 1,
  "total_uses": 1,
  "available_uses": 2
}
```

---

## Test 5: Report Limits (Existing Feature) 📈

### Goal: Verify report limit is still working

The report limit was already implemented (3 reports per user). Let's verify it still works.

#### Step 1: Upload 3 Inventory Files (Should SUCCEED)

**Request: `POST http://localhost:5000/api/v1/reports`**

**Headers:**
- `Authorization: Bearer YOUR_TOKEN_HERE`

**Body (form-data):**
- `file`: [Upload any Excel/CSV file]
- `warehouse_id`: "TEST_WAREHOUSE"

**Repeat 3 times** - all should succeed.

---

#### Step 2: Try to Upload 4th Report (Should FAIL)

**Expected Response:** ❌ HTTP 403
```json
{
  "message": "You have reached the maximum limit of 3 analysis reports."
}
```

---

## Quick Test Checklist ✅

Use this checklist to verify all features:

### Registration & Invitations:
- [ ] Cannot register without invitation code
- [ ] Cannot register with invalid code
- [ ] Can register with valid code (BOOTSTRAP2025)
- [ ] Can generate new invitation codes
- [ ] Can validate invitation codes
- [ ] Invitation uses increment correctly

### Template Limits:
- [ ] Can create 5 templates
- [ ] Cannot create 6th template
- [ ] Error message is clear and helpful

### Monitoring:
- [ ] Can view database statistics
- [ ] Can view database health warnings
- [ ] Can view personal user statistics
- [ ] Statistics accurately reflect current state

### Report Limits (Existing):
- [ ] Can create 3 reports
- [ ] Cannot create 4th report

---

## Troubleshooting 🔧

### "Token is invalid" Error:
**Solution**: Login again to get a fresh token. Tokens may expire.

### "401 Unauthorized" Error:
**Solution**: Check that you're including the `Authorization: Bearer YOUR_TOKEN` header.

### "Connection Refused" Error:
**Solution**: Make sure the backend server is running on port 5000.

### Templates Not Creating:
**Solution**: Check that you're using the correct endpoint and JSON format.

---

## Using Postman (Visual Guide)

### Setup:
1. Download Postman: https://www.postman.com/downloads/
2. Create a new Collection: "Database Efficiency Tests"
3. Add environment variables:
   - `base_url`: `http://localhost:5000`
   - `token`: (will be set after login)

### Request Template:
```
Method: POST
URL: {{base_url}}/api/v1/auth/login
Headers:
  Content-Type: application/json
Body (raw JSON):
  {
    "username": "testuser1",
    "password": "password123"
  }
```

---

## Expected Test Duration ⏱️

- **Test 1 (Registration)**: 5 minutes
- **Test 2 (Template Limits)**: 10 minutes
- **Test 3 (Monitoring)**: 5 minutes
- **Test 4 (Invitations)**: 10 minutes
- **Test 5 (Reports)**: 5 minutes

**Total**: ~35 minutes for complete testing

---

## Test Results Template 📋

Copy this template to track your testing:

```
DATABASE EFFICIENCY TESTING RESULTS
Date: ___________
Tester: ___________

Test 1: Invitation-Only Registration
- [ ] PASS: Cannot register without code
- [ ] PASS: Cannot register with invalid code
- [ ] PASS: Can register with BOOTSTRAP2025
Notes: ___________

Test 2: Template Limits
- [ ] PASS: Created 5 templates successfully
- [ ] PASS: 6th template rejected with limit error
Notes: ___________

Test 3: Database Monitoring
- [ ] PASS: db-stats endpoint works
- [ ] PASS: db-health endpoint works
- [ ] PASS: user-stats endpoint works
Notes: ___________

Test 4: Invitation Management
- [ ] PASS: Can generate invitation codes
- [ ] PASS: Can validate codes
- [ ] PASS: Can use codes for registration
- [ ] PASS: Usage count increments correctly
Notes: ___________

Test 5: Report Limits
- [ ] PASS: Can create 3 reports
- [ ] PASS: 4th report rejected
Notes: ___________

OVERALL RESULT: PASS / FAIL
Issues Found: ___________
```

---

## Success Criteria 🎯

All tests are successful if:
1. ✅ Cannot register without valid invitation code
2. ✅ Template creation stops at 5 per user
3. ✅ Monitoring endpoints return accurate data
4. ✅ Invitation codes work correctly
5. ✅ Report limit still enforced at 3

---

**Need Help?**
- Check server logs: `backend/server.log`
- Verify database: `backend/instance/database.db`
- Review implementation: `DB_EFFICIENCY_IMPLEMENTATION_SUMMARY.md`

**Happy Testing! 🚀**
