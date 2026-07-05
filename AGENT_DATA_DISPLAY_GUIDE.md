# Agent Data Display Guide - Chatbot UI

## Overview

This guide documents how agent data from the Agent Orchestrator is fetched and displayed in the Chatbot UI. All data flows through the MCP architecture from agents → API → Chatbot UI.

---

## Data Sources & Display Locations

### 1. ApplicantProfileAgent Data

**Data Generated:**
```json
{
  "applicant_id": "APP-2024-001001",
  "age": 35,
  "income": 85000,
  "employment_type": "Salaried",
  "location": "New York, NY",
  "income_stability_score": 82,
  "employment_risk_score": 35,
  "credit_category": "Excellent",
  "application_status": "SUBMITTED",
  "credit_score": 750,
  "loan_amount": 200000
}
```

**API Endpoint:**
```
GET /api/v1/analyze/{applicant_id}
└─ agents.applicant_profile_agent
```

**Chatbot UI Display Location:**
```
Tab 2: "👤 Applicant Profile"
├─ Income Stability Score: 82/100 ✅ Stable
├─ Employment Risk Score: 35/100 ✅ Low Risk
├─ Age: 35 years
├─ Annual Income: $85,000
├─ Employment Type: Salaried
├─ Credit Score: 750
├─ Credit Category: Excellent
└─ Location: New York, NY
```

**Display Code Reference:**
- **File**: `src/ui/streamlit_chatbot_ui.py`
- **Function**: `display_applicant_profile(profile: Dict[str, Any])`
- **Lines**: 78-116

**Visual Indicators:**
```
✅ Green   → income_stability_score >= 80 (Stable)
ℹ️ Blue    → 60 <= income_stability_score < 80 (Moderate)
⚠️ Yellow  → income_stability_score < 60 (Low)

✅ Green   → employment_risk_score <= 30 (Low Risk)
ℹ️ Blue    → 30 < employment_risk_score <= 70 (Moderate)
⚠️ Yellow  → employment_risk_score > 70 (High Risk)
```

---

### 2. LoanDecisionAgent Data

**Data Generated:**
```json
{
  "applicant_id": "APP-2024-001001",
  "classification": "APPROVE",
  "risk_score": 78.5,
  "confidence_level": 92,
  "key_decision_factors": {
    "credit_score_factor": "Strong",
    "dti_ratio_factor": "Acceptable",
    "income_stability": "Stable",
    "employment_risk": "Low"
  },
  "explanation": "Applicant has strong financial profile with low risk indicators...",
  "recommended_actions": [
    "Proceed with loan approval",
    "Generate loan offer letter",
    "Schedule documentation review"
  ],
  "decision_timestamp": "2026-07-06T14:30:00"
}
```

**API Endpoint:**
```
GET /api/v1/analyze/{applicant_id}
└─ agents.loan_decision_agent
```

**Chatbot UI Display Location:**
```
Tab 1: "🎯 Loan Decision"
├─ DECISION: APPROVE ✅
├─ Risk Score: 78.5/100 (✅ Low)
├─ Confidence Level: 92% (Very High)
└─ Explanation: "Applicant has strong financial profile..."

Tab 4: "📊 Decision Factors"
├─ Credit Score Factor: Strong ✅
├─ DTI Ratio Factor: Acceptable ℹ️
├─ Income Stability: Stable ✅
└─ Employment Risk: Low ✅

Tab 5: "✨ Recommended Actions"
1. Proceed with loan approval
2. Generate loan offer letter
3. Schedule documentation review
```

**Display Code Reference:**
- **File**: `src/ui/streamlit_chatbot_ui.py`
- **Function 1**: `display_loan_decision(decision: Dict[str, Any])` (Lines: 101-143)
- **Function 2**: `display_decision_factors(factors: Dict[str, Any])` (Lines: 145-191)
- **Function 3**: `display_recommended_actions(actions: list)` (Lines: 178-190)

**Visual Indicators:**
```
Classification Display:
  ✅ APPROVE  → Green success banner
  ❌ REJECT   → Red error banner
  ⏳ REVIEW   → Yellow warning banner

Risk Score with Delta:
  ✅ Low      → risk_score >= 75
  ⚠️ Moderate → 40 <= risk_score < 75
  ❌ High     → risk_score < 40

Confidence Level:
  Very High   → confidence >= 90%
  High        → confidence >= 75%
  Moderate    → confidence >= 50%
  Low         → confidence < 50%
```

