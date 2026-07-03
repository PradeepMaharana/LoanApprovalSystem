# Developer Guide - LoanApprovalSystem

## Project Organization

This project follows professional software engineering practices with a clean, modular architecture.

## Directory Organization

### Source Code (`src/`)

The `src/` directory contains all application code organized by functional domains:

- **core/** - Orchestration and business logic
- **agents/** - AI agent implementations
- **api/** - REST API endpoints
- **ui/** - Streamlit frontend
- **database/** - Database management
- **mcp/** - Model Context Protocol integrations
- **config/** - Configuration management
- **utils/** - Reusable utilities

### Documentation (`docs/`)

All documentation is centralized with clear purposes:

- Setup guides (MySQL, MCP, Quick Start)
- API and agent documentation
- Implementation guides and checklists
- Sample data descriptions

### Data (`data/`)

Sample data in multiple formats for development and testing:

- JSON format (structured data)
- CSV format (tabular data)
- Excel format (spreadsheet format)

### Tests (`tests/`)

Automated test suites:

- `test_api.py` - API endpoint tests
- Add more test files following naming convention: `test_*.py`

### Scripts (`scripts/`)

Automation and deployment:

- `deploy_mysql.sh` - Database deployment
- `run_api.sh` - API server startup
- Add deployment and utility scripts here

## Python Module Imports

When importing from the organized structure:

```python
# Top-level imports from packages
from src.core import langgraph_orchestrator
from src.agents import financial_risk_agent
from src.api import api
from src.ui import app
from src.database import mysql_setup
from src.mcp import mcp_client
from src.config import config
from src.utils import generate_sample_data

# Or specific imports
from src.core.langgraph_orchestrator import LangGraphOrchestrator
from src.agents.financial_risk_agent import FinancialRiskAgent
from src.api.api import app as flask_app
```

## Running the Application

### 1. Setup Environment

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database

```bash
python src/database/mysql_enhanced_setup.py
```

### 4. Run API Server

```bash
bash scripts/run_api.sh
# or
python -m src.api.api
```

### 5. Run UI

```bash
streamlit run src/ui/app.py
```

## Development Workflow

### Adding New Code

1. **For new business logic**: Add to `src/core/`
2. **For new agents**: Add to `src/agents/`
3. **For API endpoints**: Add to `src/api/`
4. **For UI components**: Add to `src/ui/`
5. **For utilities**: Add to `src/utils/`

### Adding Tests

1. Create `tests/test_*.py` file
2. Import from appropriate module: `from src.core import module`
3. Write test cases following pytest conventions

```python
def test_agent_processing():
    from src.agents import financial_risk_agent
    # Test implementation
```

### Managing Dependencies

- Update `requirements.txt` when adding packages
- Activate virtual environment before installing: `source venv/bin/activate`

### Configuration

1. Environment-specific settings go in `.env`
2. Application defaults in `src/config/config.py`
3. Module-specific configs in respective directories

## Project Components

### Multi-Agent System

- **Applicant Profile Agent**: Analyzes applicant background
- **Financial Risk Agent**: Evaluates financial metrics
- **Compliance Action Agent**: Checks regulatory compliance
- **Loan Decision Agent**: Makes final decision
- **Integrated Processor**: Orchestrates all agents

### Workflow Engine

- **LangGraph Orchestrator**: Manages agent workflows and state
- **Risk Assessment**: Advanced risk scoring algorithms

### APIs

- **REST API** (`src/api/api.py`): Main application endpoints
- **Orchestrator API** (`src/api/orchestrator_api.py`): Workflow control

### User Interfaces

- **Streamlit App** (`src/ui/app.py`): Main web application
- **Chatbot UI** (`src/ui/streamlit_chatbot_ui.py`): Interactive chatbot
- **Integration** (`src/ui/streamlit_integration.py`): UI helpers

### Database

- **MySQL Setup**: Initialization and schema creation
- **Enhanced Setup**: Advanced configuration and migrations

### Model Context Protocol

- **MCP Client**: Communication with MCP servers
- **Decision Synthesis Server**: Decision consolidation
- **Notification System**: Alert management
- **Risk Rules Server**: Business rule engine
- **Applicant DB Server**: Data access layer

## Common Tasks

### Debug an Agent

```python
from src.agents.financial_risk_agent import FinancialRiskAgent
from src.config import config

agent = FinancialRiskAgent()
result = agent.process(applicant_data)
print(result)
```

### Test an API Endpoint

```python
import requests

response = requests.post('http://localhost:5000/api/process', json={...})
print(response.json())
```

### Generate Sample Data

```python
from src.utils.generate_sample_data import generate_sample_data

generate_sample_data()
```

### Run Database Setup

```python
from src.database.mysql_enhanced_setup import setup_database

setup_database()
```

## Documentation Reference

- **Setup**: See `docs/QUICK_START.md`
- **API**: See `docs/API_DOCUMENTATION.md`
- **Agents**: See `docs/AGENTS_DOCUMENTATION.md`
- **Database**: See `docs/MYSQL_DATABASE_README.md`
- **Workflows**: See `docs/LANGGRAPH_WORKFLOW_GUIDE.md`

## Project Conventions

### File Naming

- Python modules: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Code Organization

- One main class per file
- Related utilities in module files
- Imports organized: stdlib → third-party → local
- Maximum line length: 100 characters (recommended)

### Documentation

- Docstrings for all public classes and functions
- README files in each major directory
- Inline comments for complex logic only

## Troubleshooting

### Import Errors

Make sure you're importing from the correct path:
```python
# ✓ Correct
from src.agents import financial_risk_agent

# ✗ Wrong
from agents import financial_risk_agent
```

### Module Not Found

1. Ensure `src/__init__.py` exists (it does)
2. Check virtual environment is activated
3. Verify `requirements.txt` is installed
4. Run from project root directory

### Database Connection Issues

- Check `.env` has correct database credentials
- Verify MySQL is running
- Run `src/database/mysql_enhanced_setup.py` to initialize

---
*This guide is maintained as part of the project structure. Update as needed.*
