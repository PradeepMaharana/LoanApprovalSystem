# Quick Start - Unified Loan Application Assistant

## 🚀 5-Minute Setup

### **1. Start All Services (Open 3 terminals)**

**Terminal 1 - API Server**:
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python3 src/api/api.py
```
✅ Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Unified App**:
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python3 -m streamlit run src/ui/unified_loan_app.py --server.port 8502
```
✅ Wait for: `Local URL: http://localhost:8502`

**Terminal 3 - MySQL** (if not running):
```bash
mysql -u root -p
```

---

## 🎯 First Test (2 minutes)

### **Step 1: Submit Application**
1. Go to **http://localhost:8502** in browser
2. You're in **Tab 1: Submit Application**
3. Fill form with sample data:
   ```
   Applicant ID: TEST-001
   Age: 35
   Income: $75,000
   Employment: Salaried
   Credit Score: 750
   Loan Amount: $200,000
   Tenure: 120
   Liabilities: $30,000
   Location: New York, NY
   ```
4. Click **"✅ Submit Application"**
5. ✅ See success message

### **Step 2: Analyze Application**
1. Click **Tab 2: Analyze Application**
   - Applicant ID auto-populated: `TEST-001`
2. Click **"🔍 Analyze"**
3. ✅ See 5 analysis tabs:
   - 📋 Decision: ✅ APPROVE (Risk: 75/100)
   - 👤 Profile: Income stability, employment risk
   - 💰 Financial: DTI, LTI ratios
   - 🎯 Factors: Top 5 decision factors
   - ✅ Actions: Recommended next steps

### **Step 3: Try Features**
- Click **"📝 Load to Form for Editing"** → Tab 1 pre-fills
- Click **"📥 Download Analysis (JSON)"** → File downloads
- Change applicant ID → Click Analyze → See different applicant

---

## 📚 Complete Workflows

### **Workflow A: Submit → Analyze (2 minutes)**

```
Tab 1: Fill Form
↓
Click: Submit Application
↓
Success: "Application submitted!"
↓
Tab 2: Analyze
↓
See: 5 analysis tabs with AI insights
↓
Decision: APPROVE/REJECT/REVIEW
```

### **Workflow B: Analyze → Edit → Resubmit (3 minutes)**

```
Tab 2: Enter existing applicant ID
↓
Click: Analyze
↓
Review: Decision, profile, financial analysis
↓
Click: "Load to Form for Editing"
↓
Tab 1: Form pre-filled with applicant data
↓
Edit: Change loan amount or other fields
↓
Submit: As new/updated application
```

### **Workflow C: Download for Records (1 minute)**

```
Tab 2: Analyze application
↓
Click: "📥 Download Analysis (JSON)"
↓
File: analysis_TEST-001_20260706_120000.json
↓
Contains: Applicant data, AI analysis, decision, factors
```

---

## 🎓 Key Concepts

### **Decision Classifications**

| Decision | Score | Meaning |
|----------|-------|---------|
| ✅ APPROVE | ≥60 | Proceed with loan |
| ⚠️ REVIEW | 45-59 | Manual review needed |
| ❌ REJECT | <45 | Decline application |

### **Financial Metrics**

| Metric | Calculation | Good Range |
|--------|------------|------------|
| **DTI** | (Debt + Loan) / Income | < 43% |
| **LTI** | Loan / Income | < 3x |

### **Confidence Level**

| Level | Meaning |
|-------|---------|
| 90%+ | Very high (clear decision) |
| 75-89% | High (normal review) |
| 60-74% | Moderate (extra verification) |
| <60% | Low (manual underwriting) |

---

## 🔍 Where to Find Things

### **In Tab 1: Submit Application**

| What | Where |
|------|-------|
| Enter applicant ID | Top left |
| Enter loan amount | Right column |
| See DTI/LTI | Bottom section |
| Submit button | Bottom left |
| Clear form button | Bottom middle |

### **In Tab 2: Analyze Application**

| What | Where |
|------|-------|
| Enter applicant ID | Top search box |
| Analyze button | Top right |
| Applicant details | Below search |
| Decision (APPROVE/REJECT) | First tab |
| Income stability score | Profile tab |
| DTI & LTI ratios | Financial tab |
| Decision factors | Factors tab |
| Next actions | Actions tab |
| Load to form button | Bottom left |
| Download button | Bottom right |

### **In Sidebar**

| What | Where |
|------|-------|
| Instructions | Expand "How to Submit" |
| Help for analysis | Expand "How to Analyze" |
| System status | Expand "System Status" |
| Links to other apps | Bottom of sidebar |

---

## 💡 Pro Tips

### **Tip 1: Use Descriptive IDs**
```
Bad:  TEST1, APP1, LOAN1
Good: APP-2024-001001, CUST-12345-2026
```
Makes tracking and searching easier.

### **Tip 2: Check DTI Before Submitting**
```
DTI = (Liabilities + Loan Amount) / Income × 100
Example: ($30,000 + $200,000) / $75,000 × 100 = 307%
⚠️ Very high! Consider reducing loan amount or increasing income.
```

