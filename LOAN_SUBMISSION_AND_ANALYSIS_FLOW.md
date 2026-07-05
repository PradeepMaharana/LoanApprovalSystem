# Loan Submission & Agent Analysis Flow

## Complete End-to-End Process

This document describes the complete flow from loan application submission through agent analysis.

---

## Part 1: Loan Application Submission (Streamlit App)

### Step 1: User Submits Application
**File**: `src/ui/app.py`

1. User fills out all required loan application fields:
   - Applicant ID, Location, Age, Income, Employment Type
   - Credit Score, Loan Amount, Tenure
   - Existing Liabilities
   - Application Timestamp

2. User clicks "✅ Submit Application"

3. Form validation checks all fields are filled

### Step 2: API Request Construction
**File**: `src/ui/app.py` (Submit Button Handler)

Form data is converted to API-compatible JSON structure:

```json
{
  "applicant": {
    "applicant_id": "APP-2024-001001",
    "age": 35,
    "income": 85000,
    "employment_type": "Salaried",
    "location": "New York, NY"
  },
  "loan_details": {
    "credit_score": 750,
    "loan_amount": 200000,
    "tenure": 120,
    "liabilities": 45000
  },
  "timestamp": "2026-07-06 14:30:00"
}
```

### Step 3: API Submission
**File**: `src/ui/streamlit_integration.py`

```python
LoanAPIClient.submit_application(api_request)
  ↓
POST http://localhost:8000/api/v1/applications
```

---

## Part 2: API Processing & Database Insertion

### Step 4: API Endpoint Receives Request
**File**: `src/api/api.py` (Line 306: `submit_application` endpoint)

1. Validates Pydantic models:
   - `ApplicantProfile` validation
   - `CreditLoanDetails` validation

2. Calculates risk score using `calculate_risk_score()`:
   ```
   Credit Score Impact: ±40 points
   DTI Ratio Impact: ±30 points
   Age Impact: ±15 points
   LTI Ratio Impact: ±20 points
   Final Score: 0-100
   ```

3. Determines initial application status:
   - Risk Score ≥ 75 → APPROVED
   - Risk Score < 20 → REJECTED
   - Otherwise → UNDER_REVIEW

### Step 5: Database Insertion (Critical)
**File**: `src/api/api.py` (Lines 349-383)

#### 5A: Insert Applicant Data
```python
db_service.insert_applicant({
    'applicant_id': 'APP-2024-001001',
    'age': 35,
    'income': 85000,
    'employment_type': 'Salaried',
    'location': 'New York, NY'
})
```

**Database Operation**:
```sql
INSERT INTO applicants
(applicant_id, age, income, employment_type, location, created_at, updated_at)
VALUES ('APP-2024-001001', 35, 85000, 'Salaried', 'New York, NY', NOW(), NOW())
ON DUPLICATE KEY UPDATE updated_at = NOW()
```

✅ **Result**: Row inserted into `applicants` table

#### 5B: Insert Loan Application Data
```python
db_service.insert_loan_application({
    'applicant_id': 'APP-2024-001001',
    'credit_score': 750,
    'loan_amount': 200000,
    'tenure_months': 120,
    'existing_liabilities': 45000,
    'risk_score': 78.5,
    'risk_level': 'Low Risk'
})
```

**Database Operation**:
```sql
INSERT INTO loan_applications
(applicant_id, credit_score, loan_amount, tenure_months, existing_liabilities,
 risk_score, risk_level, application_status, application_timestamp, created_at, updated_at)
VALUES ('APP-2024-001001', 750, 200000, 120, 45000, 78.5, 'Low Risk', 
        'SUBMITTED', NOW(), NOW(), NOW())
ON DUPLICATE KEY UPDATE
    credit_score = VALUES(credit_score),
    loan_amount = VALUES(loan_amount),
    tenure_months = VALUES(tenure_months),
    existing_liabilities = VALUES(existing_liabilities),
    risk_score = VALUES(risk_score),
    risk_level = VALUES(risk_level),
    updated_at = VALUES(updated_at)
```

✅ **Result**: Row inserted into `loan_applications` table

### Step 6: API Response
**File**: `src/api/api.py` (Lines 382-403)

Returns `LoanApplicationResponse`:
```json
{
  "application_id": "LOAN-20260706-000001",
  "status": "UNDER_REVIEW",
  "applicant_id": "APP-2024-001001",
  "loan_amount": 200000,
  "risk_assessment": {
    "risk_score": 78.5,
    "risk_level": "Low Risk",
    "dti_ratio": 0.576,
    "lti_ratio": 2.353,
    "factors": {...}
  },
  "created_at": "2026-07-06T14:30:00.000Z",
  "updated_at": "2026-07-06T14:30:00.000Z",
  "message": "Application received and under review..."
}
```

### Step 7: UI Success Feedback
**File**: `src/ui/app.py` (Lines 453-483)

Streamlit displays:
- ✅ Success message with Application ID
- Application details from API response
- Rich bot response with all details
- Chat history update

