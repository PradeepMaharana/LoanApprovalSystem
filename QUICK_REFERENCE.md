# 🎯 Quick Reference Card - LoanApprovalSystem

## 📍 Where Is Everything?

### Source Code (`src/`)
```
src/core/          → Business logic & workflow engine
src/agents/        → AI agents (5 types)
src/api/           → REST API endpoints
src/ui/            → Streamlit interfaces
src/database/      → MySQL setup & management
src/mcp/           → MCP servers & client
src/config/        → Configuration files
src/utils/         → Helper utilities & data generation
```

### Documentation & Resources
```
docs/              → All documentation (20+ guides)
data/              → Sample data (JSON, CSV, Excel)
tests/             → Automated tests
scripts/           → Deployment scripts
notebooks/         → Reserved for analysis
```

## 🚀 How to Run?

### API Server
```bash
bash scripts/run_api.sh
# OR
python -m src.api.api
```
**Runs at:** `http://localhost:5000`

### Streamlit App
```bash
streamlit run src/ui/app.py
```
**Runs at:** `http://localhost:8501`

### Chatbot UI
```bash
streamlit run src/ui/streamlit_chatbot_ui.py
```

### Database Setup
```bash
python src/database/mysql_enhanced_setup.py
```

### Sample Data Generation
```bash
python -m src.utils.generate_sample_data
```

## 📚 Key Files

| Purpose | Location |
|---------|----------|
| **API Routes** | `src/api/api.py` |
| **Main App** | `src/ui/app.py` |
| **Orchestrator** | `src/core/langgraph_orchestrator.py` |
| **Risk Assessment** | `src/core/advanced_risk_assessment.py` |
| **Agents** | `src/agents/*.py` (5 files) |
| **Database** | `src/database/mysql_enhanced_setup.py` |
| **MCP Client** | `src/mcp/mcp_client.py` |
| **Configuration** | `src/config/config.py` |
| **Env Variables** | `.env` (create from `.env.example`) |

## 🔗 How to Import?

```python
# Module imports
from src.core import langgraph_orchestrator
from src.agents import financial_risk_agent
from src.api import api
from src.database import mysql_setup
from src.config import config
from src.utils import generate_sample_data

# Class/function imports
from src.core.langgraph_orchestrator import LangGraphOrchestrator
from src.agents.financial_risk_agent import FinancialRiskAgent
from src.api.api import app as flask_app
```

## ⚙️ Setup Checklist

- [ ] `cd /home/ubuntu/Desktop/LoanApprovalSystem`
- [ ] `source venv/bin/activate`
- [ ] `pip install -r requirements.txt`
- [ ] `cp .env.example .env`
- [ ] Edit `.env` with database credentials
- [ ] `python src/database/mysql_enhanced_setup.py`
- [ ] `bash scripts/run_api.sh` (in one terminal)
- [ ] `streamlit run src/ui/app.py` (in another terminal)

## 📖 Documentation Map

| Need | Read |
|------|------|
| **Overview** | `README.md` or `PROJECT_STRUCTURE.md` |
| **Setup** | `DEVELOPER_GUIDE.md` |
| **First Steps** | `docs/QUICK_START.md` |
| **API Docs** | `docs/API_DOCUMENTATION.md` |
| **Agent Docs** | `docs/AGENTS_DOCUMENTATION.md` |
| **Database** | `docs/MYSQL_SETUP_GUIDE.md` |
| **Workflows** | `docs/LANGGRAPH_WORKFLOW_GUIDE.md` |
| **Risk Scoring** | `docs/ADVANCED_RISK_ASSESSMENT_GUIDE.md` |
| **MCP Integration** | `docs/MCP_SETUP_GUIDE.md` |
| **All Guides** | See `FOLDER_STRUCTURE_GUIDE.md` |

## 🤖 AI Agents

