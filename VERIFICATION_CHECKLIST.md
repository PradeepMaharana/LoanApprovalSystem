# 🔍 Verification Checklist - Database-Driven Loan Approval System

## Pre-Flight Checks

Before starting the system, verify these prerequisites:

### ✅ Environment Setup
- [ ] MySQL server running (`service mysql status`)
- [ ] Database exists: `loan_approval_system`
- [ ] Database user has credentials: `root` / `Tek@12345`
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated (if using one)
- [ ] Dependencies installed: `pip install -r requirements.txt`

### ✅ File Structure
- [ ] `src/database/db_service.py` exists (new file)
- [ ] `src/api/api.py` modified with DB persistence
- [ ] `src/ui/streamlit_integration.py` has search methods
- [ ] `src/ui/app.py` has search panel
- [ ] `src/ui/streamlit_chatbot_ui.py` has sidebar search
- [ ] Documentation files created

---

## Component Verification

### Database Service Layer (`db_service.py`)

```python
# Test import
from src.database.db_service import DatabaseService, get_db_service

# Verify methods exist:
- [ ] insert_applicant()
- [ ] insert_loan_application()
- [ ] update_applicant()
- [ ] update_loan_application()
- [ ] search_applicants()
- [ ] get_applicant_with_application()
- [ ] search_by_status()
- [ ] list_all_applicants()
- [ ] get_statistics()
- [ ] connect()
- [ ] disconnect()
```

### REST API (`api.py`)

```python
# Startup event
- [ ] @app.on_event("startup") initializes db_service
- [ ] @app.on_event("shutdown") closes connection

# Endpoints added:
- [ ] POST /api/v1/applications - Modified to use DB
- [ ] GET /api/v1/applicants/search - New search endpoint
- [ ] GET /api/v1/applicants - New list endpoint
- [ ] GET /api/v1/applicants/{applicant_id} - New get endpoint
- [ ] PUT /api/v1/applicants/{applicant_id} - New update endpoint
- [ ] GET /api/v1/statistics - New statistics endpoint
```

### Streamlit Integration (`streamlit_integration.py`)

```python
# New methods:
- [ ] search_applicants(**filters)
- [ ] list_all_applicants(page, limit)
- [ ] get_applicant_profile(applicant_id)
- [ ] update_applicant(applicant_id, update_data)
- [ ] get_statistics()
- [ ] create_loan_application(profile, details)
```

### Main App (`app.py`)

```python
# UI Components added:
- [ ] Search & Retrieve Applicants section
- [ ] Search criteria inputs (6+ filters)
- [ ] Search and List All buttons
- [ ] Results dataframe display
- [ ] Load to Form functionality
- [ ] Database Statistics tab
- [ ] Statistics refresh button
- [ ] Charts for status and employment
```

### Chatbot App (`streamlit_chatbot_ui.py`)

```python
# Sidebar enhancement:
- [ ] Quick Search section added
- [ ] Applicant ID search input
- [ ] Search button functional
- [ ] Auto-loads applicant context
```

---

## Functional Verification

### Test Scenario 1: Submit New Application

**Steps**:
1. [ ] Start API server: `python src/api/api.py`
2. [ ] Start Streamlit app: `streamlit run src/ui/app.py`
3. [ ] Fill application form with test data
   - [ ] Applicant ID: `APP-TEST-001`
   - [ ] Age: `35`
   - [ ] Income: `120000`
   - [ ] Employment: `Salaried`
   - [ ] Credit Score: `750`
   - [ ] Loan Amount: `300000`
   - [ ] Location: `New York, NY`
4. [ ] Click "✅ Submit Application"
5. [ ] Verify success message appears
6. [ ] **Check database**:
   ```sql
   SELECT * FROM applicants WHERE applicant_id = 'APP-TEST-001';
   SELECT * FROM loan_applications WHERE applicant_id = 'APP-TEST-001';
   ```
   - [ ] Data appears in applicants table
   - [ ] Data appears in loan_applications table
   - [ ] created_at timestamp is recent
   - [ ] updated_at timestamp is recent

**Expected Result**: ✅ Data persisted to MySQL

---

### Test Scenario 2: Search Applicant

**Steps**:
1. [ ] Scroll to "🔍 Search & Retrieve Applicants" section
2. [ ] Click "Search Applicants" tab
3. [ ] Enter `Applicant ID`: `APP-TEST-001`
4. [ ] Click "🔎 Search"
5. [ ] Verify results appear
   - [ ] Dataframe shows 1 result
   - [ ] Data matches submitted application
   - [ ] All fields populated correctly

**Expected Result**: ✅ Search returns correct data