---

## Part 3: Agent Analysis (Chatbot UI)

### Step 8: User Requests Agent Analysis
**File**: `src/ui/streamlit_chatbot_ui.py`

1. User opens Chatbot UI at http://localhost:8503
2. User enters Applicant ID: `APP-2024-001001`
3. User clicks "🔍 Analyze Application"

### Step 9: Fetch Applicant from Database
**File**: `src/api/api.py` (Line 613: `get_applicant_profile` endpoint)

```python
db_service.get_applicant_with_application(applicant_id)
```

**Database Query**:
```sql
SELECT
    a.*,
    l.credit_score, l.loan_amount, l.tenure_months, l.existing_liabilities,
    l.application_status, l.risk_score, l.risk_level,
    r.income_stability_score, r.employment_risk_score, r.credit_category,
    r.dti_ratio, r.lti_ratio
FROM applicants a
LEFT JOIN loan_applications l ON a.applicant_id = l.applicant_id
LEFT JOIN risk_assessments r ON a.applicant_id = r.applicant_id
WHERE a.applicant_id = 'APP-2024-001001'
```

✅ **Result**: Complete applicant profile with all related data

### Step 10: Agent Orchestration (Coordinate Agent Analysis)
**File**: `src/api/api.py` (Line 828: `analyze_applicant` endpoint)

Triggers `AgentCoordinator.coordinate_agent_analysis(applicant_id)`:

#### 10A: ApplicantProfileAgent
- **Input**: Applicant database profile
- **Output**: 
  ```json
  {
    "income_stability_score": 82,
    "employment_risk_score": 35,
    "credit_category": "Excellent",
    "employment_stability": "High",
    "income_trend": "Stable"
  }
  ```

#### 10B: FinancialRiskAgent
- **Input**: Loan application data
- **Output**:
  ```json
  {
    "dti_ratio": 0.576,
    "dti_percentage": 57.6,
    "lti_ratio": 2.353,
    "lti_percentage": 235.3,
    "monthly_payment_estimate": 1666.67,
    "financial_risk_level": "Moderate"
  }
  ```

#### 10C: LoanDecisionAgent
- **Input**: ApplicantProfile + FinancialRisk + LoanDetails
- **Output**:
  ```json
  {
    "classification": "APPROVE",
    "risk_score": 78.5,
    "confidence_level": 92.5,
    "key_factors": {
      "credit_score_factor": "Strong",
      "dti_ratio_factor": "Acceptable",
      "income_stability_factor": "Stable",
      "employment_risk_factor": "Low"
    },
    "explanation": "Strong credit profile with stable employment and acceptable debt levels...",
    "recommended_actions": [
      "Prepare required documentation",
      "Schedule final verification call",
      "Expected funding: 2-3 business days"
    ]
  }
  ```

### Step 11: Agent Response Synthesis
**File**: `src/api/agent_coordinator.py`

Combines all agent outputs:

```json
{
  "status": "success",
  "applicant_id": "APP-2024-001001",
  "applicant_profile": {
    "age": 35,
    "income": 85000,
    "employment_type": "Salaried",
    "location": "New York, NY",
    "income_stability_score": 82,
    "employment_risk_score": 35,
    "credit_score": 750,
    "credit_category": "Excellent"
  },
  "financial_analysis": {
    "dti_ratio": 0.576,
    "dti_percentage": 57.6,
    "lti_ratio": 2.353,
    "lti_percentage": 235.3,
    "monthly_payment_estimate": 1666.67
  },
  "decision": {
    "classification": "APPROVE",
    "risk_score": 78.5,
    "confidence_level": 92.5,
    "key_factors": {...},
    "explanation": "...",
    "recommended_actions": [...]
  }
}
```

### Step 12: Chatbot UI Display
**File**: `src/ui/streamlit_chatbot_ui.py`

Displays in organized tabs:

#### Tab 1: Decision
- ✅ **DECISION: APPROVE** (with color coding)
- Risk Score: 78.5/100
- Confidence Level: 92.5%
- Explanation with detailed reasoning

#### Tab 2: Applicant Profile
- Age: 35 years
- Income: $85,000
- Income Stability Score: 82/100
- Employment Risk Score: 35/100
- Credit Score: 750 (Excellent)
- Employment Type: Salaried
- Location: New York, NY

#### Tab 3: Financial Analysis
- DTI Ratio: 0.576 (57.6%)
- LTI Ratio: 2.353 (235.3%)
- Monthly Payment: $1,666.67
- Loan Amount: $200,000
- Tenure: 120 months

#### Tab 4: Decision Factors
- Credit Score Factor: Strong
- DTI Ratio Factor: Acceptable
- Income Stability: Stable
- Employment Risk: Low

#### Tab 5: Recommended Actions
1. Prepare required documentation
2. Schedule final verification call
3. Expected funding: 2-3 business days

---

## Database Schema Overview

### applicants table
```sql
applicant_id (PK)
age
income
employment_type
location
created_at
updated_at
```

