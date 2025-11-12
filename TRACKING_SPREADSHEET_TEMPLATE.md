# OUTREACH TRACKING SPREADSHEET TEMPLATE
## Copy this into Google Sheets

---

## SHEET 1: OUTREACH TRACKER

| Name | Company | Title | LinkedIn URL | Email | Phone | Source | Outreach Date | Status | Response Date | Demo Booked | Demo Date | Interest Level | Notes | Next Action | Follow-up Date |
|------|---------|-------|--------------|-------|-------|--------|--------------|--------|---------------|-------------|-----------|----------------|-------|-------------|----------------|
| John Smith | ACME Logistics | Warehouse Manager | linkedin.com/in/johnsmith | john@acme.com | 555-1234 | LinkedIn | 2024-01-15 | Responded | 2024-01-16 | Yes | 2024-01-20 | Hot | Loves the concept, wants pilot | Send pilot agreement | 2024-01-21 |
| | | | | | | | | | | | | | | | |

### Status Values:
- Not Sent
- Sent
- Responded
- No Response
- Demo Booked
- Demo Completed
- Pilot Started
- Committed
- Not Interested
- Dead

### Interest Level:
- Hot (wants to buy)
- Warm (interested, needs more info)
- Cold (not interested)
- Unknown

### Source:
- LinkedIn Search
- Industry Directory
- Personal Network
- Referral
- Conference
- Other

---

## SHEET 2: DEMO TRACKER

| Name | Company | Demo Date | Duration (min) | Showed Up? | Current Pain (1-10) | Time Spent on Analysis | Features Requested | Objections | Interest Level (1-10) | Commitment Level | Next Action | Follow-up Date | Notes |
|------|---------|-----------|----------------|------------|---------------------|----------------------|-------------------|------------|---------------------|------------------|-------------|----------------|-------|
| John Smith | ACME Logistics | 2024-01-20 | 15 | Yes | 9 | 2-3 hrs/day | WMS integration | Price | 9 | Pilot committed | Send pilot agreement | 2024-01-21 | Very engaged, asked great questions |
| | | | | | | | | | | | | | |

### Commitment Level:
- Signed (paid or contract signed)
- Pilot Committed (agreed to pilot)
- Thinking (interested but needs time)
- Not Now (interested but bad timing)
- No Fit (not interested)

---

## SHEET 3: WEEKLY METRICS

| Week | Start Date | End Date | Outreach Sent | Responses | Response Rate | Demos Booked | Demos Completed | Show Rate | Intent Signals | Commitments | Notes |
|------|------------|----------|---------------|-----------|---------------|--------------|-----------------|-----------|----------------|-------------|-------|
| 1 | 2024-01-15 | 2024-01-21 | 50 | 8 | 16% | 3 | 2 | 67% | 0 | 0 | Good start, refining messaging |
| 2 | 2024-01-22 | 2024-01-28 | 50 | 12 | 24% | 5 | 4 | 80% | 1 | 0 | Better response rate with new hook |
| 3 | | | | | | | | | | | |
| 4 | | | | | | | | | | | |

---

## SHEET 4: OBJECTIONS LOG

| Objection | Count | How to Handle | Resolved? |
|-----------|-------|---------------|-----------|
| "Too expensive" | 3 | Show ROI calculation (saves $14K, costs $12K) | Yes |
| "Our WMS should do this" | 2 | "Does it though? Let's run a pilot and see what we catch" | Partially |
| "Need to see [Feature X]" | 5 | Building feature, eta 2 weeks | In progress |
| "No budget right now" | 2 | Offer free pilot, time contract to budget reset | Yes |

---

## SHEET 5: FEATURE REQUESTS

| Feature | Requested By (Count) | Priority | Status | Notes |
|---------|---------------------|----------|--------|-------|
| WMS Integration (SAP) | 3 companies | High | Not started | Big deal, need for enterprise |
| Email alerts for critical issues | 5 companies | High | In development | Easy win |
| Mobile app | 2 companies | Low | Backlog | Nice to have |
| Multi-warehouse dashboard | 4 companies | Medium | Planned | Key for 3PL companies |

---

## SHEET 6: MONTHLY SUMMARY

| Month | Total Outreach | Total Responses | Total Demos | Commitments | CAC ($) | Notes |
|-------|---------------|-----------------|-------------|-------------|---------|-------|
| Month 1 | 150 | 25 | 12 | 1 | $600 | Good learning month, found messaging that works |
| Month 2 | 150 | 35 | 15 | 3 | $400 | Scaling what works, better targeting |
| Month 3 | 100 | 20 | 12 | 2 | $300 | Focused on warm leads, higher conversion |
| **TOTAL** | 400 | 80 | 39 | 6 | $433 avg | **KEEP GOING** ✅ |

### CAC Calculation:
Total Cost (tools + time) / Total Commitments = CAC

Example:
- Month 1: $600 (tools) + $0 (your time = free for now) / 1 commitment = $600 CAC
- Month 2: $600 / 3 = $200 CAC
- Month 3: $600 / 2 = $300 CAC

---

## SHEET 7: DECISION DASHBOARD

### THE GO/NO-GO SCORECARD (Fill out on Day 90)

