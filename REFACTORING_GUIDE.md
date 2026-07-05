# Loan Approval System - Refactoring to Database-Driven Architecture

## Overview

The Loan Approval System has been refactored to enable **persistent data storage**, **real-time database updates**, and **comprehensive search functionality**. Form data from the UI now flows directly to the MySQL database, ensuring data is not lost when sessions expire.

---

## Architecture Changes

### Before Refactoring
```
Streamlit UI
    ↓ (Form submission)
    ↓
Session State (In-Memory)
    ↓
Data Lost on Session End ❌
```

### After Refactoring
```
Streamlit UI (app.py, streamlit_chatbot_ui.py)
    ↓ (Form submission)
    ↓
FastAPI REST API (api.py)
    ↓ (HTTP POST/GET/PUT)
    ↓
Database Service Layer (db_service.py)
    ↓ (SQL INSERT/UPDATE/SELECT)
    ↓
MySQL Database (loan_approval_system)
    ├── applicants table
    ├── loan_applications table
    ├── risk_assessments table
    └── chat_messages table
    ↓
Search Results Back to UI ✅
```

---

## Key Components

### 1. Database Service Layer (`src/database/db_service.py`) - NEW

**Purpose**: Centralized database operations with connection pooling

**Main Methods**:
- `insert_applicant()` - Add new applicant
- `insert_loan_application()` - Add loan details
- `update_applicant()` - Modify applicant
- `update_loan_application()` - Update loan status
- `search_applicants()` - Search by multiple criteria
- `get_applicant_with_application()` - Retrieve complete profile
- `search_by_status()` - Filter by application status
- `list_all_applicants()` - Paginated listing
- `get_statistics()` - Database statistics

**Singleton Pattern**: 
```python
db_service = get_db_service()  # Returns singleton instance
```

---

### 2. REST API Enhancements (`src/api/api.py`) - MODIFIED

#### Database Initialization
- Startup event initializes `db_service` on API start
- Shutdown event closes database connection gracefully

#### New Search Endpoints

**Search Applicants**
```
GET /api/v1/applicants/search
Parameters:
  - applicant_id: str (optional)
  - location: str (optional, partial match)
  - age_min: int, age_max: int
  - employment_type: str
  - credit_score_min: int, credit_score_max: int
  - application_status: str (SUBMITTED, APPROVED, etc.)
  - limit: int (1-500, default 100)

Response: { count: int, data: [...] }
```

**List All Applicants**
```
GET /api/v1/applicants
Parameters:
  - page: int (default 1)
  - limit: int (1-500, default 50)

Response: { page, limit, total, total_pages, data: [...] }
```

**Get Applicant Profile**
```
GET /api/v1/applicants/{applicant_id}

Response: Complete profile with loan application and risk assessment
```

**Update Applicant**
```
PUT /api/v1/applicants/{applicant_id}
Body: { age?, income?, employment_type?, location? }

Response: { success: bool, message: str, updated_fields: [...] }
```

**Get Statistics**
```
GET /api/v1/statistics

Response: {
  total_applicants: int,
  total_applications: int,
  applications_by_status: {...},
  applicants_by_employment: {...}
}
```

#### Modified Endpoint: Submit Application
- **Before**: Stored data in `applications_db` dictionary (in-memory)
- **After**: Persists to MySQL database via `db_service.insert_applicant()` and `db_service.insert_loan_application()`

---

### 3. Streamlit Integration Layer (`src/ui/streamlit_integration.py`) - EXTENDED

**New Methods Added**:

```python
# Search operations
search_applicants(**filters) → Dict with search results
list_all_applicants(page, limit) → Dict with paginated results
get_applicant_profile(applicant_id) → Complete applicant profile
update_applicant(applicant_id, update_data) → Update result

# Statistics
get_statistics() → Database statistics

# Combined operation
create_loan_application(applicant_profile, loan_details) → Application response
```

---

### 4. Main Streamlit App (`src/ui/app.py`) - ENHANCED