### **Tip 3: Understand Credit Score Impact**
```
750+: Excellent → Better rates & terms
700-749: Good → Standard rates
650-699: Fair → Higher rates
<650: Poor → Likely rejection or co-signer needed
```

### **Tip 4: Load & Edit Pattern**
```
1. Analyze application (Tab 2)
2. See decision and factors
3. If not ideal, click "Load to Form"
4. Edit loan amount or other fields
5. Submit as new application
6. See improved decision
```

### **Tip 5: Download for Documentation**
```
Always download analysis JSON for records.
Useful for:
- Audit trail
- Review documentation
- Dispute resolution
- Compliance requirements
```

---

## ⚡ Common Actions (Quick Reference)

### **"I want to submit a new application"**
→ Tab 1 → Fill form → Submit

### **"I want to see analysis of existing application"**
→ Tab 2 → Enter ID → Analyze

### **"I want to edit and resubmit"**
→ Tab 2 → Analyze → Load to Form → Edit → Submit

### **"I want to download the analysis"**
→ Tab 2 → Analyze → Download JSON

### **"I want to check if an applicant was approved"**
→ Tab 2 → Enter ID → Analyze → Look at Decision tab

### **"I want to see why application was rejected"**
→ Tab 2 → Analyze → Review Factors & Explanation

### **"I want to find a better loan strategy"**
→ Tab 2 → Analyze → Load to Form → Reduce loan or increase income → Submit

---

## 🔗 Access Points

| App | URL | Purpose |
|-----|-----|---------|
| **Unified App** ⭐ | http://localhost:8502 | **USE THIS** - Combined form + analysis |
| Form App (Original) | http://localhost:8501 | Form only (if needed) |
| Chatbot App (Original) | http://localhost:8503 | Analysis only (if needed) |
| API | http://localhost:8000 | Backend API |

---

## 🆘 Quick Troubleshooting

### **"App won't load"**
```
✅ Check: http://localhost:8502 is correct URL
✅ Check: Terminal shows "Streamlit running"
✅ Try: Refresh page or use incognito mode
```

### **"Can't submit application"**
```
✅ Check: All fields are filled (marked with *)
✅ Check: API running on 8000 (see "System Status" in sidebar)
✅ Check: Applicant ID is unique (new, not existing)
```

### **"Can't find applicant"**
```
✅ Check: Applicant ID exactly matches what you submitted
✅ Check: You submitted application first (it saves to database)
✅ Check: ID is case-sensitive (TEST-001 ≠ test-001)
```

### **"Analysis takes forever"**
```
✅ Normal: First analysis takes 5-10 seconds
✅ Check: Wait for green checkmark to appear
✅ Check: API not blocked (check terminal for errors)
```

---

## 📊 Example Test Data

### **Conservative Applicant (Likely Approve)**
```
ID: CONSERVATIVE-001
Age: 45
Income: $100,000
Credit Score: 780
Loan: $150,000
Tenure: 120 months
Liabilities: $20,000
Employment: Salaried
```
✅ Expected: APPROVE (Low risk)

### **Moderate Applicant (Likely Review)**
```
ID: MODERATE-001
Age: 35
Income: $60,000
Credit Score: 700
Loan: $150,000
Tenure: 120 months
Liabilities: $80,000
Employment: Self-Employed
```
⚠️ Expected: REVIEW (Moderate risk)

### **Risky Applicant (Likely Reject)**
```
ID: RISKY-001
Age: 25
Income: $40,000
Credit Score: 580
Loan: $300,000
Tenure: 360 months
Liabilities: $100,000
Employment: Freelancer
```
❌ Expected: REJECT (High risk)

---

## 📈 What You'll See

### **After Successful Submission**
```
✅ Application submitted successfully!
   Application ID: LOAN-20260706-000001
   Status: APPROVED
   Risk Score: 75.0
   
💡 Go to "Analyze Application" tab to see AI-powered loan analysis!
```

### **After Successful Analysis**
```
DECISION: ✅ APPROVE

Risk Score: 75/100
Confidence: 92.5%
Reason: Strong credit profile with stable employment

[5 tabs with detailed analysis]
```

---

## 🎯 Typical Session (5-10 minutes)

```
1. Go to http://localhost:8502 (0 min)
2. Fill application form (2 min)
3. Click Submit (1 min)
4. See success message (30 sec)
5. Click Tab 2: Analyze (30 sec)
6. Review all 5 analysis tabs (2 min)
7. Download JSON if needed (30 sec)
8. Try another applicant or edit this one (5 min)
```

---

## 📞 Need More Help?

- **Detailed Guide**: Read `UNIFIED_APP_GUIDE.md` (comprehensive)
- **Implementation Details**: Read `INTEGRATION_SUMMARY.md` (technical)
- **Troubleshooting**: Check Troubleshooting sections in full guides
- **Code Comments**: Review code in `src/ui/unified_loan_app.py`

---

**Ready to go? Visit http://localhost:8502 now! 🚀**