| Criteria | Target | Actual | Pass/Fail |
|----------|--------|--------|-----------|
| Total Outreach Sent | 400+ | | |
| Total Demos Completed | 20+ | | |
| Total Commitments | 3-5 | | |
| Response Rate | >15% | | |
| Demo Show Rate | >60% | | |
| Demo → Interest Rate | >40% | | |
| Interest → Commitment Rate | >25% | | |

### QUALITATIVE ASSESSMENT

**1. Did prospects resonate with the problem?**
- [ ] Yes (75%+ said "this is a real pain")
- [ ] Somewhat (40-75% acknowledged pain)
- [ ] No (<40% felt the pain)

**2. Did the solution get them excited?**
- [ ] Yes (multiple "wow" moments, asking how to buy)
- [ ] Somewhat (interested but not urgent)
- [ ] No (polite but not excited)

**3. Was price the main blocker?**
- [ ] Yes (everyone wants it, just can't afford)
- [ ] Somewhat (some price objections)
- [ ] No (objections were about features/fit, not price)

**4. Do I have a repeatable sales playbook?**
- [ ] Yes (I know exactly what works, can scale it)
- [ ] Somewhat (some things work, need refinement)
- [ ] No (every conversation is random, no pattern)

**5. Am I excited to keep doing this?**
- [ ] Yes (energized by conversations, can do this for years)
- [ ] Somewhat (it's okay, not thrilled)
- [ ] No (dreading every call, this is painful)

### THE DECISION

**If 3+ commitments AND mostly "Yes" answers above:**
✅ **KEEP GOING** - You have proof of concept. Scale it.

**If 1-2 commitments AND mixed answers:**
⚠️ **PIVOT** - There's something here, but reposition. Run another 90-day test.

**If 0-1 commitments AND mostly "No/Somewhat" answers:**
🛑 **SHUT DOWN** - Market isn't ready or product isn't right. Move on.

---

## FORMULAS TO USE IN GOOGLE SHEETS

### Response Rate
```
=COUNTIF(Status,"Responded")/COUNTIF(Status,"Sent")*100
```

### Demo Show Rate
```
=COUNTIF(Showed_Up,"Yes")/COUNTIF(Demo_Booked,"Yes")*100
```

### Demo to Interest Rate
```
=COUNTIF(Commitment_Level,"Pilot Committed","Signed")/COUNTIF(Showed_Up,"Yes")*100
```

### Weekly Outreach Count
```
=COUNTIFS(Outreach_Date,">="&StartDate,Outreach_Date,"<="&EndDate)
```

---

## HOW TO USE THIS TRACKER

### Daily (End of day):
1. Log all outreach sent today
2. Log all responses received
3. Update demo statuses
4. Set follow-up dates for tomorrow

### Weekly (Friday):
1. Fill out Weekly Metrics sheet
2. Calculate response rates
3. Review what's working / not working
4. Plan next week's targets

### Monthly (Last day):
1. Fill out Monthly Summary
2. Calculate CAC
3. Review feature requests (prioritize)
4. Analyze objections (find patterns)
5. Adjust strategy for next month

### Day 90:
1. Fill out Decision Dashboard
2. Complete qualitative assessment
3. Make your GO/NO-GO decision
4. Document learnings (either way)

---

## TIPS FOR EFFECTIVE TRACKING

1. **Update in Real-Time:** Don't batch-update at end of week (you'll forget details)

2. **Be Brutally Honest:** "Warm" interest isn't real interest. Only count real commitments.

3. **Track Objections Obsessively:** Patterns in objections = insights for pivots

4. **Celebrate Small Wins:** First response = beer. First demo = dinner. First commitment = champagne.

5. **Review Weekly:** Friday review keeps you honest and focused

6. **Share Metrics:** Tell someone your numbers weekly (accountability)

---

## RED FLAGS TO WATCH FOR

🚩 **Response rate <10% after Week 4**
→ Your messaging isn't working. Rewrite it.

🚩 **Demo show rate <50%**
→ You're not qualifying properly. Ask better questions before booking.

🚩 **Everyone says "interesting but..."**
→ It's a nice-to-have, not a must-have. Rethink positioning.

🚩 **Every prospect wants different features**
→ No clear market fit. You're talking to wrong people.

🚩 **You dread opening this spreadsheet**
→ You've lost momentum. Take a break or shut it down.

---

## GREEN LIGHTS TO CELEBRATE

✅ **Response rate >20%**
→ Your messaging is working! Scale it.

✅ **Demo show rate >70%**
→ You're qualifying well and people are genuinely interested.

✅ **Multiple "when can we start?" questions**
→ You have demand. Close them.

✅ **Feature requests are similar across prospects**
→ Clear market need. Build those features.

✅ **You're excited to check this spreadsheet**
→ You have momentum. Keep going.

---

## COPY THIS TEMPLATE

1. Open Google Sheets
2. Create new spreadsheet called "90-Day Validation Tracker"
3. Create 7 sheets (tabs) with names above
4. Copy column headers into each sheet
5. Set up formulas for automatic calculations
6. Share with accountability buddy (optional)
7. Start filling it out TODAY

**First Action:** Add 10 names to Sheet 1 (Outreach Tracker) right now.

Then send them outreach messages.

The clock starts TODAY.

Go! 🚀
