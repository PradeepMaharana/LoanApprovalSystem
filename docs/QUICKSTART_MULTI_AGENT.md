# Multi-Agent System - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem

# Install required packages
pip install fastapi uvicorn streamlit langgraph langchain langchain-anthropic \
    mysql-connector-python httpx requests pydantic
```

### Step 2: Configure Environment

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: Verify MySQL is running
mysql -u root -p'Tek@12345' -e "SELECT 1;"
```

### Step 3: Start the Services

**Terminal 1 - Start FastAPI Orchestrator:**
```bash
python orchestrator_api.py
```
Output: `INFO:     Uvicorn running on http://0.0.0.0:8001`

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run streamlit_chatbot_ui.py
```
Output: `Local URL: http://localhost:8501`

### Step 4: Process Your First Loan Application

1. Open browser to `http://localhost:8501`
2. Enter applicant ID: `APP-2026-000001`
3. Click Send
4. Wait for results (typically 10-15 seconds)

---

## 📊 System Components

### 1. Streamlit UI (`streamlit_chatbot_ui.py`)

**Port:** 8501 (http://localhost:8501)

**Features:**
- Chat interface for loan applications
- Real-time processing display
- Results visualization with tabs
- Analytics dashboard
- Processing status tracking

**How to Use:**
```
1. Enter applicant ID (e.g., APP-2026-000001)
2. View processing stages
3. See LLM analysis
4. Download results
```

### 2. FastAPI Orchestrator (`orchestrator_api.py`)

**Port:** 8001 (http://localhost:8001)

**Key Endpoints:**

```bash
# Process single application
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"applicant_id": "APP-2026-000001"}'

# Get processing status
curl http://localhost:8001/status/APP-2026-000001

# Get analytics
curl http://localhost:8001/analytics/summary

# Health check
curl http://localhost:8001/health
```

### 3. LangGraph Orchestrator (`langgraph_orchestrator.py`)

**Workflow Stages:**

```
1. Fetch Application Data
   ↓
2. Applicant Profile Analysis (Agent 1)
   ↓
3. Financial Risk Analysis (Agent 2)
   ↓
4. Loan Decision Synthesis (Agent 3)
   ↓
5. Compliance & Action Orchestration (Agent 4)
   ↓
6. LLM Synthesis (Claude Sonnet 4.6)
   ↓
7. Final Recommendation
```

### 4. MCP Client (`mcp_client.py`)

Provides two modes:

```python
# Mode 1: Remote MCP Servers (via HTTP)
mcp_client = MCPClient(servers_config)

# Mode 2: Local Agents (direct Python)
mcp_client = LocalMCPClient()
mcp_client.get_applicant_profile(applicant_id)
```

---

## 💻 Testing the System

### Quick Test via API

```bash
# Start orchestrator in one terminal
python orchestrator_api.py

# In another terminal, test the API
python -c "
import requests
import json

response = requests.post(
    'http://localhost:8001/process',
    json={'applicant_id': 'APP-2026-000001'}
)

result = response.json()
print('Decision:', result['decision'])
print('Risk Score:', result['risk_score'])
print('Confidence:', result['confidence'])
print('Case ID:', result['case_id'])
"
```

### Batch Processing Test

```bash
# Process multiple applications
curl -X POST http://localhost:8001/batch-process \
  -H "Content-Type: application/json" \
  -d '[
    {"applicant_id": "APP-2026-000001"},
    {"applicant_id": "APP-2026-000002"},
    {"applicant_id": "APP-2026-000003"}
  ]' | python -m json.tool
```

### WebSocket Test

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8001/ws/process/APP-2026-000001
```

---

## 📈 Processing Flow

### Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────┐
│ User enters "APP-2026-000001" in Streamlit UI          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Streamlit sends HTTP POST  │
        │ /process with applicant_id │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ FastAPI receives request   │
        │ Invokes LangGraph          │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────────────┐
        │ LangGraph executes 7 stages:       │
        │ 1. Fetch Application Data          │
        │ 2. Applicant Profile Analysis      │
        │ 3. Financial Risk Analysis         │
        │ 4. Loan Decision Synthesis         │
        │ 5. Compliance Orchestration        │
        │ 6. LLM Synthesis (Claude)          │
        │ 7. Final Recommendation            │
        └────────────┬───────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Each stage invokes agents  │
        │ via MCP client (LocalAgent)│
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Agents read from MySQL     │
        │ database tables:           │
        │ - applicants               │
        │ - loan_applications        │
        │ - risk_assessments         │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ LLM (Claude) synthesizes   │
        │ all analysis results       │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ FastAPI returns formatted  │
        │ response with decision,    │
        │ risk scores, LLM analysis  │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Streamlit displays:        │
        │ - Chat response            │
        │ - Processing stages        │
        │ - Risk scores              │
        │ - LLM analysis             │
        │ - Case ID                  │
        └─────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Issue: "Failed to connect to orchestrator API"

**Solution:**
```bash
# Make sure orchestrator is running
python orchestrator_api.py

# Check if port 8001 is available
lsof -i :8001

# If port is busy, kill process
kill -9 <PID>
```

### Issue: "Applicant not found"

**Solution:**
```bash
# Verify applicant exists in database
mysql -u root -p'Tek@12345' loan_approval_system \
  -e "SELECT applicant_id FROM applicants LIMIT 5;"

# Use one of the returned IDs
```

### Issue: "API Error: 500"

**Solution:**
```bash
# Check orchestrator logs
# Look for error messages in terminal running orchestrator_api.py

# Verify MCP client initialization
# Add debug logging in orchestrator_api.py

# Check database connectivity
mysql -u root -p'Tek@12345' loan_approval_system -e "SELECT 1;"
```

### Issue: "Processing timeout"

**Solution:**
```bash
# Use asynchronous endpoint instead
curl -X POST http://localhost:8001/process-async \
  -H "Content-Type: application/json" \
  -d '{"applicant_id": "APP-2026-000001"}'

# Check status
curl http://localhost:8001/status/APP-2026-000001
```

### Issue: "ModuleNotFoundError: No module named 'langgraph'"

**Solution:**
```bash
# Install missing packages
pip install langgraph langchain langchain-anthropic

# Or install all dependencies
pip install -r requirements.txt
```

---

## 📊 Monitoring & Analytics

### View System Health

```bash
curl http://localhost:8001/health
# Returns: {"status": "healthy", "timestamp": "...", "version": "1.0.0"}
```

### Get Processing Summary

```bash
curl http://localhost:8001/analytics/summary
# Returns: approval rate, average risk score, total processed, etc.
```

### Get Decision Breakdown

```bash
curl http://localhost:8001/analytics/decisions
# Returns: count and stats for each decision type
```

---

## 📝 Configuration

### Change API Port

Edit `orchestrator_api.py`:
```python
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Change here
        log_level="info"
    )
```

### Change Streamlit Port

Edit `streamlit_chatbot_ui.py` or run with:
```bash
streamlit run streamlit_chatbot_ui.py --server.port 8502
```

### Change Database Connection

Edit `mcp_client.py` - LocalMCPClient.__init__():
```python
self.db_config = {
    'host': 'localhost',        # Change host
    'user': 'root',             # Change user
    'password': 'Tek@12345',    # Change password
    'database': 'loan_approval_system'
}
```

### Change Claude Model

Edit `langgraph_orchestrator.py`:
```python
llm = ChatAnthropic(
    model="claude-opus-4-1"  # Change model here
)
```

---

## 📚 Key Files

| File | Purpose | Port |
|------|---------|------|
| `orchestrator_api.py` | FastAPI microservice | 8001 |
| `streamlit_chatbot_ui.py` | Streamlit UI | 8501 |
| `langgraph_orchestrator.py` | LangGraph workflow | N/A |
| `mcp_client.py` | MCP client | N/A |
| `agents/` | Individual agents | N/A |
| `mcp_servers/` | MCP server implementations | Various |

---

## 🎯 Common Tasks

### Process Single Application

```bash
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"applicant_id": "APP-2026-000001"}'
```

### Process Multiple Applications

```bash
curl -X POST http://localhost:8001/batch-process \
  -H "Content-Type: application/json" \
  -d '[
    {"applicant_id": "APP-2026-000001"},
    {"applicant_id": "APP-2026-000002"}
  ]'