| Agent | File | Purpose |
|-------|------|---------|
| **Profile Agent** | `src/agents/applicant_profile_agent.py` | Analyzes applicant background |
| **Risk Agent** | `src/agents/financial_risk_agent.py` | Evaluates financial metrics |
| **Compliance Agent** | `src/agents/compliance_action_agent.py` | Checks regulations |
| **Decision Agent** | `src/agents/loan_decision_agent.py` | Makes final decision |
| **Processor** | `src/agents/integrated_loan_processor.py` | Orchestrates all agents |

## 🔧 Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Orchestrator** | `src/core/langgraph_orchestrator.py` | Manages agent workflows |
| **Risk Scoring** | `src/core/advanced_risk_assessment.py` | Calculates risk scores |
| **API** | `src/api/api.py` | REST endpoints |
| **Streamlit** | `src/ui/app.py` | Web interface |
| **MySQL** | `src/database/mysql_enhanced_setup.py` | Database setup |

## 📊 Sample Data Locations

```
data/Loan_Applicants_Sample_Data.json    # JSON format
data/Loan_Applicants_Sample_Data.csv     # CSV format
data/Loan_Applicants_Sample_Data.xlsx    # Excel format
```

## 🐛 Common Issues

### Import Error: "No module named 'src'"
```python
# Make sure you're in the project root:
cd /home/ubuntu/Desktop/LoanApprovalSystem
python your_script.py  # NOT python /src/your_script.py
```

### Database Connection Failed
```bash
# Check .env has correct credentials
cat .env | grep MYSQL

# Then reinitialize database
python src/database/mysql_enhanced_setup.py
```

### Streamlit Won't Start
```bash
# Make sure venv is activated
source venv/bin/activate

# Then run Streamlit
streamlit run src/ui/app.py
```

## 📦 Project Statistics

- **Total Files:** 58
- **Python Modules:** 26 (.py files)
- **MCP Servers:** 4 (.js files)
- **Documentation:** 20+ guides
- **Directories:** 15 organized folders
- **Sample Data Formats:** 3 (JSON, CSV, Excel)

## 💡 Development Tips

### Adding New Agent
1. Create file in `src/agents/`
2. Follow naming: `*_agent.py`
3. Update `src/agents/__init__.py`

### Adding API Endpoint
1. Add route to `src/api/api.py`
2. Test with `pytest tests/`

### Adding Configuration
1. Add to `src/config/config.py`
2. Use environment variables in `.env`

### Adding Utility
1. Create in `src/utils/`
2. Export in `src/utils/__init__.py`

## 🎓 Learning Path

1. Start with `DEVELOPER_GUIDE.md` - understand the setup
2. Read `FOLDER_STRUCTURE_GUIDE.md` - understand the layout
3. Check `docs/QUICK_START.md` - get it running
4. Review `docs/AGENTS_DOCUMENTATION.md` - understand agents
5. Explore source code in `src/` - dive deeper
6. Read API docs to extend functionality
7. Check tests for examples of usage

## 🔐 Security Notes

- **Never commit `.env`** - it contains secrets
- **Use `.env.example`** - as a template
- **Don't hardcode secrets** - use environment variables
- **Validate user input** - at API boundaries
- **Keep dependencies updated** - regularly run `pip update`

## 📞 Quick Help

| Topic | File |
|-------|------|
| Project structure | `PROJECT_STRUCTURE.md` |
| Folder layout | `FOLDER_STRUCTURE_GUIDE.md` |
| Development setup | `DEVELOPER_GUIDE.md` |
| Getting started | `docs/QUICK_START.md` |
| API reference | `docs/API_DOCUMENTATION.md` |
| Agent specs | `docs/AGENTS_DOCUMENTATION.md` |
| Database setup | `docs/MYSQL_SETUP_GUIDE.md` |
| Workflow guide | `docs/LANGGRAPH_WORKFLOW_GUIDE.md` |

## ✅ You're All Set!

Your project is now organized professionally and ready for development.

**Next steps:**
1. Read `DEVELOPER_GUIDE.md`
2. Run the setup commands above
3. Start building!

---
*Last Updated: 2026-07-03*
