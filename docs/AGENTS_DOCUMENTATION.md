# Loan Approval System - Agents Documentation

## Overview

Four specialized agents process loan applications end-to-end, reading from MySQL database (`loan_approval_system`) and outputting comprehensive analysis at each stage.

```
┌─────────────────────────────────────────────────────────────────┐
│              INTEGRATED LOAN PROCESSING PIPELINE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MySQL Database (loan_approval_system)                         │
│  ├── applicants (profiles)                                     │
│  ├── loan_applications (application data)                      │
│  └── risk_assessments (risk scores)                            │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  AGENT 1: Applicant Profile Agent                    │     │
│  │  - Income Stability Score                            │     │
│  │  - Employment Risk Analysis                          │     │
│  │  - Credit History Summary                            │     │
│  │  - Application Completeness Flags                    │     │
│  └──────────────────────────────────────────────────────┘     │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  AGENT 2: Financial Risk Analysis Agent              │     │
│  │  - Debt-to-Income Ratio Calculation                  │     │
│  │  - Credit Score Risk Level Assessment                │     │
│  │  - Loan Amount Risk Evaluation                       │     │
│  │  - Anomaly Detection & Reasoning                     │     │
│  └──────────────────────────────────────────────────────┘     │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  AGENT 3: Loan Decision Agent                        │     │
│  │  - Classification (Approve/Reject/Review)            │     │
│  │  - Risk Score Calculation (0-100)                    │     │
│  │  - Confidence Level Assessment                       │     │
│  │  - Key Decision Factors Extraction                   │     │
│  │  - Detailed Explanation Generation                   │     │
│  └──────────────────────────────────────────────────────┘     │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  AGENT 4: Compliance & Action Orchestrator           │     │
│  │  - Action Execution (Database Updates)               │     │
│  │  - Notification Orchestration                        │     │
│  │  - Case ID Generation                                │     │
│  │  - Compliance Verification                           │     │
│  │  - Audit Trail Logging                               │     │
│  └──────────────────────────────────────────────────────┘     │
│           │                                                    │
│           ▼                                                    │
│  Comprehensive Report + JSON Output                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent 1: Applicant Profile Agent

### Location
[agents/applicant_profile_agent.py](agents/applicant_profile_agent.py)

### MCP Server
**ApplicantDB** - Applicant data management

### Purpose
Analyzes complete applicant profiles, combining personal data, application status, and risk assessments.

### Input
- `applicant_id`: String (e.g., "APP-2026-000001")

### Database Tables Used
- `applicants` - Personal information, employment, income
- `loan_applications` - Loan request details, credit score
- `risk_assessments` - Risk scores and completeness flags

### Output Data

```json
{
  "applicant_id": "APP-2026-000001",
  "timestamp": "2026-07-01T10:30:45.123456",
  "applicant_info": {
    "name": "John Doe",
    "age": 35,
    "location": "New York, NY",
    "employment_type": "Salaried",
    "annual_income": 120000
  },
  "income_stability_score": {
    "score": 78,
    "range": "0-100",
    "interpretation": "Stable - Reasonably consistent income",
    "factors": {
      "employment_type": "Salaried",
      "employment_years": 8,
      "income_level": "High"
    }
  },
  "employment_risk": {
    "score": 45,
    "range": "0-100 (higher = more risk)",
    "risk_level": "Moderate Risk - Some employment risk",
    "factors": {
      "employment_type": "Salaried",
      "industry": "Technology",
      "employment_duration": 8
    }
  },
  "credit_history_summary": {
    "category": "Very Good",
    "description": "Strong credit profile with minimal late payments",
    "credit_score": 745,
    "recommendation": "Low risk credit profile",
    "liabilities": 35000,
    "debt_accounts": 3
  },
  "application_completeness": {
    "completion_percentage": 95.5,
    "missing_fields": [],
    "verifications": {
      "documents_verified": true,
      "employment_verified": true,
      "income_verified": true
    },
    "warning_flags": [],
    "status": "Ready for Processing"
  },
  "application_status": {
    "status": "Pending",
    "loan_amount_requested": 300000,
    "date_submitted": "2026-07-01"
  }
}
```

### Key Metrics

| Metric | Range | Interpretation |
|--------|-------|-----------------|
| Income Stability Score | 0-100 | Higher = More Stable |
| Employment Risk Score | 0-100 | Lower = Less Risk |
| Application Completeness | 0-100% | Higher = More Complete |

### Running the Agent

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python agents/applicant_profile_agent.py
```

---

## Agent 2: Financial Risk Analysis Agent

### Location
[agents/financial_risk_agent.py](agents/financial_risk_agent.py)

### MCP Server
**RiskRulesDB** - Risk assessment rules and algorithms

