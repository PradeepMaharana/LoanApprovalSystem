# 🚀 Quick Start Guide - Loan Approval API

## 60-Second Setup

### 1. Start API Server
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
source venv/bin/activate
python api.py
```

**Expected Output:**
```
INFO:     Started server process [XXXX]
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Access in Browser
- **Interactive Docs:** http://localhost:8000/api/docs
- **Alternative Docs:** http://localhost:8000/api/redoc

### 3. Test API
```bash
# In another terminal
source venv/bin/activate
python test_api.py
```

---

## ✨ Key Endpoints

### Submit Loan Application
```bash
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
```

### Get Application Status
```bash
curl http://localhost:8000/api/v1/applications/LOAN-20240115-000001
```

### List All Applications
```bash
curl "http://localhost:8000/api/v1/applications?page=1&page_size=10"
```

### Validate Without Submitting
```bash
curl -X POST http://localhost:8000/api/v1/validate-application \
  -H "Content-Type: application/json" \
  -d '{ /* same request format as submit */ }'
```

### Send Chat Message
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "What are my approval chances?",
    "application_id": "LOAN-20240115-000001"
  }'
```

---

## 📊 Response Example

### Success Response (201 Created)
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
    "lti_ratio": 2.5
  },
  "created_at": "2024-01-15T10:30:45.123456",
  "message": "Application approved!"
}
```

---

## 🎓 Validation Rules Quick Reference

| Field | Min | Max | Notes |
|-------|-----|-----|-------|
| `applicant_id` | 3 chars | 50 chars | Alphanumeric + `-_` |
| `age` | 18 | 100 | Years |
| `income` | $0.01 | Unlimited | Annual USD |
| `credit_score` | 300 | 850 | FICO score |
| `loan_amount` | $1,000 | $10M | USD |
| `tenure` | 3 | 360 | Months, multiple of 3 |
| `liabilities` | $0 | Unlimited | USD |

### Employment Types
- `Salaried`
- `Self-Employed`
- `Freelancer`
- `Business Owner`

---

## 📈 Risk Levels

| Score | Level | Status |
|-------|-------|--------|
| ≥ 75 | Very Low Risk | ✅ APPROVED |
| 60-74 | Low Risk | ⏳ UNDER_REVIEW |
| 40-59 | Moderate Risk | ⏳ UNDER_REVIEW |
| 20-39 | High Risk | ⏳ UNDER_REVIEW |
| < 20 | Very High Risk | ❌ REJECTED |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `api.py` | Main FastAPI application |
| `config.py` | Configuration settings |
| `streamlit_integration.py` | Streamlit client library |
| `test_api.py` | Test suite |
| `API_DOCUMENTATION.md` | Complete API reference |
| `README_API.md` | Detailed guide |

---

## 🔗 Integration with Streamlit

```python
from streamlit_integration import get_api_client, display_risk_assessment

# Get API client
client = get_api_client()

# Submit application
response = client.submit_application(form_data)

# Display risk assessment
if response:
    display_risk_assessment(response['risk_assessment'])
```

---

## ❌ Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### API Won't Start
```bash
# Ensure venv is activated
source venv/bin/activate

# Install dependencies if needed
pip install fastapi uvicorn pydantic

# Run with verbose output
python api.py --debug
```

### Import Errors
```bash
# Reinstall requirements
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Quick Links

- 📖 **Full Documentation:** `API_DOCUMENTATION.md`
- 🎯 **Setup Guide:** `README_API.md`
- 📋 **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`
- 🧪 **Run Tests:** `python test_api.py`
- 🌐 **Swagger UI:** http://localhost:8000/api/docs

---

## 💡 Pro Tips

1. **Real-time Validation:** Use `/validate-application` endpoint for instant feedback
2. **Pagination:** Always use pagination for listing: `?page=1&page_size=20`
3. **Chat Context:** Link chat messages to applications for better responses
4. **Error Handling:** Always check HTTP status code first
5. **Testing:** Run full test suite regularly: `python test_api.py`

---

## 🔄 Full Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Validate form data first
validation = requests.post(f"{BASE_URL}/validate-application", json=app_data).json()
print(f"Risk Score: {validation['risk_score']}")

# 2. If satisfied, submit application
response = requests.post(f"{BASE_URL}/applications", json=app_data)
app = response.json()
print(f"Application ID: {app['application_id']}")
print(f"Status: {app['status']}")

# 3. Get application details
status = requests.get(f"{BASE_URL}/applications/{app['application_id']}").json()
print(f"Current Status: {status['status']}")

# 4. Send chat message
chat = requests.post(f"{BASE_URL}/chat", json={
    "user_id": "user-123",
    "message": "When will I hear back?",
    "application_id": app['application_id']
}).json()
print(f"Bot: {chat['bot_response']}")
```

---

## ✅ Verification Checklist

- [ ] API starts without errors
- [ ] Can access Swagger UI at `/api/docs`
- [ ] Health check returns 200
- [ ] Can submit a valid application
- [ ] Invalid data is rejected
- [ ] Can retrieve application by ID
- [ ] Can list applications
- [ ] Chat endpoint works
- [ ] All tests pass

---

**Ready to go!** 🎉

For detailed information, see the full documentation files.