---

### 3. FinancialRiskAgent Data

**Data Generated:**
```json
{
  "applicant_id": "APP-2024-001001",
  "dti_ratio": 0.576,
  "lti_ratio": 2.353,
  "debt_to_income_percentage": 57.6,
  "loan_to_income_percentage": 235.3,
  "existing_liabilities": 45000,
  "loan_amount": 200000,
  "monthly_payment_estimate": 1666.67,
  "dti_impact": -10,
  "lti_impact": -15
}
```

**API Endpoint:**
```
GET /api/v1/analyze/{applicant_id}
└─ agents.financial_risk_agent
```

**Chatbot UI Display Location:**
```
Tab 3: "💰 Financial Analysis"
├─ Debt-to-Income Ratio: 0.576 (57.6%)
├─ Loan-to-Income Ratio: 2.353 (235.3%)
├─ Monthly Payment Estimate: $1,666.67
├─ Existing Liabilities: $45,000
└─ Total Debt: $245,000
```

**Display Code Reference:**
- **File**: `src/ui/streamlit_chatbot_ui.py`
- **Function**: `display_financial_analysis(financial: Dict[str, Any])`
- **Lines**: 159-175

---

## Complete Data Flow

```
1. USER ACTION
   User enters Applicant ID in Chatbot UI sidebar
   Clicks "🔍 Analyze Application"
        ↓
2. API REQUEST
   GET /api/v1/analyze/{applicant_id}
   → Called from: streamlit_chatbot_ui.py:get_agent_analysis()
        ↓
3. AGENT ORCHESTRATOR
   AgentCoordinator.coordinate_agent_analysis(applicant_id)
   ├─ fetch_applicant_profile_analysis()
   │  └─ Returns: income_stability_score, employment_risk_score, etc.
   ├─ fetch_financial_risk_analysis()
   │  └─ Returns: dti_ratio, lti_ratio, monthly_payment, etc.
   └─ fetch_loan_decision_analysis()
      └─ Returns: classification, risk_score, confidence_level, key_factors, explanation
        ↓
4. RESPONSE SYNTHESIS
   to_chatbot_format(synthesized_response)
   └─ Converts to UI-friendly format with all three agent outputs
        ↓
5. CHATBOT UI RENDERING
   display_loan_status(analysis)
   ├─ display_loan_decision()        → Tab 1
   ├─ display_applicant_profile()    → Tab 2
   ├─ display_financial_analysis()   → Tab 3
   ├─ display_decision_factors()     → Tab 4
   └─ display_recommended_actions()  → Tab 5
        ↓
6. USER VIEWS RESULTS
   Professional 5-tab interface with all agent insights
```

---

## Data Extraction from API Response

### Response Structure
```json
{
  "status": "success",
  "applicant_id": "APP-2024-001001",
  "decision": {
    "classification": "APPROVE",
    "risk_score": 78.5,
    "confidence_level": 92,
    "explanation": "...",
    "key_factors": {...},
    "recommended_actions": [...]
  },
  "applicant_profile": {
    "income_stability_score": 82,
    "employment_risk_score": 35,
    "credit_category": "Excellent",
    "employment_type": "Salaried",
    "age": 35,
    "income": 85000,
    "location": "New York, NY",
    "credit_score": 750
  },
  "financial_analysis": {
    "dti_ratio": 0.576,
    "lti_ratio": 2.353,
    "debt_to_income_percentage": 57.6,
    "loan_to_income_percentage": 235.3,
    "monthly_payment_estimate": 1666.67
  },
  "timestamp": "2026-07-06T14:30:00.000Z"
}
```

### Python Code to Access Data
```python
# Get API response
response = requests.get(f"http://localhost:8000/api/v1/analyze/{applicant_id}")
analysis = response.json()

# ApplicantProfileAgent data
profile = analysis['applicant_profile']
income_stability = profile['income_stability_score']           # 82
employment_risk = profile['employment_risk_score']            # 35
credit_score = profile['credit_score']                         # 750

# LoanDecisionAgent data
decision = analysis['decision']
classification = decision['classification']                    # "APPROVE"
risk_score = decision['risk_score']                           # 78.5
confidence = decision['confidence_level']                     # 92
factors = decision['key_factors']                             # {...}
explanation = decision['explanation']                         # "..."
actions = decision['recommended_actions']                     # [...]

# FinancialRiskAgent data
financial = analysis['financial_analysis']
dti_ratio = financial['dti_ratio']                            # 0.576
lti_ratio = financial['lti_ratio']                            # 2.353
monthly_payment = financial['monthly_payment_estimate']       # 1666.67
```