---

### Test Scenario 3: List All Applicants

**Steps**:
1. [ ] In Search Applicants tab
2. [ ] Click "📋 List All"
3. [ ] Verify results appear
   - [ ] Shows multiple applicants (100+ if DB has data)
   - [ ] Pagination info displayed
   - [ ] Data from database, not session state

**Expected Result**: ✅ All applicants loaded from database

---

### Test Scenario 4: Load to Form and Update

**Steps**:
1. [ ] Search for `APP-TEST-001` (from Scenario 1)
2. [ ] In search results, click "📝 Load to Form"
3. [ ] Verify form populated:
   - [ ] Applicant ID: `APP-TEST-001`
   - [ ] Age: `35`
   - [ ] Income: `120000`
   - [ ] All fields match search result
4. [ ] Modify a field: Change Income to `130000`
5. [ ] Click "✅ Submit Application"
6. [ ] Search again for same applicant
7. [ ] Verify updated value:
   - [ ] Income now shows `130000`
   - [ ] updated_at timestamp changed

**Expected Result**: ✅ Update persisted to database

---

### Test Scenario 5: Database Statistics

**Steps**:
1. [ ] Scroll to "🔍 Search & Retrieve Applicants"
2. [ ] Click "Database Statistics" tab
3. [ ] Click "📊 Refresh Statistics"
4. [ ] Verify metrics displayed:
   - [ ] Total Applicants: Shows count (≥1 from tests)
   - [ ] Total Applications: Shows count (≥1 from tests)
   - [ ] Applications by Status: Chart or breakdown
   - [ ] Applicants by Employment: Chart or breakdown

**Expected Result**: ✅ Statistics retrieved from database

---

### Test Scenario 6: Cross-Session Persistence

**Steps**:
1. [ ] Submit an application (if not already done)
   - Note the Applicant ID
2. [ ] Close browser tab (end Streamlit session)
3. [ ] Close Streamlit terminal (CTRL+C)
4. [ ] Wait 3 seconds
5. [ ] Restart Streamlit: `streamlit run src/ui/app.py`
6. [ ] Go to Search section
7. [ ] Click "📋 List All"
8. [ ] Search for previously submitted applicant
9. [ ] Verify:
   - [ ] Applicant still exists
   - [ ] All data intact and unchanged
   - [ ] No data loss occurred

**Expected Result**: ✅ Data persists across sessions

---

### Test Scenario 7: Advanced Search Filters

**Steps**:
1. [ ] Go to Search Applicants tab
2. [ ] Try each search criterion:
   - [ ] **By Location**: Enter `New York` → Results filtered
   - [ ] **By Age Range**: Min=30, Max=40 → Results filtered
   - [ ] **By Employment**: Select `Salaried` → Results filtered
   - [ ] **By Credit Score Range**: Min=700, Max=800 → Results filtered
   - [ ] **By Status**: Select `SUBMITTED` → Results filtered
3. [ ] Combine multiple criteria:
   - [ ] Location + Employment
   - [ ] Age Range + Credit Score
   - [ ] All criteria together
4. [ ] Verify:
   - [ ] All filters work independently
   - [ ] Multiple filters combine with AND logic
   - [ ] Results accurate

**Expected Result**: ✅ All search filters functional

---

### Test Scenario 8: Chatbot Quick Search

**Steps**:
1. [ ] Open chatbot: `streamlit run src/ui/streamlit_chatbot_ui.py`
2. [ ] Look at left sidebar
3. [ ] Find "🔍 Quick Search" section
4. [ ] Enter an Applicant ID from database
5. [ ] Click "Search"
6. [ ] Verify:
   - [ ] `st.session_state.applicant_id` populated
   - [ ] Chat interface shows applicant context
   - [ ] Ready to process application

**Expected Result**: ✅ Chatbot search works

---

### Test Scenario 9: API Direct Testing

**Steps**:
1. [ ] Open terminal
2. [ ] Test each endpoint:

**Search API**:
```bash
[ ] curl "http://localhost:8000/api/v1/applicants/search?applicant_id=APP-TEST-001"
    Expected: JSON with matching applicant
```

**List API**:
```bash
[ ] curl "http://localhost:8000/api/v1/applicants?page=1&limit=10"
    Expected: JSON with pagination info and applicants array
```

**Get Profile API**:
```bash
[ ] curl "http://localhost:8000/api/v1/applicants/APP-TEST-001"
    Expected: Single applicant object with all details
```

**Statistics API**:
```bash
[ ] curl "http://localhost:8000/api/v1/statistics"
    Expected: JSON with totals and breakdowns
```