#### New Search Panel
- **Location**: Separate section after chat interface
- **Two tabs**:
  1. **Search Applicants**
     - Search by: Applicant ID, Location, Age range, Employment type, Credit score range, Status
     - "Search" button - Execute search query
     - "List All" button - Show all applicants in database
     - Results displayed in searchable dataframe
     - "Load to Form" button - Load found applicant into editor for updates
  
  2. **Database Statistics**
     - Total applicants and applications counts
     - Bar charts for status distribution
     - Employment type distribution

#### Session State Extensions
```python
st.session_state.search_results = []  # Stores search results
st.session_state.show_search = False
st.session_state.api_client = LoanAPIClient()  # API client instance
```

---

### 5. Chatbot Streamlit App (`src/ui/streamlit_chatbot_ui.py`) - ENHANCED

#### Quick Search Sidebar
- **Location**: Left sidebar, before settings
- "Search Applicant ID" text field
- Quick search button - Find applicant and load to processing
- Auto-populates `applicant_id` in session state

---

## Data Flow Examples

### Example 1: New Loan Application Submission

```
1. User opens app.py
2. Fills out form (Applicant ID, age, income, credit score, loan amount, etc.)
3. Clicks "Submit Application"
4. Frontend validates with LoanAPIClient.create_loan_application()
5. FastAPI POST /api/v1/applications receives request
6. API calls db_service.insert_applicant()
   ↓ INSERT INTO applicants (applicant_id, age, income, employment_type, location, created_at, updated_at)
7. API calls db_service.insert_loan_application()
   ↓ INSERT INTO loan_applications (applicant_id, credit_score, loan_amount, tenure_months, ...)
8. Database confirms with timestamps
9. API returns LoanApplicationResponse to UI
10. UI displays success message with application_id
11. ✅ Data persisted to MySQL - Session-independent!
```

### Example 2: Search and Update Application

```
1. User opens Search panel in app.py
2. Enters search criteria (e.g., location="New York", age_min=30)
3. Clicks "Search"
4. Frontend calls api_client.search_applicants(location="New York", age_min=30)
5. FastAPI GET /api/v1/applicants/search?location=New%20York&age_min=30
6. API calls db_service.search_applicants(criteria)
   ↓ SELECT a.*, l.* FROM applicants a LEFT JOIN loan_applications l WHERE location LIKE '%New York%' AND age >= 30
7. MySQL returns matching rows with timestamps
8. Results displayed in dataframe
9. User clicks "Load to Form" on specific applicant
10. Form fields populate with applicant data
11. User modifies fields (e.g., changes loan_amount from 100000 to 150000)
12. Clicks "Update" button
13. Frontend calls api_client.update_applicant(applicant_id, {loan_amount: 150000})
14. FastAPI PUT /api/v1/applicants/{applicant_id}
15. API calls db_service.update_loan_application()
    ↓ UPDATE loan_applications SET loan_amount=150000, updated_at=NOW() WHERE applicant_id=...
16. Database updates with new timestamp
17. UI displays success message
18. ✅ Update persisted to MySQL
```

### Example 3: Chatbot Search

```
1. User opens streamlit_chatbot_ui.py
2. In sidebar, enters applicant_id in "Quick Search"
3. Clicks "Search" button
4. Sidebar calls api_client.search_applicants(applicant_id="APP-2024-001")
5. FastAPI returns matching applicant
6. st.session_state.applicant_id is populated
7. Page reruns
8. Main interface now shows applicant context
9. User can process application or get profile details
10. ✅ Seamless applicant lookup
```

---

## Database Schema (No Changes - Existing Tables)

The system reuses existing MySQL tables:

### applicants
```sql
id, applicant_id (UNIQUE), age, income, employment_type, location, created_at, updated_at
```

### loan_applications
```sql
id, applicant_id (UNIQUE), credit_score, loan_amount, tenure_months, existing_liabilities,
application_status, risk_score, risk_level, application_timestamp, created_at, updated_at
```