```

### Get Processing Result

```bash
curl http://localhost:8001/process/APP-2026-000001
```

### Stream Results via WebSocket

```bash
wscat -c ws://localhost:8001/ws/process/APP-2026-000001
```

### View Analytics

```bash
curl http://localhost:8001/analytics/summary | python -m json.tool
```

---

## 🔄 Workflow Stages Explained

### Stage 1: Fetch Application Data
- Retrieves applicant ID and basic metadata
- Checks if applicant exists
- Time: ~0.5 seconds

### Stage 2: Applicant Profile Analysis
- Calls Agent 1 (ApplicantProfileAgent)
- Analyzes: Income stability, employment risk, credit history
- Time: 1-2 seconds

### Stage 3: Financial Risk Analysis
- Calls Agent 2 (FinancialRiskAgent)
- Analyzes: DTI ratio, credit risk, loan amount risk, anomalies
- Time: 2-3 seconds

### Stage 4: Loan Decision Synthesis
- Calls Agent 3 (LoanDecisionAgent)
- Combines scores, classifies decision, calculates terms
- Time: 1-2 seconds

### Stage 5: Compliance & Action Orchestration
- Calls Agent 4 (ComplianceActionOrchestrator)
- Updates status, sends notifications, logs actions
- Time: 1-2 seconds

### Stage 6: LLM Synthesis (Claude)
- Invokes Claude Sonnet 4.6
- Generates executive summary, strengths, concerns, recommendation letter
- Time: 3-5 seconds

### Stage 7: Final Recommendation
- Formats results for return
- Includes all analysis and recommendations
- Time: <1 second

**Total Time: 9-15 seconds per application**

---

## 🎓 Next Steps

1. **Run your first application** - Follow "5-Minute Setup"
2. **Review results** - Check UI and API responses
3. **Test batch processing** - Process multiple applications
4. **Customize prompts** - Modify Claude prompts in `langgraph_orchestrator.py`
5. **Add authentication** - Secure API endpoints with JWT
6. **Deploy** - Move to production environment

---

## 📞 Support

### Check Logs

```bash
# Orchestrator logs appear in terminal running orchestrator_api.py
# Streamlit logs appear in terminal running streamlit run