**Expected Result**: ✅ All API endpoints return correct JSON

---

### Test Scenario 10: Error Handling

**Steps**:
1. [ ] Search for non-existent applicant: `DOES-NOT-EXIST`
   - [ ] Should return: "No applicants found" message
2. [ ] Try to load non-existent applicant profile
   - [ ] Should return: 404 error
3. [ ] Stop MySQL server and try to submit
   - [ ] Should return: "Database service not available" error
4. [ ] Stop API server and try to search from UI
   - [ ] Should return: "Cannot connect to API server" error
5. [ ] Verify errors are user-friendly and descriptive

**Expected Result**: ✅ Errors handled gracefully

---

## API Specification Verification

### Submit Application
```
✅ Endpoint: POST /api/v1/applications
✅ Request Body: {applicant: {...}, loan_details: {...}}
✅ Response: LoanApplicationResponse with application_id
✅ Database: INSERT into applicants AND loan_applications
✅ Status Code: 201 (Created)
```

### Search Applicants
```
✅ Endpoint: GET /api/v1/applicants/search
✅ Query Params: applicant_id, location, age_min, age_max, employment_type, 
                 credit_score_min, credit_score_max, application_status, limit
✅ Response: {count: int, data: [objects]}
✅ Status Code: 200 (OK)
```

### List All Applicants
```
✅ Endpoint: GET /api/v1/applicants
✅ Query Params: page, limit
✅ Response: {page, limit, total, total_pages, data: [objects]}
✅ Status Code: 200 (OK)
```

### Get Applicant Profile
```
✅ Endpoint: GET /api/v1/applicants/{applicant_id}
✅ Response: Complete applicant object with relations
✅ Status Code: 200 (OK) or 404 (Not Found)
```

### Update Applicant
```
✅ Endpoint: PUT /api/v1/applicants/{applicant_id}
✅ Request Body: {age?, income?, employment_type?, location?}
✅ Response: {success: bool, message: str, updated_fields: [...]}
✅ Database: UPDATE applicants/loan_applications
✅ Status Code: 200 (OK) or 404 (Not Found)
```

### Statistics
```
✅ Endpoint: GET /api/v1/statistics
✅ Response: {total_applicants, total_applications, 
             applications_by_status, applicants_by_employment}
✅ Status Code: 200 (OK)
```

---

## Documentation Verification

- [ ] `REFACTORING_GUIDE.md` exists and is comprehensive
- [ ] `QUICK_START.md` exists and is user-friendly
- [ ] `REFACTORING_SUMMARY.md` exists with overview
- [ ] API documentation accessible at `/api/docs`
- [ ] All code is well-commented
- [ ] Function signatures are clear

---

## Performance Checks (Optional)

- [ ] Search completes in <1 second with 1000 records
- [ ] List All completes in <2 seconds with pagination
- [ ] Database connection pool efficient (max 10 connections)
- [ ] No N+1 query problems in searches
- [ ] Proper indexes on search fields

---

## Final Sign-Off

### All Tests Complete?
- [ ] Yes, all scenarios passed
- [ ] Database integration verified
- [ ] UI functionality working
- [ ] API endpoints responding correctly
- [ ] Error handling working
- [ ] Documentation complete

### System Status
- [ ] ✅ **READY FOR PRODUCTION**

---

## Quick Health Check (1 minute)

```bash
# 1. API Server Health
curl http://localhost:8000/health

# 2. Database Connection
curl http://localhost:8000/api/v1/statistics

# 3. Streamlit App
# Open http://localhost:8501 in browser

# 4. Try one search
# Search for any applicant in database
```

**If all 4 checks pass**: ✅ **System is operational**

---

## Troubleshooting Guide

### Issue: "Database service not available"
- [ ] Check MySQL is running: `service mysql status`
- [ ] Verify database exists: `mysql -u root -p -e "USE loan_approval_system;"`
- [ ] Check credentials in `db_service.py`

### Issue: "Cannot connect to API server"
- [ ] Check API is running: `http://localhost:8000/health`
- [ ] Check port 8000 is not in use: `lsof -i :8000`

### Issue: Search returns empty
- [ ] Verify data exists: `SELECT COUNT(*) FROM applicants;`
- [ ] Try "📋 List All" first
- [ ] Check search criteria are valid

### Issue: Streamlit won't start
- [ ] Check Python 3.8+: `python --version`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Check port 8501 not in use: `lsof -i :8501`

---

## Sign-Off

**Date**: ________
**Tester**: ________________
**Status**: [ ] All Pass [ ] Needs Fixes
**Notes**: _____________________________________________

---

**Verification Complete** ✅
