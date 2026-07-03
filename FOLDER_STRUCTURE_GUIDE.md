# 📁 LoanApprovalSystem - Professional Folder Structure

## Complete Project Layout

```
LoanApprovalSystem/
│
├── 📁 src/                                    # ⭐ MAIN SOURCE CODE
│   ├── __init__.py                           # Package entry point
│   │
│   ├── 📁 core/                              # 🔧 Core Business Logic
│   │   ├── __init__.py
│   │   ├── langgraph_orchestrator.py          # Workflow orchestration engine
│   │   └── advanced_risk_assessment.py        # Risk scoring algorithms
│   │
│   ├── 📁 agents/                            # 🤖 AI Agents
│   │   ├── __init__.py
│   │   ├── applicant_profile_agent.py         # Profile analysis
│   │   ├── financial_risk_agent.py            # Financial evaluation
│   │   ├── compliance_action_agent.py         # Regulatory compliance
│   │   ├── loan_decision_agent.py             # Decision making
│   │   └── integrated_loan_processor.py       # Orchestration
│   │
│   ├── 📁 api/                               # 🌐 REST API
│   │   ├── __init__.py
│   │   ├── api.py                            # Main endpoints
│   │   └── orchestrator_api.py               # Workflow APIs
│   │
│   ├── 📁 ui/                                # 💻 User Interface
│   │   ├── __init__.py
│   │   ├── app.py                            # Main Streamlit app
│   │   ├── streamlit_chatbot_ui.py           # Chatbot interface
│   │   └── streamlit_integration.py          # UI utilities
│   │
│   ├── 📁 database/                          # 🗄️ Database
│   │   ├── __init__.py
│   │   ├── mysql_setup.py                    # Schema initialization
│   │   └── mysql_enhanced_setup.py           # Advanced setup
│   │
│   ├── 📁 mcp/                               # 🔗 Model Context Protocol
│   │   ├── __init__.py
│   │   ├── mcp_client.py                     # MCP client
│   │   ├── decision_synthesis_server.js      # Decision server
│   │   ├── notification_system_server.js     # Notifications
│   │   ├── risk_rules_server.js              # Rules engine
│   │   └── applicant_db_server.js            # Database server
│   │
│   ├── 📁 config/                            # ⚙️ Configuration
│   │   ├── __init__.py
│   │   ├── config.py                         # Settings
│   │   └── mcp_config.json                   # MCP configuration
│   │
│   └── 📁 utils/                             # 🛠️ Utilities
│       ├── __init__.py
│       └── generate_sample_data.py            # Data generation
│
├── 📁 docs/                                  # 📖 Documentation
│   ├── README.md                             # Project overview
│   ├── QUICK_START.md                        # Getting started
│   ├── API_DOCUMENTATION.md                  # API reference
│   ├── README_API.md                         # API guide
│   ├── AGENTS_DOCUMENTATION.md               # Agent specs
│   ├── MCP_SETUP_GUIDE.md                    # MCP integration
│   ├── MYSQL_SETUP_GUIDE.md                  # DB setup
│   ├── MYSQL_DATABASE_README.md              # DB reference
│   ├── LANGGRAPH_WORKFLOW_GUIDE.md           # Workflow details
│   ├── ADVANCED_RISK_ASSESSMENT_GUIDE.md     # Risk scoring
│   ├── QUICKSTART_MULTI_AGENT.md             # Multi-agent guide
│   ├── SAMPLE_DATA_README.md                 # Data reference
│   ├── IMPLEMENTATION_SUMMARY.md             # Implementation
│   ├── DELIVERY_CHECKLIST.md                 # Deployment
│   ├── PROJECT_SUMMARY.txt                   # Project overview
│   ├── MYSQL_DEPLOYMENT_SUMMARY.txt          # Deployment log
│   ├── MYSQL_DEPLOYMENT_COMPLETE.txt         # Completion status
│   └── requirements.txt                      # Dependencies
│
├── 📁 data/                                  # 📊 Sample Data
│   ├── Loan_Applicants_Sample_Data.json      # JSON format
│   ├── Loan_Applicants_Sample_Data.csv       # CSV format
│   └── Loan_Applicants_Sample_Data.xlsx      # Excel format
│
├── 📁 tests/                                 # ✅ Test Suite
│   └── test_api.py                           # API tests
│
├── 📁 scripts/                               # 🚀 Deployment Scripts
│   ├── deploy_mysql.sh                       # DB deployment
│   └── run_api.sh                            # API startup
│
├── 📁 notebooks/                             # 📓 Jupyter Notebooks
│   └── (reserved for analysis & exploration)
│
├── 📁 venv/                                  # 🐍 Virtual Environment
│   └── (Python dependencies)
│
├── 📄 .env                                   # 🔐 Environment Variables
├── 📄 .env.example                           # 📋 Env Template
├── 📄 .gitignore                             # 🔒 Git Configuration
├── 📄 requirements.txt                       # 📦 Dependencies
├── 📄 PROJECT_STRUCTURE.md                   # 📐 Architecture Guide
└── 📄 DEVELOPER_GUIDE.md                     # 👨‍💻 Dev Guide

```