### Purpose
Performs comprehensive financial risk analysis including DTI calculations, credit risk assessment, and anomaly detection.

### Input
- `applicant_id`: String

### Database Tables Used
- `applicants` - Income, liabilities
- `loan_applications` - Credit score, loan amount, debt accounts
- `risk_assessments` - Risk scores

### Output Data

```json
{
  "applicant_id": "APP-2026-000001",
  "timestamp": "2026-07-01T10:31:15.234567",
  "financial_overview": {
    "annual_income": 120000,
    "monthly_income": 10000,
    "total_liabilities": 35000,
    "monthly_liabilities": 2916.67,
    "requested_loan_amount": 300000
  },
  "debt_to_income_analysis": {
    "current_dti_ratio": 0.292,
    "current_dti_status": "Good",
    "interpretation": "Good - Acceptable debt-to-income ratio"
  },
  "credit_score_risk_level": {
    "score": 745,
    "risk_level": "Low Risk",
    "recommendation": "Excellent credit profile, minimal risk",
    "approval_likelihood": 0.95
  },
  "loan_amount_risk_assessment": {
    "loan_amount": 300000,
    "loan_to_income_ratio": 2.5,
    "monthly_debt_service_estimate": 1266.71,
    "projected_dti": 0.416,
    "projected_dti_status": "Acceptable",
    "risk_score": 15,
    "risk_level": "Low-Medium Risk",
    "risk_factors": [
      "Loan amount within reasonable limits"
    ],
    "recommendation": "Acceptable"
  },
  "anomaly_detection": {
    "total_anomalies": 0,
    "severity_distribution": {
      "Critical": 0,
      "High": 0,
      "Medium": 0,
      "Low": 0
    },
    "anomalies": []
  },
  "overall_financial_risk": {
    "risk_score": 42,
    "risk_classification": "Low-Medium Risk",
    "confidence_level": 95.0
  },
  "reasoning": "DTI ratio: 29.2% - healthy | Credit score: 745 - strong | Loan amount risk: Low-Medium Risk | No financial anomalies detected",
  "recommendations": [
    "Recommend approval with standard terms"
  ]
}
```

### Key Metrics

| Metric | Ranges | Status |
|--------|--------|--------|
| DTI Ratio | < 0.15 | Excellent |
| DTI Ratio | 0.15 - 0.30 | Good |
| DTI Ratio | 0.30 - 0.50 | Acceptable |
| DTI Ratio | 0.50 - 0.70 | High |
| DTI Ratio | > 0.70 | Very High |
| Credit Score | 750+ | Low Risk |
| Credit Score | 700-750 | Low-Medium Risk |
| Credit Score | 650-700 | Medium Risk |
| Credit Score | < 650 | High Risk |

### Anomaly Detection Types

- High Debt Load
- Excessive Loan Request
- Credit-Debt Mismatch
- Low Credit + Large Loan
- High Employment Risk

### Running the Agent

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python agents/financial_risk_agent.py
```

---

## Agent 3: Loan Decision Agent

### Location
[agents/loan_decision_agent.py](agents/loan_decision_agent.py)

### MCP Server
**DecisionSynthesis** - Loan decision synthesis

### Purpose
Synthesizes final loan decision based on all risk factors, calculates terms, and provides detailed explanation.

### Input
- `applicant_id`: String

### Database Tables Used
- `applicants` - All personal and financial data
- `loan_applications` - Application details
- `risk_assessments` - Risk scores

### Output Data

```json
{
  "applicant_id": "APP-2026-000001",
  "timestamp": "2026-07-01T10:32:00.345678",
  "decision": {
    "classification": "APPROVE",
    "classification_reason": "Strong approval recommended - low risk profile",
    "risk_score": 78.5,
    "confidence_level": 95.0
  },
  "key_decision_factors": [
    {
      "factor": "Income Stability",
      "value": 78,
      "impact": "Positive",
      "contribution_to_score": 5.6,
      "weight": 20.0
    },
    {
      "factor": "Credit Score",
      "value": 745,
      "impact": "Positive",
      "contribution_to_score": 20.0,
      "weight": 25.0
    },
    {
      "factor": "Dti Ratio",
      "value": 0.416,
      "impact": "Positive",
      "contribution_to_score": 10.0,
      "weight": 15.0
    }
  ],
  "financial_breakdown": {
    "requested_loan_amount": 300000,
    "recommended_interest_rate": 4.5,
    "recommended_term": "30 years (360 months)",
    "estimated_monthly_payment": 1520.06,
    "total_interest_cost": 247221.60,
    "total_amount_to_repay": 547221.60
  },
  "conditions": [
    "Standard loan terms apply",
    "Recommend automatic payment setup"
  ],
  "explanation": "Loan decision synthesis for John Doe: Overall risk score is 78/100, resulting in a 'APPROVE' decision. Strongest positive factor: Credit Score (745). Applicant demonstrates acceptable creditworthiness and repayment capacity.",
  "recommendation_for_processor": "Process immediately with standard terms"
}
```

### Decision Classifications

| Classification | Risk Score | Action |
|---|---|---|
| APPROVE | 75+ | Process immediately |
| APPROVE | 60-75 | Process with standard review |
| REVIEW | 45-60 | Manual underwriter review |
| REJECT | 30-45 | Rejection recommended |
| REJECT | 0-30 | Strong rejection recommended |

### Risk Score Calculation

```
Base Score: 50
+ Credit Factor (0-25 points)
+ Income Stability (0-20 points)
+ Employment Risk (-20 to 20 points)
+ DTI Ratio (-15 to 15 points)
+ Loan-to-Income (-10 to 10 points)
= Final Risk Score (0-100)
```

### Running the Agent

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python agents/loan_decision_agent.py
```

