# Customer Demo Account Setup & Monitoring Guide

## Overview
Complete guide for creating demo accounts for potential customers and monitoring their activity to gain sales insights.

---

## Quick Start: Create Demo User

### Option 1: Interactive Mode (Easiest)
```bash
cd backend/src
python create_demo_user.py
```

Follow the prompts:
1. Enter customer/company name: `Acme Corp`
2. Enter email (optional): `contact@acmecorp.com`
3. Enter password (or press Enter for default): `Demo2025!`
4. Confirm: `y`

### Option 2: Command Line
```bash
# Create demo user
python create_demo_user.py create "Acme Corp" contact@acmecorp.com MyPassword123

# List all demo users
python create_demo_user.py list

# Create custom invitation code
python create_demo_user.py invite "Acme Corp" 3
```

---

## What Gets Created

### Demo User Account:
- **Username**: `demo_acme_corp` (auto-generated from company name)
- **Password**: `Demo2025!` (or custom)
- **Max Reports**: 10 (higher than regular users)
- **Max Templates**: 10 (higher than regular users)
- **User ID**: Auto-generated

### Example Output:
```
============================================================
✓ DEMO USER CREATED SUCCESSFULLY!
============================================================

Customer: Acme Corp
Email: contact@acmecorp.com

Credentials:
  Username: demo_acme_corp
  Password: Demo2025!
  User ID: 5

Limits:
  Max Reports: 10
  Max Templates: 10

Created: 2025-01-07T15:30:00.000000

============================================================
IMPORTANT: Share these credentials securely!
Recommend customer changes password after first login.
============================================================
```

---

## Monitoring Customer Activity

### 1. List All Demo Users
**Endpoint**: `GET /api/v1/customer-monitoring/demo-users`

**Request**:
```bash
curl -X GET http://localhost:5000/api/v1/customer-monitoring/demo-users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**:
```json
{
  "demo_users": [
    {
      "user_id": 5,
      "username": "demo_acme_corp",
      "activity": {
        "reports_created": 3,
        "templates_created": 2,
        "last_activity": "2025-01-07T18:45:00",
        "engagement_score": 65
      },
      "limits": {
        "max_reports": 10,
        "max_templates": 10,
        "reports_remaining": 7,
        "templates_remaining": 8
      }
    }
  ],
  "total_count": 1,
  "timestamp": "2025-01-07T20:00:00"
}
```

---

### 2. Get Detailed Activity for Specific Customer
**Endpoint**: `GET /api/v1/customer-monitoring/user/{user_id}/activity`

**Request**:
```bash
curl -X GET http://localhost:5000/api/v1/customer-monitoring/user/5/activity \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**:
```json
{
  "user": {
    "id": 5,
    "username": "demo_acme_corp"
  },
  "activity_summary": {
    "total_reports": 3,
    "total_templates": 2,
    "total_warehouses": 1,
    "total_sessions": 2,
    "avg_session_duration_minutes": 25
  },
  "recent_reports": [
    {
      "id": 15,
      "name": "Warehouse Analysis - 2025-01-07",
      "created_at": "2025-01-07T18:45:00",
      "anomaly_count": 12
    }
  ],
  "templates": [
    {
      "id": 8,
      "name": "Standard Warehouse Layout",
      "created_at": "2025-01-07T17:30:00",
      "usage_count": 1
    }
  ],
  "sessions": [
    {
      "session_start": "2025-01-07T17:00:00",
      "session_end": "2025-01-07T17:45:00",
      "duration_minutes": 45,
      "actions_count": 5
    }
  ],
  "engagement_metrics": {
    "engagement_score": 65,
    "reports_created": 3,
    "templates_created": 2,
    "days_since_last_activity": 0,
    "is_active": true
  }
}
```

---

### 3. Get Chronological Timeline
**Endpoint**: `GET /api/v1/customer-monitoring/user/{user_id}/timeline`