## Module Hierarchy & Dependencies

```
src/
├── config          ← Configuration (base layer - no dependencies)
├── utils           ← Utilities (base layer)
├── core            ← Business logic (depends on config)
├── agents          ← AI Agents (depends on core, config, utils)
├── database        ← DB Management (depends on config)
├── mcp             ← MCP Integration (depends on config, utils)
├── api             ← REST API (depends on core, agents, mcp)
└── ui              ← Frontend (depends on api, core, agents)
```

## Key Entry Points

### 1. **API Server**
```bash
scripts/run_api.sh
# OR
python -m src.api.api
```
Located at: `src/api/api.py`

### 2. **Streamlit UI**
```bash
streamlit run src/ui/app.py
```
Located at: `src/ui/app.py`

### 3. **Chatbot UI**
```bash
streamlit run src/ui/streamlit_chatbot_ui.py
```
Located at: `src/ui/streamlit_chatbot_ui.py`

### 4. **Database Setup**
```bash
python src/database/mysql_enhanced_setup.py
```
Located at: `src/database/mysql_enhanced_setup.py`

### 5. **Sample Data Generation**
```bash
python -m src.utils.generate_sample_data
```
Located at: `src/utils/generate_sample_data.py`

## File Purposes

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Sensitive environment variables (not in git) |
| `.env.example` | Template for `.env` |
| `.gitignore` | Git exclusion rules |
| `src/config/config.py` | Application configuration |
| `src/config/mcp_config.json` | MCP server configuration |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `QUICK_START.md` | Getting started guide |
| `DEVELOPER_GUIDE.md` | Development instructions |
| `PROJECT_STRUCTURE.md` | Architecture documentation |
| `API_DOCUMENTATION.md` | API endpoint reference |
| `AGENTS_DOCUMENTATION.md` | Agent specifications |

### Test Files

| File | Purpose |
|------|---------|
| `tests/test_api.py` | API endpoint tests |

### Script Files

| File | Purpose |
|------|---------|
| `scripts/run_api.sh` | Start API server |
| `scripts/deploy_mysql.sh` | Deploy database |

### Data Files

| File | Purpose |
|------|---------|
| `data/Loan_Applicants_Sample_Data.json` | Structured JSON data |
| `data/Loan_Applicants_Sample_Data.csv` | Tabular CSV data |
| `data/Loan_Applicants_Sample_Data.xlsx` | Excel spreadsheet data |

## Development Tips

### ✅ DO

- ✅ Keep related code in the same module
- ✅ Use `__init__.py` to expose public APIs
- ✅ Put configuration in `src/config/`
- ✅ Put utilities in `src/utils/`
- ✅ Add tests to `tests/`
- ✅ Document in `docs/`
- ✅ Use environment variables for secrets

### ❌ DON'T

- ❌ Create random directories at the root
- ❌ Mix concerns (agents with API logic)
- ❌ Store secrets in code
- ❌ Put test files with source code
- ❌ Put documentation in root (use `docs/`)
- ❌ Create duplicate code

## Quick Navigation

| Task | Location |
|------|----------|
| Add new agent | `src/agents/` |
| Add API endpoint | `src/api/api.py` |
| Add UI component | `src/ui/` |
| Add configuration | `src/config/` |
| Add utility | `src/utils/` |
| Add database migration | `src/database/` |
| Write tests | `tests/` |
| Update docs | `docs/` |
| Add scripts | `scripts/` |

## Import Convention

```python
# ✓ Correct imports from organized structure
from src.core import langgraph_orchestrator
from src.agents import financial_risk_agent
from src.api import api
from src.database import mysql_setup
from src.config import config

# Or specific imports
from src.core.langgraph_orchestrator import LangGraphOrchestrator
from src.agents.financial_risk_agent import FinancialRiskAgent
```

## Starting Development

1. Read `DEVELOPER_GUIDE.md` for setup
2. Check `QUICK_START.md` for first steps
3. Review `docs/API_DOCUMENTATION.md` for APIs
4. Explore `src/` structure for code
5. Check `docs/AGENTS_DOCUMENTATION.md` for agents

---

**This structure follows professional software engineering practices and is scalable for team development.**

*Last Updated: 2026-07-03*