---

## Agent 4: Compliance & Action Orchestrator

### Location
[agents/compliance_action_agent.py](agents/compliance_action_agent.py)

### MCP Server
**NotificationSystem** - Communication and alerts

### Purpose
Executes compliance checks, orchestrates actions, sends notifications, and generates case tracking.

### Input
- `applicant_id`: String
- `decision_data`: Decision output from Agent 3

### Database Tables Used
- `applicants` - Contact information
- `loan_applications` - Application status
- `action_audit_log` - Action tracking (created automatically)
- `notifications` - Notification records

### Output Data

```json
{
  "applicant_id": "APP-2026-000001",
  "case_id": "CASE-20260701-A7F2D3C1",
  "timestamp": "2026-07-01T10:32:45.456789",
  "action_type": "APPROVAL",
  "actions_taken": [
    "Application status updated to APPROVED",
    "Approval notifications sent (EMAIL + SMS)",
    "Scheduled document collection process",
    "Action logged in audit trail"
  ],
  "notifications_sent": [
    {
      "type": "EMAIL",
      "recipient": "john.doe@example.com",
      "status": "SENT"
    },
    {
      "type": "SMS",
      "recipient": "+1-555-0123",
      "status": "SENT"
    }
  ],
  "compliance_checks": {
    "credit_verification": "PASSED",
    "income_verification": "PASSED",
    "employment_verification": "PENDING",
    "documentation_verification": "PENDING"
  },
  "next_steps": [
    "Send formal approval letter",
    "Request final documentation",
    "Schedule loan disbursement"
  ],
  "summary": "4 actions executed, 2 notifications sent"
}
```

### Action Types by Decision

#### APPROVAL Actions
- Update application status to APPROVED
- Send approval notification (EMAIL + SMS)
- Schedule document collection
- Log in audit trail

#### REVIEW Actions
- Update application status to UNDER_REVIEW
- Request additional documents
- Assign to underwriting team
- Set follow-up reminder
- Log in audit trail

#### REJECTION Actions
- Update application status to REJECTED
- Send rejection notification
- Archive application
- Log in audit trail
- Set reapplication eligibility date

### Compliance Checks

| Check | Approval | Review | Rejection |
|-------|----------|--------|-----------|
| Credit Verification | ✅ PASSED | ✅ PASSED | ❌ FAILED |
| Income Verification | ✅ PASSED | ⏳ REQUIRES_DOC | ❌ FAILED |
| Employment Verification | ⏳ PENDING | ⏳ REQUIRES_DOC | ❌ FAILED |
| Documentation | ⏳ PENDING | ⏳ PENDING | ❌ FAILED |

### Running the Agent

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python agents/compliance_action_agent.py
```

---

## Integrated Loan Processor

### Location
[agents/integrated_loan_processor.py](agents/integrated_loan_processor.py)

### Purpose
Orchestrates all four agents in sequence for end-to-end loan processing.

### Features
- Connects all four agents to database
- Processes applicants through complete pipeline
- Generates comprehensive reports
- Supports batch processing
- Exports JSON reports

### Usage

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem/agents
python integrated_loan_processor.py
```

### Output Files

1. **report_APP-2026-000001.json** - Individual applicant comprehensive report
2. **batch_processing_summary.json** - Batch processing summary with all reports

### Comprehensive Report Structure