# Enable debug logging
export LOG_LEVEL=DEBUG
python orchestrator_api.py
```

### Verify Services

```bash
# Check FastAPI is running
curl http://localhost:8001/health

# Check Streamlit is running
curl http://localhost:8501

# Check database
mysql -u root -p'Tek@12345' -e "SELECT 1;"
```

### Check Database Applicants

```bash
mysql -u root -p'Tek@12345' loan_approval_system \
  -e "SELECT applicant_id, full_name FROM applicants LIMIT 10;"
```

---

## ⚡ Performance Tips

1. **Use async endpoint for long operations**
   ```bash
   POST /process-async
   ```

2. **Batch multiple applications**
   ```bash
   POST /batch-process
   ```

3. **Monitor via WebSocket for real-time updates**
   ```bash
   WS /ws/process/{applicant_id}
   ```

4. **Cache frequently accessed data**
   - Modify `langgraph_orchestrator.py` to add caching

5. **Use connection pooling**
   - Already implemented in MCP clients

---

## 📚 Documentation

- **Full Guide:** See `LANGGRAPH_WORKFLOW_GUIDE.md`
- **Agents:** See `AGENTS_DOCUMENTATION.md`
- **MCP Servers:** See `MCP_SETUP_GUIDE.md`

---

**Ready to go! 🚀 Follow the 5-Minute Setup to get started.**

Generated: 2026-07-01
Version: 1.0.0