### risk_assessments
```sql
id, applicant_id (UNIQUE), credit_score_impact, dti_ratio, dti_impact, age_impact,
lti_ratio, lti_impact, final_score, assessment_date
```

### chat_messages
```sql
id, applicant_id, user_message, bot_response, message_timestamp, created_at
```

---

## API Testing with curl

### Search by Location
```bash
curl "http://localhost:8000/api/v1/applicants/search?location=New%20York&limit=10"
```

### Search by Credit Score Range
```bash
curl "http://localhost:8000/api/v1/applicants/search?credit_score_min=700&credit_score_max=800"
```

### List All Applicants
```bash
curl "http://localhost:8000/api/v1/applicants?page=1&limit=50"
```

### Get Specific Applicant Profile
```bash
curl "http://localhost:8000/api/v1/applicants/APP-2024-001"
```

### Get Statistics
```bash
curl "http://localhost:8000/api/v1/statistics"
```

### Submit New Application
```bash
curl -X POST "http://localhost:8000/api/v1/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {
      "applicant_id": "APP-2024-NEW",
      "age": 35,
      "income": 120000,
      "employment_type": "Salaried",
      "location": "San Francisco, CA"
    },
    "loan_details": {
      "credit_score": 750,
      "loan_amount": 300000,
      "tenure": 360,
      "liabilities": 50000
    }
  }'
```

---

## Running the System

### Prerequisites
- MySQL server running with `loan_approval_system` database
- Python dependencies installed: `fastapi`, `mysql-connector-python`, `streamlit`, `requests`, `pandas`

### Start Services

**Terminal 1: FastAPI Backend**
```bash
cd src/api
python api.py
# or
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2: Streamlit Main App**
```bash
cd src/ui
streamlit run app.py --server.port 8501
```

**Terminal 3: Streamlit Chatbot UI (Optional)**
```bash
cd src/ui
streamlit run streamlit_chatbot_ui.py --server.port 8502
```

### Access URLs
- **Main App**: http://localhost:8501
- **Chatbot**: http://localhost:8502
- **API Docs**: http://localhost:8000/api/docs
- **API RedOc**: http://localhost:8000/api/redoc

---

## Key Improvements

✅ **Persistent Data Storage**: All form submissions now save to MySQL
✅ **Data Retrieval**: Search applicants by multiple criteria
✅ **Data Updates**: Modify applicant information and loan details
✅ **Session Independence**: Data survives browser closes and session expiration
✅ **Real-time Statistics**: Dashboard shows database statistics
✅ **Scalability**: Database pooling supports concurrent requests
✅ **Backward Compatibility**: Existing agents and orchestrator continue working
✅ **Clean Architecture**: Separation of concerns with db_service layer

---

## Backward Compatibility

- ✅ Existing agent code unchanged
- ✅ Orchestrator API (port 8001) continues working
- ✅ MCP servers unaffected
- ✅ Risk calculations same as before
- ✅ Session state UI features still available
- ✅ In-memory storage optional for testing

---

## Future Enhancements

1. **Distributed MCP Mode**: Add write tools to `applicant_db_server.js` for distributed operations
2. **Audit Logging**: Track all database changes with user attribution
3. **Advanced Analytics**: Dashboard with trend analysis and reporting
4. **Export/Import**: Bulk operations for data migration
5. **API Rate Limiting**: Protect endpoints from abuse
6. **Caching Layer**: Redis caching for frequently accessed data

---

## Summary

The refactoring successfully transforms the Loan Approval System from a **session-based, in-memory application** to a **database-driven, persistent system** with comprehensive search and update capabilities. Users can now:

1. **Submit applications** → Stored permanently in MySQL
2. **Search applicants** → By ID, location, employment, credit score, etc.
3. **Update records** → Load and modify existing applicants
4. **View statistics** → Real-time database analytics
5. **Work across sessions** → Data persists between browser sessions

All changes maintain backward compatibility with existing agents, orchestrator, and MCP servers.
