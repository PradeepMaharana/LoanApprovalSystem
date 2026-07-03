# Loan Approval System - REST API Documentation

## Overview

Professional REST API for loan application processing with comprehensive validation, risk assessment, and chat functionality.

**Base URL:** `http://localhost:8000`
**API Version:** `v1`
**API Prefix:** `/api/v1`

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Data Models](#data-models)
4. [Endpoints](#endpoints)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the API

```bash
python api.py
```

Or using uvicorn directly:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

---

## Authentication

Currently, the API uses no authentication. For production, implement JWT or OAuth2.

---

## Data Models

### ApplicantProfile

```json
{
  "applicant_id": "string (3-50 chars, alphanumeric)",
  "age": "integer (18-100)",
  "income": "float (>0)",
  "employment_type": "Salaried | Self-Employed | Freelancer | Business Owner",
  "location": "string (2-100 chars)"
}
```

**Validation Rules:**
- `applicant_id`: Must be alphanumeric (hyphens and underscores allowed)
- `age`: Between 18 and 100 years old
- `income`: Annual income in USD, must be positive
- `employment_type`: Must be one of the enum values
- `location`: Geographic location, 2-100 characters

### CreditLoanDetails

```json
{
  "credit_score": "integer (300-850)",
  "loan_amount": "float (>0, ≤10,000,000)",
  "tenure": "integer (3-360, multiple of 3)",
  "liabilities": "float (≥0, default: 0)"
}
```

**Validation Rules:**
- `credit_score`: FICO score range (300-850)
- `loan_amount`: Loan amount in USD
- `tenure`: Loan duration in months, must be multiple of 3
- `liabilities`: Existing debts in USD

### LoanApplicationRequest

```json
{
  "applicant": { /* ApplicantProfile */ },
  "loan_details": { /* CreditLoanDetails */ },
  "timestamp": "ISO 8601 datetime (optional)"
}
```

### RiskAssessment

```json
{
  "risk_score": "float (0-100)",
  "risk_level": "string",
  "dti_ratio": "float (Debt-to-Income)",
  "lti_ratio": "float (Loan-to-Income)",
  "factors": {
    "credit_score": {
      "impact": "integer",
      "value": "number",
      "description": "string"
    },
    "dti_ratio": { /* ... */ },
    "age": { /* ... */ },
    "lti_ratio": { /* ... */ }
  }
}
```

**Risk Levels:**
- **Very Low Risk:** Score ≥ 75
- **Low Risk:** Score 60-74
- **Moderate Risk:** Score 40-59
- **High Risk:** Score 20-39
- **Very High Risk:** Score < 20

### ApplicationStatus

```
SUBMITTED | UNDER_REVIEW | APPROVED | REJECTED | PENDING_DOCUMENTS
```

### LoanApplicationResponse

```json
{
  "application_id": "string",
  "status": "ApplicationStatus enum",
  "applicant_id": "string",
  "loan_amount": "float",
  "risk_assessment": { /* RiskAssessment */ },
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "message": "string"
}
```

### ChatMessage

```json
{
  "user_id": "string (required)",
  "message": "string (1-1000 chars)",
  "application_id": "string (optional)"
}
```

### ChatResponse

```json
{
  "message_id": "string",
  "user_id": "string",
  "user_message": "string",
  "bot_response": "string",
  "timestamp": "ISO 8601 datetime",
  "application_context": { /* optional */ }
}
```

---

## Endpoints

### Health Check

#### GET `/health`

Check if the API is running and healthy.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "service": "Loan Approval System API"
}
```

---

### Applications

#### POST `/api/v1/applications`

Submit a new loan application.

**Status Code:** 201 Created

**Request Body:**
```json
{
  "applicant": {
    "applicant_id": "APP-2024-001",
    "age": 35,
    "income": 120000,
    "employment_type": "Salaried",
    "location": "New York, NY"
  },
  "loan_details": {
    "credit_score": 750,
    "loan_amount": 300000,
    "tenure": 360,
    "liabilities": 50000
  }
}
```

**Success Response (201):**
```json
{
  "application_id": "LOAN-20240115-000001",
  "status": "APPROVED",
  "applicant_id": "APP-2024-001",
  "loan_amount": 300000,
  "risk_assessment": {
    "risk_score": 78.5,
    "risk_level": "Very Low Risk",
    "dti_ratio": 0.29,
    "lti_ratio": 2.5,
    "factors": {
      "credit_score": {
        "impact": 5,
        "value": 750,
        "description": "Credit Score Factor"
      },
      "dti_ratio": {
        "impact": 0,
        "value": 0.29,
        "description": "Debt-to-Income Ratio"
      },
      "age": {
        "impact": 0,
        "value": 35,
        "description": "Age Factor"
      },
      "lti_ratio": {
        "impact": 0,
        "value": 2.5,
        "description": "Loan-to-Income Ratio"
      }
    }
  },
  "created_at": "2024-01-15T10:30:45.123456",
  "updated_at": "2024-01-15T10:30:45.123456",
  "message": "Application approved! Congratulations on your pre-approval."
}
```

**Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "applicant", "age"],
      "msg": "ensure this value is greater than or equal to 18",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

#### GET `/api/v1/applications/{application_id}`

Get details of a specific application.

**URL Parameters:**
- `application_id` (string): The application ID

**Success Response (200):**
```json
{
  "application_id": "LOAN-20240115-000001",
  "status": "APPROVED",
  /* ... see POST response above ... */
}
```

**Error Response (404):**
```json
{
  "detail": "Application LOAN-20240115-000999 not found"
}
```

---

#### GET `/api/v1/applications`

List all applications with pagination and filtering.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 10, max: 100): Items per page
- `status_filter` (string, optional): Filter by status (SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, PENDING_DOCUMENTS)

**Example Request:**
```
GET /api/v1/applications?page=1&page_size=20&status_filter=APPROVED
```

**Success Response (200):**
```json
{
  "total_count": 42,
  "applications": [
    {
      "application_id": "LOAN-20240115-000001",
      "status": "APPROVED",
      /* ... */
    },
    {
      "application_id": "LOAN-20240115-000002",
      "status": "UNDER_REVIEW",
      /* ... */
    }
  ],
  "page": 1,
  "page_size": 20
}
```

---

### Validation

#### POST `/api/v1/validate-application`

Validate application data without submitting. Useful for real-time UI validation.

**Request Body:** (Same as POST /applications)

**Success Response (200):**
```json
{
  "risk_score": 78.5,
  "risk_level": "Very Low Risk",
  "dti_ratio": 0.29,
  "lti_ratio": 2.5,
  "factors": { /* ... */ }
}
```

---

### Chat

#### POST `/api/v1/chat`

Send a chat message and receive an intelligent response.

**Request Body:**
```json
{
  "user_id": "user-123",
  "message": "What are my chances of approval?",
  "application_id": "LOAN-20240115-000001"
}
```

**Success Response (200):**
```json
{
  "message_id": "MSG-20240115103045-1234",
  "user_id": "user-123",
  "user_message": "What are my chances of approval?",
  "bot_response": "Based on your profile and credit information, our team is reviewing your application. You'll receive a decision within 2-3 business days.",
  "timestamp": "2024-01-15T10:30:45.123456",
  "application_context": {
    "application_id": "LOAN-20240115-000001",
    "risk_assessment": {
      "risk_score": 78.5,
      "risk_level": "Very Low Risk",
      /* ... */
    }
  }
}
```

**Error Response (400):**
```json
{
  "detail": "Message cannot be empty"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Response

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

---

## Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Submit application
app_data = {
    "applicant": {
        "applicant_id": "APP-2024-001",
        "age": 35,
        "income": 120000,
        "employment_type": "Salaried",
        "location": "New York, NY"
    },
    "loan_details": {
        "credit_score": 750,
        "loan_amount": 300000,
        "tenure": 360,
        "liabilities": 50000
    }
}

response = requests.post(f"{BASE_URL}/api/v1/applications", json=app_data)
print(response.json())

# Get application
app_id = response.json()["application_id"]
response = requests.get(f"{BASE_URL}/api/v1/applications/{app_id}")
print(response.json())

# List applications
response = requests.get(f"{BASE_URL}/api/v1/applications", params={"page": 1, "page_size": 10})
print(response.json())

# Send chat message
chat_data = {
    "user_id": "user-123",
    "message": "What are my chances of approval?",
    "application_id": app_id
}
response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_data)
print(response.json())
```

### cURL

```bash
# Submit application
curl -X POST http://localhost:8000/api/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {
      "applicant_id": "APP-2024-001",
      "age": 35,
      "income": 120000,
      "employment_type": "Salaried",
      "location": "New York, NY"
    },
    "loan_details": {
      "credit_score": 750,
      "loan_amount": 300000,
      "tenure": 360,
      "liabilities": 50000
    }
  }'