---

## Chatbot UI Tabs & Content Map

| Tab # | Tab Name | Content | Agent Source |
|-------|----------|---------|--------------|
| 1 | 🎯 Decision | Classification, Risk Score, Confidence, Explanation | LoanDecisionAgent |
| 2 | 👤 Applicant Profile | Income Stability, Employment Risk, Demographics | ApplicantProfileAgent |
| 3 | 💰 Financial | DTI, LTI, Monthly Payment | FinancialRiskAgent |
| 4 | 📊 Decision Factors | Factor breakdown, assessment table | LoanDecisionAgent.key_factors |
| 5 | ✨ Actions | Recommended next steps | LoanDecisionAgent.recommended_actions |

---

## Color Coding & Visual Indicators

### Profile Metrics
```
Income Stability Score:
  ✅ Green    (80-100) → Stable
  ℹ️ Blue     (60-79)  → Moderate
  ⚠️ Yellow   (0-59)   → Low

Employment Risk Score:
  ✅ Green    (0-30)   → Low Risk
  ℹ️ Blue     (31-70)  → Moderate Risk
  ⚠️ Yellow   (71-100) → High Risk
```

### Decision Indicators
```
Classification:
  ✅ Green  → APPROVE
  ⏳ Yellow → REVIEW
  ❌ Red    → REJECT

Risk Assessment:
  ✅ Green    → Low (75-100)
  ℹ️ Blue     → Moderate (40-74)
  ❌ Red      → High (0-39)
```

### Factor Assessment
```
✅ Strong/Stable/Low  → Green success
ℹ️ Acceptable/Moderate → Blue info
⚠️ High/Problematic   → Yellow warning
```

---

## Implementation Details

### Display Functions
```python
# File: src/ui/streamlit_chatbot_ui.py

def display_applicant_profile(profile: Dict[str, Any]):
    """Displays ApplicantProfileAgent data"""
    # Shows income_stability_score, employment_risk_score with color coding
    # Displays age, income, employment type, location, credit info

def display_loan_decision(decision: Dict[str, Any]):
    """Displays LoanDecisionAgent decision data"""
    # Shows classification with banner
    # Displays risk_score, confidence_level with deltas
    # Shows explanation

def display_decision_factors(factors: Dict[str, Any]):
    """Displays LoanDecisionAgent key_decision_factors"""
    # Individual factor breakdown with color coding
    # Summary table
    # Key insights

def display_financial_analysis(financial: Dict[str, Any]):
    """Displays FinancialRiskAgent financial metrics"""
    # DTI ratio, LTI ratio, monthly payment
    # Loan terms and financial summary

def display_recommended_actions(actions: list):
    """Displays LoanDecisionAgent recommended_actions"""
    # Numbered list of recommendations
    # Context-specific actions based on classification
```

---

## Testing Agent Data Display

### Test Case 1: View APPROVE Decision
```
1. Submit loan application with:
   - Credit Score: 750+
   - DTI Ratio: <43%
   - Income Stability: 80+
   - Employment Risk: <30

2. Expected Result:
   ✅ Tab 1 shows: APPROVE (green banner)
   ✅ Risk Score: 75+ (Low)
   ✅ Confidence: 90%+
   ✅ Tab 2: Income Stability 80+ (✅ Stable)
   ✅ Tab 2: Employment Risk <30 (✅ Low)
   ✅ Tab 4: All factors green (Strong/Acceptable/Stable/Low)
```

### Test Case 2: View REJECT Decision
```
1. Submit loan application with:
   - Credit Score: <600
   - DTI Ratio: >60%
   - Income Stability: <50
   - Employment Risk: >70

2. Expected Result:
   ❌ Tab 1 shows: REJECT (red banner)
   ⚠️ Risk Score: <20 (High)
   ✓ Confidence: 90%+ (very confident it's a reject)
   ⚠️ Tab 2: Income Stability <50 (⚠️ Low)
   ⚠️ Tab 2: Employment Risk >70 (⚠️ High)
   ⚠️ Tab 4: Most factors yellow/red warnings
```

