# Quick Start Guide - Database-Driven Loan Approval System

## 📋 What Changed?

Your loan application data is now **automatically saved to the database** when you submit applications through the UI. You can search, update, and retrieve this data anytime.

---

## 🚀 Running the System

### Step 1: Start the FastAPI Backend
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
cd src/api
python api.py
```
✅ Opens on `http://localhost:8000`

### Step 2: Start the Main Streamlit App
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
cd src/ui
streamlit run app.py
```
✅ Opens on `http://localhost:8501`

### Step 3 (Optional): Start the Chatbot UI
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
cd src/ui
streamlit run streamlit_chatbot_ui.py
```
✅ Opens on `http://localhost:8502`

---

## 📝 Submitting a Loan Application

1. **Open the Main App** → `http://localhost:8501`
2. **Fill out the form**:
   - Applicant ID (e.g., `APP-2024-001`)
   - Age, Income, Employment Type, Location
   - Credit Score, Loan Amount, Tenure, Liabilities
3. **Click "✅ Submit Application"**
4. **Success!** → Data saved to database ✅

---

## 🔍 Searching for Applicants

### In Main App (app.py)

1. **Scroll to "🔍 Search & Retrieve Applicants"** section
2. **Click "Search Applicants" tab**
3. **Enter search criteria**:
   - **Applicant ID**: Exact match
   - **Location**: Partial text match
   - **Age Range**: Min/Max
   - **Employment Type**: Dropdown
   - **Credit Score**: Min/Max range
   - **Application Status**: SUBMITTED, APPROVED, etc.
4. **Click "🔎 Search"** to find applicants

### Quick List All Applicants
- Click **"📋 List All"** to see all 100 applicants from database

### Results Actions
- **View results** in searchable dataframe
- **Load to Form**: Select applicant → Click "📝 Load to Form" → Edit in form above

---

## ✏️ Updating an Application

1. **Search** for the applicant you want to update
2. **Click "📝 Load to Form"** on the search result
3. **Scroll up** to the form section
4. **Modify fields** (Age, Income, Loan Amount, etc.)
5. **Click "✅ Submit Application"** again
6. **Updated!** → Changes saved to database ✅

---

## 📊 Viewing Database Statistics

1. **In Main App**, scroll to **"🔍 Search & Retrieve Applicants"**
2. **Click "Database Statistics" tab**
3. **Click "📊 Refresh Statistics"**
4. **See**:
   - Total number of applicants
   - Applications breakdown by status
   - Distribution by employment type
   - Charts and metrics

---

## 💬 Using the Chatbot UI

### Quick Search (Sidebar)
1. **Open Chatbot** → `http://localhost:8502`
2. **Left sidebar** → "🔍 Quick Search" section
3. **Enter Applicant ID** (e.g., `APP-2024-001`)
4. **Click "Search"** → Applicant loaded
5. **Chat with applicant profile context**

### Main Chat
1. **Enter applicant ID** in chat box (e.g., `APP-2024-001`)
2. **Or type**: `Process applicant APP-2024-001`
3. **Bot processes** applicant through orchestrator
4. **View results** in right panel

---

## 🔗 API Endpoints (For Developers)

### Search Applicants
```bash
curl "http://localhost:8000/api/v1/applicants/search?location=New%20York&limit=10"
```

### List All
```bash
curl "http://localhost:8000/api/v1/applicants?page=1&limit=50"
```

### Get Profile
```bash
curl "http://localhost:8000/api/v1/applicants/APP-2024-001"
```

### Submit Application
```bash
curl -X POST "http://localhost:8000/api/v1/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant": {
      "applicant_id": "APP-2024-NEW",
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

### Get Statistics
```bash
curl "http://localhost:8000/api/v1/statistics"
```

### Update Applicant
```bash
curl -X PUT "http://localhost:8000/api/v1/applicants/APP-2024-001" \
  -H "Content-Type: application/json" \
  -d '{"income": 130000, "location": "San Francisco, CA"}'
```

---

## ✅ Verify Everything Works

### Check 1: Can I Submit?
1. Open app.py
2. Fill form and click "Submit"
3. See success message ✅

### Check 2: Is Data Saved?
1. Close browser (close session)
2. Reopen app.py
3. Scroll to "Search & Retrieve Applicants"
4. Click "📋 List All"
5. See your submitted application ✅

### Check 3: Can I Search?
1. Enter search criteria
2. Click "🔎 Search"
3. See results ✅

### Check 4: Can I Update?
1. Search for an applicant
2. Click "📝 Load to Form"
3. Modify a field
4. Click "Submit"
5. Search again to verify change ✅

---

## 🛠️ Troubleshooting

### ❌ API Connection Error
- **Problem**: "Cannot connect to API server"
- **Solution**: 
  - Make sure `python api.py` is running on terminal 1
  - Check `http://localhost:8000/health` in browser

### ❌ Database Connection Error
- **Problem**: "Database service not available"
- **Solution**:
  - Make sure MySQL is running
  - Check database name is `loan_approval_system`
  - Check credentials in `src/database/db_service.py`

### ❌ No Results in Search
- **Problem**: "No applicants found"
- **Solution**:
  - First submit a test application
  - Use "📋 List All" to see what's in database
  - Try searching with fewer criteria

### ❌ Port Already In Use
- **Problem**: "Address already in use"
- **Solution**:
  ```bash
  # Kill the process using the port
  lsof -ti:8000 | xargs kill -9  # For port 8000
  lsof -ti:8501 | xargs kill -9  # For port 8501
  ```

---

## 📚 Key Features

✅ **Persistent Storage** - Data saved permanently to MySQL
✅ **Search Multiple Ways** - By ID, location, credit score, status, etc.
✅ **Update Records** - Load and modify existing applications
✅ **Session Independent** - Data survives browser close
✅ **Statistics Dashboard** - Real-time database insights
✅ **API First** - All operations accessible via REST API
✅ **Backward Compatible** - Works with existing agents and orchestrator

---

## 📖 Documentation

- **Full Architecture**: See `REFACTORING_GUIDE.md`
- **API Docs**: Visit `http://localhost:8000/api/docs`
- **Database Schema**: Check `src/database/mysql_setup.py`

---

## 🎯 Next Steps

1. ✅ Start the API server
2. ✅ Start Streamlit app
3. ✅ Submit a test application
4. ✅ Search and find your application
5. ✅ Modify and update it
6. ✅ View database statistics

**Enjoy using the database-driven Loan Approval System!** 🎉