```json
{
  "processing_summary": {
    "applicant_id": "APP-2026-000001",
    "start_time": "2026-07-01T10:30:00",
    "end_time": "2026-07-01T10:33:00",
    "processing_time_seconds": 180,
    "status": "COMPLETED"
  },
  "stage_1_applicant_profile": { ... },
  "stage_2_financial_risk": { ... },
  "stage_3_loan_decision": { ... },
  "stage_4_compliance_action": { ... },
  "final_recommendation": {
    "final_decision": "APPROVE",
    "overall_assessment": { ... },
    "key_strengths": [ ... ],
    "key_concerns": [ ... ],
    "recommended_action": "Process immediately with standard terms",
    "next_processing_steps": [ ... ]
  }
}
```

---

## Database Schema Reference

### Tables Used

#### applicants
```sql
- applicant_id (PK)
- full_name
- date_of_birth
- email
- phone
- address
- location
- employment_type
- employment_years
- income
- liabilities
- industry
```

#### loan_applications
```sql
- application_id (PK)
- applicant_id (FK)
- credit_score
- loan_amount
- application_status
- debt_accounts
- documents_verified
- employment_verified
- income_verified
- date_submitted
```

#### risk_assessments
```sql
- assessment_id (PK)
- applicant_id (FK)
- income_stability_score
- employment_risk_score
- credit_category
- credit_recommendation
- warning_flags (JSON)
```

#### action_audit_log (Auto-created)
```sql
- log_id (PK)
- applicant_id (FK)
- action_type
- action_details (JSON)
- timestamp
```

#### notifications (Auto-created)
```sql
- notification_id (PK)
- applicant_id (FK)
- notification_type
- message
- priority
- status
- timestamp
```

---

## Running Individual Agents

### Agent 1: Applicant Profile
```bash
python agents/applicant_profile_agent.py
```
**Output**: Profile analysis with completeness flags

### Agent 2: Financial Risk
```bash
python agents/financial_risk_agent.py
```
**Output**: DTI ratio, credit risk, anomalies

### Agent 3: Loan Decision
```bash
python agents/loan_decision_agent.py
```
**Output**: Decision, terms, explanation

### Agent 4: Compliance
```bash
python agents/compliance_action_agent.py
```
**Output**: Actions, notifications, case ID

### All Agents Integrated
```bash
cd agents
python integrated_loan_processor.py
```
**Output**: Comprehensive reports for all applicants

---

## Configuration

### Database Configuration
All agents use this configuration:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tek@12345',
    'database': 'loan_approval_system'
}
```

### Modifying Applicant ID
Edit the `main()` function in each agent:
```python
applicant_id = 'APP-2026-000001'  # Change this
```

---

## Processing Flow Example

```
Input: applicant_id = "APP-2026-000001"
  ↓
Agent 1: Fetch applicant data → Analyze profile → Output: Profile data
  ↓
Agent 2: Fetch financial data → Calculate DTI → Detect anomalies → Output: Risk analysis
  ↓
Agent 3: Combine all scores → Calculate risk score → Classify decision → Output: Decision
  ↓
Agent 4: Execute actions → Send notifications → Create case → Output: Orchestration summary
  ↓
Integrated Processor: Generate comprehensive report → Save JSON files
```

---

## Performance Metrics

| Operation | Typical Time |
|-----------|--------------|
| Single Agent Processing | 1-3 seconds |
| All Agents (1 applicant) | 5-10 seconds |
| Batch Processing (3 applicants) | 15-30 seconds |

---

## Error Handling

All agents include:
- Database connection error handling
- Missing applicant ID handling
- Invalid data type handling
- Graceful degradation for missing fields

### Common Error Messages

```
"❌ Applicant {id} not found"
"❌ Database connection error: {message}"
"❌ Database query error: {message}"
```

---

## Extending the Agents

### Adding New Analysis
1. Add calculation method to agent class
2. Include result in output dictionary
3. Add to print_report() method
4. Update documentation

### Adding New Actions
1. Add orchestration method to ComplianceActionOrchestrator
2. Call from orchestrate_action()
3. Log action with log_action()
4. Document in OUTPUT_DATA section

---

## Integration with MCP Servers

While these agents read directly from MySQL database, they're designed to integrate with:

- **ApplicantDB** MCP Server for remote applicant queries
- **RiskRulesDB** MCP Server for risk calculation rules
- **DecisionSynthesis** MCP Server for decision synthesis
- **NotificationSystem** MCP Server for notification management

To use MCP servers instead of direct database access, replace database queries with MCP tool calls.

---

## Support & Troubleshooting

### Connection Issues
```bash
mysql -u root -p'Tek@12345' -h localhost -e "SELECT 1;"
```

### Verify Data
```bash
mysql -u root -p'Tek@12345' loan_approval_system -e "SELECT COUNT(*) FROM applicants;"
```

### View Logs
Check console output for error messages and warnings (⚠️  prefix)

---

Generated: 2026-07-01
Status: Production Ready
Version: 1.0.0
