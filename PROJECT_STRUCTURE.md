# Project Structure - LoanApprovalSystem

## Overview
Professional folder organization for the Intelligent Loan Approval System with multi-agent AI orchestration.

```
LoanApprovalSystem/
│
├── src/                              # Source code directory
│   ├── __init__.py                  # Package initialization
│   ├── core/                        # Core business logic & orchestration
│   │   ├── __init__.py
│   │   ├── langgraph_orchestrator.py         # LangGraph workflow orchestration
│   │   └── advanced_risk_assessment.py       # Risk assessment algorithms
│   │
│   ├── agents/                      # AI Agent implementations
│   │   ├── __init__.py
│   │   ├── applicant_profile_agent.py        # Profile analysis agent
│   │   ├── financial_risk_agent.py           # Financial risk evaluation
│   │   ├── compliance_action_agent.py        # Compliance checking
│   │   ├── loan_decision_agent.py            # Final decision agent
│   │   └── integrated_loan_processor.py      # Integrated processor
│   │
│   ├── api/                         # REST API endpoints
│   │   ├── __init__.py
│   │   ├── api.py                           # Main API routes
│   │   └── orchestrator_api.py              # Orchestrator API
│   │
│   ├── ui/                          # User Interface
│   │   ├── __init__.py
│   │   ├── app.py                           # Main Streamlit app
│   │   ├── streamlit_chatbot_ui.py          # Chatbot UI
│   │   └── streamlit_integration.py         # UI integrations
│   │
│   ├── database/                    # Database management
│   │   ├── __init__.py
│   │   ├── mysql_setup.py                   # MySQL initialization
│   │   └── mysql_enhanced_setup.py          # Enhanced setup
│   │
│   ├── mcp/                         # Model Context Protocol
│   │   ├── __init__.py
│   │   ├── mcp_client.py                    # MCP client
│   │   ├── decision_synthesis_server.js     # Decision synthesis MCP server
│   │   ├── notification_system_server.js    # Notification MCP server
│   │   ├── risk_rules_server.js             # Risk rules MCP server
│   │   └── applicant_db_server.js           # Applicant DB MCP server
│   │
│   ├── config/                      # Configuration files
│   │   ├── __init__.py
│   │   ├── config.py                        # Configuration management
│   │   └── mcp_config.json                  # MCP configuration
│   │
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       └── generate_sample_data.py          # Sample data generation
│
├── docs/                            # Documentation
│   ├── README.md                            # Main README
│   ├── QUICK_START.md                       # Quick start guide
│   ├── API_DOCUMENTATION.md                 # API documentation
│   ├── README_API.md                        # API reference
│   ├── AGENTS_DOCUMENTATION.md              # Agent specifications
│   ├── MCP_SETUP_GUIDE.md                   # MCP setup guide
│   ├── MYSQL_SETUP_GUIDE.md                 # Database setup
│   ├── MYSQL_DATABASE_README.md             # Database documentation
│   ├── LANGGRAPH_WORKFLOW_GUIDE.md          # Workflow guide
│   ├── ADVANCED_RISK_ASSESSMENT_GUIDE.md    # Risk assessment guide
│   ├── QUICKSTART_MULTI_AGENT.md            # Multi-agent quickstart
│   ├── SAMPLE_DATA_README.md                # Sample data guide
│   ├── IMPLEMENTATION_SUMMARY.md            # Implementation details
│   ├── DELIVERY_CHECKLIST.md                # Delivery checklist
│   ├── MYSQL_DEPLOYMENT_SUMMARY.txt         # Deployment summary
│   └── PROJECT_SUMMARY.txt                  # Project summary
│
├── data/                            # Sample and test data
│   ├── Loan_Applicants_Sample_Data.json     # JSON sample data
│   ├── Loan_Applicants_Sample_Data.csv      # CSV sample data
│   └── Loan_Applicants_Sample_Data.xlsx     # Excel sample data
│
├── tests/                           # Test files
│   └── test_api.py                          # API tests
│
├── scripts/                         # Deployment and setup scripts
│   ├── deploy_mysql.sh                      # MySQL deployment script
│   └── run_api.sh                           # API run script
│
├── notebooks/                       # Jupyter notebooks (if any)
│   └── (reserved for analysis)
│
├── venv/                            # Virtual environment
│
├── .env                             # Environment variables
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── requirements.txt                 # Python dependencies
│
└── PROJECT_STRUCTURE.md             # This file

```

## Directory Descriptions

### `src/`
Main source code directory containing all application logic.

### `src/core/`
Core business logic including workflow orchestration and risk assessment algorithms.

### `src/agents/`
AI agent implementations for different aspects of loan processing (profiles, financial risk, compliance, decisions).

### `src/api/`
REST API endpoints and request handlers.

### `src/ui/`
Streamlit-based user interface components and applications.

### `src/database/`
Database initialization, migration, and management scripts.

### `src/mcp/`
Model Context Protocol servers for integrating with AI models and external systems.

### `src/config/`
Configuration files and settings management.

### `src/utils/`
Utility functions and helpers for data generation, logging, etc.

### `docs/`
Comprehensive documentation including setup guides, API docs, and implementation details.

### `data/`
Sample data in multiple formats (JSON, CSV, Excel) for testing and development.

### `tests/`
Automated tests for API endpoints and business logic.

### `scripts/`
Deployment scripts and automation tools.

### `notebooks/`
Jupyter notebooks for analysis and exploration (reserved for future use).

## Key Files at Root

- `.env` - Environment variables (secret, not in git)
- `.env.example` - Template for environment variables
- `.gitignore` - Git exclusion rules
- `requirements.txt` - Python package dependencies
- `PROJECT_STRUCTURE.md` - This architecture document

## Getting Started

1. **Setup**: Read `docs/QUICK_START.md`
2. **Database**: Follow `docs/MYSQL_SETUP_GUIDE.md`
3. **API**: See `docs/API_DOCUMENTATION.md`
4. **Agents**: Review `docs/AGENTS_DOCUMENTATION.md`
5. **Workflows**: Check `docs/LANGGRAPH_WORKFLOW_GUIDE.md`

## Development Best Practices

- Keep related functionality in the same module
- Use `__init__.py` files to expose public APIs
- Follow PEP 8 for Python code
- Document all public functions and classes
- Write tests for business logic
- Use environment variables for configuration
- Keep database migrations in `src/database/`
- Add new utilities to `src/utils/`

## Import Examples

```python
# Importing from the organized structure
from src.core import langgraph_orchestrator
from src.agents import financial_risk_agent
from src.api import api
from src.database import mysql_setup
from src.config import config
from src.utils import generate_sample_data
```

---
*Last updated: 2026-07-03*