**Shows every action the customer took, in order:**
```json
{
  "timeline": [
    {
      "type": "report_created",
      "timestamp": "2025-01-07T18:45:00",
      "description": "Created report: Warehouse Analysis",
      "details": {
        "report_id": 15,
        "report_name": "Warehouse Analysis"
      }
    },
    {
      "type": "template_created",
      "timestamp": "2025-01-07T17:30:00",
      "description": "Created template: Standard Warehouse Layout",
      "details": {
        "template_id": 8,
        "template_name": "Standard Warehouse Layout"
      }
    }
  ],
  "total_events": 5
}
```

---

### 4. Get Engagement Report (All Demo Users)
**Endpoint**: `GET /api/v1/customer-monitoring/engagement-report`

**Perfect for weekly sales reviews:**
```json
{
  "demo_users_engagement": [
    {
      "user_id": 5,
      "username": "demo_acme_corp",
      "metrics": {
        "engagement_score": 85,
        "reports_created": 5,
        "templates_created": 3,
        "days_since_last_activity": 1,
        "is_active": true
      },
      "risk_level": "low"
    },
    {
      "user_id": 6,
      "username": "demo_widgets_inc",
      "metrics": {
        "engagement_score": 25,
        "reports_created": 1,
        "templates_created": 0,
        "days_since_last_activity": 15,
        "is_active": false
      },
      "risk_level": "high"
    }
  ],
  "summary": {
    "total_demo_users": 2,
    "highly_engaged": 1,
    "moderately_engaged": 0,
    "at_risk": 1
  }
}
```

---

## Understanding Engagement Metrics

### Engagement Score (0-100):
- **Reports Created**: 40 points max (10 points per report)
- **Templates Created**: 30 points max (10 points per template)
- **Recency**: 30 points max
  - Active today: 30 points
  - Active last 3 days: 20 points
  - Active last 7 days: 10 points
  - Inactive > 7 days: 0 points

### Risk Levels:
- **Low (Green)**: Engagement score ≥ 70, active within 14 days
  - Action: Schedule follow-up call to close deal
- **Medium (Yellow)**: Engagement score 40-69
  - Action: Send value-add content, schedule demo call
- **High (Red)**: Engagement score < 40 OR inactive > 14 days
  - Action: Re-engagement campaign, offer extended trial

---

## Sales Insights Dashboard

### Weekly Review Checklist:
1. **Check Engagement Report**
   ```bash
   GET /api/v1/customer-monitoring/engagement-report
   ```

2. **For Each High-Engagement User**:
   - Review their timeline
   - Identify which features they're using most
   - Prepare customized follow-up

3. **For Each At-Risk User**:
   - Check days since last activity
   - Send re-engagement email
   - Offer demo call or training

### Key Questions to Answer:
1. **Are they creating reports?**
   - Yes (3+) = Understanding the value
   - No = May need training/demo

2. **Are they creating templates?**
   - Yes = Planning to use long-term
   - No = Still exploring

3. **How long are their sessions?**
   - 30+ minutes = Deep engagement
   - < 10 minutes = Superficial exploration

4. **Days since last activity?**
   - 0-3 days = Hot lead
   - 4-7 days = Warm lead
   - 8-14 days = Cooling off
   - 15+ days = At risk of losing

---

## Demo Account Best Practices

### Setup:
1. **Create user immediately after demo call**
2. **Send credentials within 1 hour**
3. **Set higher limits** (10 reports, 10 templates) to show full capabilities
4. **Include sample data** (optional: pre-load a template)

### Follow-up Schedule:
- **Day 1**: Send welcome email with credentials
- **Day 3**: Check if they've logged in
- **Day 7**: Review activity, send helpful resources
- **Day 14**: If active, schedule closing call
- **Day 21**: If inactive, re-engagement campaign

### Communication Templates:

