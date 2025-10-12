# Create Your First Demo User - Quick Guide

## For Your Upcoming Customer Demo

### Step 1: Create the Demo Account

Open terminal in the backend folder:

```bash
cd backend/src
python create_demo_user.py
```

### Step 2: Enter Customer Information

When prompted:

```
Enter customer/company name: [Customer Company Name]
Enter email (optional): [their.email@company.com]
Enter password (press Enter for default 'Demo2025!'): [press Enter]
```

Example:
```
Enter customer/company name: Highland Logistics
Enter email (optional): john@highlandlogistics.com
Enter password (press Enter for default 'Demo2025!'): [press Enter]

Create this user? (y/n): y
```

### Step 3: Save the Credentials

You'll see output like:
```
============================================================
✓ DEMO USER CREATED SUCCESSFULLY!
============================================================

Customer: Highland Logistics
Email: john@highlandlogistics.com

Credentials:
  Username: demo_highland_logistics
  Password: Demo2025!
  User ID: 5

Limits:
  Max Reports: 10
  Max Templates: 10
============================================================
```

**IMPORTANT: Copy these credentials!**

---

## Share with Customer

### Email Template:

```
Subject: Your Warehouse Intelligence Demo Account

Hi [Customer Name],

Great connecting with you! I've set up your personal demo account:

🔐 Login Credentials:
- URL: [your-app-url.com]/auth
- Username: demo_highland_logistics
- Password: Demo2025!

💡 Your Account Includes:
- 10 analysis reports
- 10 warehouse templates
- Full access to all features

📚 Quick Start Guide:
1. Log in with the credentials above
2. Upload a sample inventory file (Excel/CSV)
3. Map your columns to our system
4. Generate your first warehouse intelligence report

Need help getting started? Reply to this email or schedule time: [calendar-link]

Looking forward to showing you the value!

Best regards,
[Your Name]
```

---

## Monitor Their Activity

### After 24 Hours:

1. **Check if they logged in:**
```bash
# In Postman or your API tool:
GET http://localhost:5000/api/v1/customer-monitoring/user/5/activity
Authorization: Bearer [your_token]
```

2. **Look for:**
   - Have they created any reports? (shows they uploaded data)
   - Have they created templates? (shows they're planning to use it)
   - When was their last activity?

### After 3 Days:

Check engagement score:
```bash
GET http://localhost:5000/api/v1/customer-monitoring/demo-users
```

**If engagement_score < 40:**
- They might need help
- Send follow-up email with training offer
- Schedule a walkthrough call

**If engagement_score > 60:**
- They're engaged!
- Schedule closing call
- Prepare pricing discussion

---

## Quick Commands Reference

### Create demo user:
```bash
python create_demo_user.py create "Customer Name" email@company.com
```

### List all demo users:
```bash
python create_demo_user.py list
```

### Check specific user activity:
```bash
# Via API (use Postman)
GET /api/v1/customer-monitoring/user/{user_id}/activity
```

### See all demo users engagement:
```bash
GET /api/v1/customer-monitoring/engagement-report
```

---

## Understanding What They're Doing

### Engagement Signals:

**🟢 Highly Engaged (Score 70-100):**
- Created 4+ reports
- Created 2+ templates
- Active within last 3 days
- **Action**: Schedule closing call this week!

**🟡 Moderate (Score 40-69):**
- Created 1-3 reports
- Maybe 1 template
- Active within last week
- **Action**: Send helpful resources, offer training

**🔴 At Risk (Score 0-39):**
- 0-1 reports
- No templates
- Inactive > 7 days
- **Action**: Re-engagement campaign, check if they need help

---

## Example: Real Customer Journey

**Day 1** (Created account):
```
Username: demo_highland_logistics
Password: Demo2025!
Email sent with credentials
```

**Day 2** (Logged in, uploaded file):
```
✓ Created report: "Warehouse A Analysis"
✓ Engagement Score: 25
```

**Day 4** (Coming back, creating more):
```
✓ Created template: "Standard Layout"
✓ Created 2 more reports
✓ Engagement Score: 65
```

**Day 7** (Schedule call):
```
Email: "I see you've created 3 reports - loving the insights?
Let's schedule a call to discuss implementation."
```

**Day 10** (Close deal):
```
✓ Engagement Score: 85
✓ Ready to discuss pricing
✓ Move to negotiation phase
```

---

## Pro Tips

1. **Create account DURING or RIGHT AFTER demo call**
   - Send credentials within 1 hour
   - Strike while iron is hot

2. **Monitor daily for first week**
   - Quick check of engagement score
   - Catch problems early

3. **Use activity timeline for follow-ups**
   - "I saw you created a template for X warehouse..."
   - Shows you're paying attention
   - Personalized approach

4. **Higher limits = Better impression**
   - 10 reports vs 3 regular users
   - Shows full capabilities
   - No frustration from hitting limits

---

## Need Help?

Check the full documentation: `CUSTOMER_DEMO_GUIDE.md`

---

**You're all set to wow your customer! 🎯**