# Get application
curl http://localhost:8000/api/v1/applications/LOAN-20240115-000001

# List applications
curl "http://localhost:8000/api/v1/applications?page=1&page_size=10"

# Send chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "What are my chances of approval?"
  }'
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000";

// Submit application
async function submitApplication() {
  const appData = {
    applicant: {
      applicant_id: "APP-2024-001",
      age: 35,
      income: 120000,
      employment_type: "Salaried",
      location: "New York, NY"
    },
    loan_details: {
      credit_score: 750,
      loan_amount: 300000,
      tenure: 360,
      liabilities: 50000
    }
  };

  const response = await fetch(`${BASE_URL}/api/v1/applications`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(appData)
  });

  return response.json();
}

// Send chat message
async function sendChat(userId, message, applicationId) {
  const response = await fetch(`${BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      user_id: userId,
      message: message,
      application_id: applicationId
    })
  });

  return response.json();
}
```

---

## Best Practices

1. **Always validate client-side** before submitting to API
2. **Handle errors gracefully** in your UI
3. **Use pagination** when listing applications
4. **Cache validation results** to reduce API calls
5. **Log all API interactions** for debugging
6. **Implement retry logic** for transient failures
7. **Keep application IDs** for reference
8. **Use the validation endpoint** for real-time form checking

---

## Future Enhancements

- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] User authentication (JWT/OAuth2)
- [ ] Rate limiting
- [ ] Request logging and analytics
- [ ] Email notifications
- [ ] Document upload handling
- [ ] Webhook support for status updates
- [ ] Advanced filtering and search
- [ ] Batch application processing
- [ ] Export functionality (PDF/Excel)

---

## Support

For issues or questions, please contact the development team or create an issue in the repository.