#### Initial Setup Email:
```
Subject: Your Warehouse Intelligence Demo Account is Ready!

Hi [Customer Name],

Great speaking with you! Your demo account is now ready:

Username: demo_[customer_name]
Password: [password]
URL: https://your-app.com

Your account has enhanced limits:
- 10 analysis reports
- 10 warehouse templates

Getting Started:
1. Upload your first inventory file
2. Explore our pre-built templates
3. Generate your first warehouse intelligence report

Need help? Reply to this email or schedule time with me.

Best regards,
[Your Name]
```

#### Day 7 Follow-up (Active User):
```
Subject: Loving the results you're getting!

Hi [Customer Name],

I noticed you've created [X] reports and [Y] templates - that's awesome!

I'd love to hear:
- What insights have surprised you?
- Any questions about advanced features?
- Ready to discuss pricing/implementation?

Let's schedule a 15-minute call: [Calendar Link]

Best regards,
[Your Name]
```

#### Day 14 Re-engagement (Inactive User):
```
Subject: Quick question about your warehouse intelligence trial

Hi [Customer Name],

I wanted to check in - I noticed you haven't logged into your demo account recently.

Common reasons customers pause:
- Too busy (we can help with onboarding)
- Need more training (free demo session available)
- Evaluating other tools (let's compare features)

Can I help remove any roadblocks?

Best regards,
[Your Name]
```

---

## Advanced Monitoring

### Export Activity Data:
```python
# Script to export customer activity to CSV
import csv
from app import app, db
from core_models import User, AnalysisReport
from models import WarehouseTemplate

with app.app_context():
    demo_users = User.query.filter(User.username.like('demo_%')).all()

    with open('demo_user_activity.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Username', 'Reports', 'Templates', 'Last Activity', 'Engagement Score'])

        for user in demo_users:
            report_count = AnalysisReport.query.filter_by(user_id=user.id).count()
            template_count = WarehouseTemplate.query.filter_by(created_by=user.id, is_active=True).count()
            last_report = AnalysisReport.query.filter_by(user_id=user.id).order_by(
                AnalysisReport.timestamp.desc()
            ).first()

            writer.writerow([
                user.username,
                report_count,
                template_count,
                last_report.timestamp if last_report else 'Never',
                calculate_engagement_score(user.id)
            ])

print("Exported to demo_user_activity.csv")
```

---

## Security & Privacy

### Important Notes:
1. **Never share monitoring data with customers** - This is internal sales intelligence
2. **Respect privacy** - Monitor usage patterns, not specific data contents
3. **Secure credentials** - Use password managers, don't send via plain email
4. **Clean up after trials** - Delete demo accounts after sales cycle (win or lose)

### Deleting Demo Users:
```python
# WARNING: This deletes all user data permanently
from app import app, db
from core_models import User

with app.app_context():
    user = User.query.filter_by(username='demo_acme_corp').first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"Deleted user: {user.username}")
```

---

## Troubleshooting

### Customer can't log in:
1. Verify username format: `demo_[company_name]`
2. Check password was shared correctly
3. Verify account exists: `python create_demo_user.py list`

### No activity showing:
1. Check if user has actually logged in
2. Verify user_id is correct
3. Check if they're using a different account

### Engagement score seems wrong:
- Score updates in real-time based on current activity
- Recent activity weighs heavily (30 points for recency)
- Check if they're creating reports/templates

---

## Summary

### To Create Demo User:
```bash
python create_demo_user.py
# Or
python create_demo_user.py create "Customer Name"
```

### To Monitor Activity:
```bash
# All demo users
GET /api/v1/customer-monitoring/demo-users

# Specific user
GET /api/v1/customer-monitoring/user/{id}/activity

# Engagement report
GET /api/v1/customer-monitoring/engagement-report
```

### Key Metrics:
- Engagement Score (0-100)
- Risk Level (Low/Medium/High)
- Days Since Last Activity
- Reports/Templates Created

---

**Ready to close more deals with data-driven insights! 🚀**