### Test Case 3: View REVIEW Decision
```
1. Submit loan application with:
   - Credit Score: 700
   - DTI Ratio: 50%
   - Income Stability: 65
   - Employment Risk: 50

2. Expected Result:
   ⏳ Tab 1 shows: REVIEW (yellow banner)
   ℹ️ Risk Score: 40-60 (Moderate)
   ℹ️ Confidence: 60-75% (moderate confidence)
   ℹ️ Tab 2: Income Stability 65 (ℹ️ Moderate)
   ℹ️ Tab 2: Employment Risk 50 (ℹ️ Moderate)
   ℹ️ Tab 4: Mixed factors (some green, some blue)
```

---

## Troubleshooting Agent Data Display

### Issue: Data Not Displaying
```
1. Check API is running on localhost:8000
   curl http://localhost:8000/health

2. Verify applicant was submitted to database
   SELECT * FROM applicants WHERE applicant_id='APP-xxx';

3. Check agent_coordinator.py is returning data
   Review API logs for: "✅ Applicant Profile Agent:", "✅ Loan Decision Agent:"

4. Verify API response format
   Use raw JSON viewer in Chatbot UI to see complete response
```

### Issue: Metrics Show "N/A"
```
Causes:
• risk_assessments table missing data
• Agent didn't calculate scores
• API response doesn't include agent outputs

Solutions:
1. Check risk_assessments table is populated:
   SELECT * FROM risk_assessments WHERE applicant_id='APP-xxx';

2. Manually verify agent response:
   curl "http://localhost:8000/api/v1/analyze/APP-xxx"

3. Check agent_coordinator.py logic for calculation issues
```

### Issue: Color Coding Not Showing
```
Check streamlit_chatbot_ui.py:
- st.success() for green (✅)
- st.info() for blue (ℹ️)
- st.warning() for yellow (⚠️)
- st.error() for red (❌)

Ensure functions are called with icon parameter:
st.success("✅ message", icon="✅")
```

---

## Agent Data Field Reference

### ApplicantProfileAgent Output Fields
| Field | Type | Range | Description |
|-------|------|-------|-------------|
| income_stability_score | int | 0-100 | Higher = more stable |
| employment_risk_score | int | 0-100 | Lower = less risky |
| credit_category | str | - | Excellent/Good/Fair/Poor |
| employment_type | str | - | Salaried/Self-Employed/etc |
| age | int | 18-100 | Applicant age |
| income | float | - | Annual income |
| location | str | - | Residential location |
| credit_score | int | 300-850 | FICO score |

### LoanDecisionAgent Output Fields
| Field | Type | Range | Description |
|-------|------|-------|-------------|
| classification | str | APPROVE/REJECT/REVIEW | Final decision |
| risk_score | float | 0-100 | Higher = lower risk |
| confidence_level | int | 0-100 | % confidence in decision |
| key_decision_factors | dict | - | Factor breakdown |
| explanation | str | - | Human-readable explanation |
| recommended_actions | list | - | Next steps |

### FinancialRiskAgent Output Fields
| Field | Type | Range | Description |
|-------|------|-------|-------------|
| dti_ratio | float | - | Debt-to-income ratio |
| lti_ratio | float | - | Loan-to-income ratio |
| debt_to_income_percentage | float | - | DTI as percentage |
| loan_to_income_percentage | float | - | LTI as percentage |
| monthly_payment_estimate | float | - | Est. monthly payment |
| existing_liabilities | float | - | Total existing debt |
| loan_amount | float | - | Requested loan amount |

---

## Summary

The Chatbot UI now displays comprehensive data from all three agents:

✅ **ApplicantProfileAgent**
- Income Stability Score (0-100)
- Employment Risk Score (0-100)
- Complete applicant demographics

✅ **LoanDecisionAgent**
- Classification (APPROVE/REJECT/REVIEW)
- Risk Score (0-100)
- Confidence Level (0-100%)
- Key Decision Factors (breakdown of decision)
- Explanation (human-readable reasoning)
- Recommended Actions (next steps)

✅ **FinancialRiskAgent**
- DTI Ratio & Percentage
- LTI Ratio & Percentage
- Monthly Payment Estimate
- Financial Summary

All data is color-coded, well-organized in 5 tabs, and clearly sourced from each agent!