### loan_applications table
```sql
id (PK)
applicant_id (FK)
credit_score
loan_amount
tenure_months
existing_liabilities
risk_score
risk_level
application_status
application_timestamp
created_at
updated_at
```

### risk_assessments table (Optional)
```sql
id (PK)
applicant_id (FK)
income_stability_score
employment_risk_score
credit_category
dti_ratio
lti_ratio
created_at
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  LOAN APPLICATION FORM                       │
│                   (Streamlit App)                            │
│  http://localhost:8501                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ User submits application
                     │ (POST /api/v1/applications)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI ORCHESTRATOR                        │
│  http://localhost:8000                                      │
│                                                              │
│  1. Validate Pydantic models                                │
│  2. Calculate risk score                                    │
│  3. Insert into applicants table                            │
│  4. Insert into loan_applications table                     │
│  5. Return API response                                     │
└────────────────────┬────────────────────────────────────────┘
                     │ Response with Application ID
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              LOAN APPLICATION FORM                           │
│         Shows success & stores in session                   │
└─────────────────────────────────────────────────────────────┘

              Data now persisted in MySQL!

┌─────────────────────────────────────────────────────────────┐
│                    CHATBOT UI                                │
│            (Streamlit Chatbot)                              │
│  http://localhost:8503                                      │
│                                                              │
│  User enters Applicant ID                                   │
└────────────────────┬────────────────────────────────────────┘
                     │ (GET /api/v1/analyze/{applicant_id})
                     ↓
┌─────────────────────────────────────────────────────────────┐
│           AGENT ORCHESTRATOR (API)                           │
│                                                              │
│  1. Fetch applicant + loan data from database               │
│  2. Run ApplicantProfileAgent                               │
│  3. Run FinancialRiskAgent                                  │
│  4. Run LoanDecisionAgent                                   │
│  5. Synthesize all agent outputs                            │
│  6. Return comprehensive analysis                           │
└────────────────────┬────────────────────────────────────────┘
                     │ Comprehensive agent response
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    CHATBOT UI                                │
│                                                              │
│  Display in organized tabs:                                 │
│  • Decision (Classification, Risk Score, Confidence)        │
│  • Applicant Profile (Income Stability, Employment Risk)    │
│  • Financial Analysis (DTI, LTI)                            │
│  • Decision Factors (Key factors breakdown)                 │
│  • Recommended Actions (Next steps)                         │
│  • Raw JSON (Complete agent output)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Files & Responsibilities

| File | Role | Key Function |
|------|------|--------------|
| `src/ui/app.py` | Form Submission | Collects user input, calls API, displays success |
| `src/ui/streamlit_integration.py` | API Client | Makes HTTP requests to FastAPI |
| `src/api/api.py` | API Server | Validates, calculates risk, inserts to DB |
| `src/database/db_service.py` | Database Layer | Executes INSERT/SELECT queries |
| `src/ui/streamlit_chatbot_ui.py` | Analysis Display | Fetches agent analysis, displays results |
| `src/api/agent_coordinator.py` | Agent Orchestration | Runs all agents, synthesizes output |

---

## Testing the Complete Flow

### Test 1: Submit Application
```bash
# 1. Start API server
python src/api/api.py &

# 2. Start Streamlit app
streamlit run src/ui/app.py --server.port 8501 &

# 3. Fill and submit form
# Expected: Success message + data in database
```

### Test 2: Verify Database
```sql
-- Check applicants table
SELECT * FROM applicants WHERE applicant_id = 'APP-2024-001001';

-- Check loan_applications table
SELECT * FROM loan_applications WHERE applicant_id = 'APP-2024-001001';
```

### Test 3: View Agent Analysis
```bash
# 1. Open Chatbot UI
streamlit run src/ui/streamlit_chatbot_ui.py --server.port 8503 &

# 2. Enter Applicant ID: APP-2024-001001
# 3. Click "Analyze Application"
# Expected: Comprehensive agent analysis displayed
```

---

## Troubleshooting

### Application not saving to database
- ✅ Check API logs for insertion errors
- ✅ Verify MySQL is running on localhost:3306
- ✅ Check database credentials in `src/database/db_service.py`
- ✅ Verify `applicants` and `loan_applications` tables exist

### Agent analysis returns 404
- ✅ Verify applicant was saved to database first
- ✅ Check exact Applicant ID format
- ✅ Try searching applicants first with search feature

### Chatbot UI shows "Not Found"
- ✅ Make sure application was submitted through main form first
- ✅ Verify API is running on port 8000
- ✅ Check API logs for errors

### API connection errors in Streamlit
- ✅ Verify API is running: `curl http://localhost:8000/health`
- ✅ Check firewall settings
- ✅ Verify port 8000 is not in use

---

## Environment Requirements

- **MySQL**: Running on localhost:3306
- **API Server**: Running on localhost:8000
- **Streamlit App**: Running on localhost:8501
- **Chatbot UI**: Running on localhost:8503

All three services must be running for the complete flow to work!
