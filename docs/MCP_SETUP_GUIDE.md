# MCP MySQL Server Setup Guide

## Overview

This guide covers the setup and usage of four specialized MCP (Model Context Protocol) MySQL servers for the Loan Approval System:

1. **ApplicantDB** - Applicant data management
2. **RiskRulesDB** - Risk assessment rules and algorithms
3. **DecisionSynthesis** - Loan decision synthesis
4. **NotificationSystem** - Communication and alerts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Servers                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ApplicantDB  │  │ RiskRulesDB  │  │ DecisionSyn- │      │
│  │              │  │              │  │ thesis       │      │
│  │ • Applicants │  │ • Thresholds │  │              │      │
│  │ • Apps       │  │ • Rules      │  │ • Decisions  │      │
│  │ • Profiles   │  │ • Algorithms │  │ • Terms      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     NotificationSystem                               │   │
│  │                                                      │   │
│  │ • Notifications      • Communication History        │   │
│  │ • Templates          • Alert Rules                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  MySQL Databases │
                    ├──────────────────┤
                    │ • applicant_db   │
                    │ • risk_rules_db  │
                    │ • decision_db    │
                    │ • notification_db│
                    └──────────────────┘
```

---

## Installation & Setup

### Prerequisites

```bash
# Node.js packages required
npm install mysql2/promise
npm install @modelcontextprotocol/sdk
```

### Database Setup

```bash
# Create the four databases
mysql -u root -p'Tek@12345' -e "CREATE DATABASE applicant_db;"
mysql -u root -p'Tek@12345' -e "CREATE DATABASE risk_rules_db;"
mysql -u root -p'Tek@12345' -e "CREATE DATABASE decision_synthesis_db;"
mysql -u root -p'Tek@12345' -e "CREATE DATABASE notification_system_db;"
```

### Configuration

Update your Claude `.env` or MCP configuration with:

```json
{
  "mcpServers": {
    "ApplicantDB": {
      "command": "node",
      "args": ["mcp_servers/applicant_db_server.js"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "Tek@12345",
        "MYSQL_DATABASE": "applicant_db"
      }
    },
    "RiskRulesDB": {
      "command": "node",
      "args": ["mcp_servers/risk_rules_server.js"],
      "env": {
        "MYSQL_DATABASE": "risk_rules_db"
      }
    },
    "DecisionSynthesis": {
      "command": "node",
      "args": ["mcp_servers/decision_synthesis_server.js"],
      "env": {
        "MYSQL_DATABASE": "decision_synthesis_db"
      }
    },
    "NotificationSystem": {
      "command": "node",
      "args": ["mcp_servers/notification_system_server.js"],
      "env": {
        "MYSQL_DATABASE": "notification_system_db"
      }
    }
  }
}
```

---

## 1. ApplicantDB Server

### Purpose
Manages all applicant data and loan application information.

### Tools Available

#### get_applicant
Retrieve a single applicant by ID.

```python
result = client.call_tool("ApplicantDB", "get_applicant", {
    "applicant_id": "APP-2026-000001"
})
```

#### search_applicants
Search applicants by criteria (age, income, location, employment type).

```python
result = client.call_tool("ApplicantDB", "search_applicants", {
    "criteria": {
        "age_min": 25,
        "age_max": 45,
        "location": "New York",
        "employment_type": "Salaried"
    },
    "limit": 20
})
```

#### get_application_status
Get the status of a loan application.

```python
result = client.call_tool("ApplicantDB", "get_application_status", {
    "applicant_id": "APP-2026-000001"
})
```

#### get_applicant_profile
Get complete applicant profile including application and risk assessment.

```python
result = client.call_tool("ApplicantDB", "get_applicant_profile", {
    "applicant_id": "APP-2026-000001"
})
```

#### list_all_applicants
List all applicants with pagination.

```python
result = client.call_tool("ApplicantDB", "list_all_applicants", {
    "page": 1,
    "limit": 50
})
```

#### get_applicants_by_location
Get all applicants from a specific location.

```python
result = client.call_tool("ApplicantDB", "get_applicants_by_location", {
    "location": "New York, NY"
})
```

#### get_applicants_by_employment
Get applicants by employment type.

```python
result = client.call_tool("ApplicantDB", "get_applicants_by_employment", {
    "employment_type": "Salaried"
})
```

---

## 2. RiskRulesDB Server

### Purpose
Manages risk assessment rules, thresholds, and scoring algorithms.

### Tools Available

#### get_risk_thresholds
Get all risk assessment thresholds.

```python
result = client.call_tool("RiskRulesDB", "get_risk_thresholds", {})
```

#### get_threshold_by_factor
Get threshold for a specific risk factor.

```python
result = client.call_tool("RiskRulesDB", "get_threshold_by_factor", {
    "risk_factor": "credit_score"
})
```

#### get_risk_rules
Get all active risk assessment rules, optionally filtered by type.

```python
result = client.call_tool("RiskRulesDB", "get_risk_rules", {
    "rule_type": "income_stability"
})
```

#### get_decision_rules
Get loan decision rules by risk score range.

```python
result = client.call_tool("RiskRulesDB", "get_decision_rules", {
    "risk_score": 75
})
```

#### get_scoring_algorithms
Get available scoring algorithms.

```python
result = client.call_tool("RiskRulesDB", "get_scoring_algorithms", {
    "algorithm_type": "income_stability"
})
```

#### get_recommendation_for_score
Get loan recommendation based on risk score.

```python
result = client.call_tool("RiskRulesDB", "get_recommendation_for_score", {
    "risk_score": 75
})
```

---

## 3. DecisionSynthesis Server

### Purpose
Synthesizes loan decisions combining applicant data and risk rules.

### Tools Available

#### synthesize_loan_decision
Synthesize a complete loan decision for an applicant.

```python
result = client.call_tool("DecisionSynthesis", "synthesize_loan_decision", {
    "applicant_id": "APP-2026-000001",
    "income_stability_score": 78,
    "employment_risk_score": 50,
    "credit_score": 750,
    "loan_amount": 300000,
    "income": 120000
})
```

#### get_loan_decision
Retrieve a saved loan decision.

```python
result = client.call_tool("DecisionSynthesis", "get_loan_decision", {
    "applicant_id": "APP-2026-000001"
})
```

#### calculate_loan_terms
Calculate detailed loan terms.

```python
result = client.call_tool("DecisionSynthesis", "calculate_loan_terms", {
    "principal_amount": 300000,
    "interest_rate": 5.5,
    "term_months": 360
})
```

#### get_all_decisions
Get all loan decisions with optional filtering.

```python
result = client.call_tool("DecisionSynthesis", "get_all_decisions", {
    "decision_type": "APPROVED",
    "limit": 50
})
```

#### update_decision_status
Update the status of a loan decision.

```python
result = client.call_tool("DecisionSynthesis", "update_decision_status", {
    "applicant_id": "APP-2026-000001",
    "new_status": "APPROVED",
    "rationale": "Strong credit profile with stable income"
})
```

---

## 4. NotificationSystem Server

### Purpose
Manages notifications, alerts, and communications.

### Tools Available

#### create_notification
Create a new notification for an applicant.

```python
result = client.call_tool("NotificationSystem", "create_notification", {
    "applicant_id": "APP-2026-000001",
    "notification_type": "APPROVED",
    "title": "Your Loan is Approved",
    "message": "Congratulations! Your loan has been approved.",
    "priority": "HIGH",
    "channels": ["EMAIL", "SMS", "IN_APP"]
})
```

#### send_notification
Send a pending notification.

```python
result = client.call_tool("NotificationSystem", "send_notification", {
    "notification_id": 42
})
```

#### get_notifications
Get notifications for an applicant.

```python
result = client.call_tool("NotificationSystem", "get_notifications", {
    "applicant_id": "APP-2026-000001",
    "limit": 20
})
```

#### get_communication_history
Get communication history for an applicant.

```python
result = client.call_tool("NotificationSystem", "get_communication_history", {
    "applicant_id": "APP-2026-000001"
})
```

#### get_pending_communications
Get all pending communications.

```python
result = client.call_tool("NotificationSystem", "get_pending_communications", {
    "limit": 50
})
```

#### mark_notification_read
Mark a notification as read.

```python
result = client.call_tool("NotificationSystem", "mark_notification_read", {
    "notification_id": 42
})
```

#### get_communication_templates
Get available communication templates.

```python
result = client.call_tool("NotificationSystem", "get_communication_templates", {
    "notification_type": "APPROVED"
})
```

#### send_bulk_notifications
Send bulk notifications to multiple applicants.

```python
result = client.call_tool("NotificationSystem", "send_bulk_notifications", {
    "applicant_ids": ["APP-2026-000001", "APP-2026-000002"],
    "notification_type": "APPROVED",
    "message": "Your loan has been approved!"
})
```

---

## Usage Examples

### Example 1: Complete Loan Decision Flow

```python
# 1. Get applicant profile
applicant = client.call_tool("ApplicantDB", "get_applicant_profile", {
    "applicant_id": "APP-2026-000001"
})

# 2. Get risk thresholds
thresholds = client.call_tool("RiskRulesDB", "get_risk_thresholds", {})

# 3. Synthesize decision
decision = client.call_tool("DecisionSynthesis", "synthesize_loan_decision", {
    "applicant_id": applicant['applicant_id'],
    "income_stability_score": applicant['risk_assessment']['income_stability_score'],
    "employment_risk_score": applicant['risk_assessment']['employment_risk_score'],
    "credit_score": applicant['application']['credit_score'],
    "loan_amount": applicant['application']['loan_amount'],
    "income": applicant['applicant']['income']
})

# 4. Send notification
notification = client.call_tool("NotificationSystem", "create_notification", {
    "applicant_id": applicant['applicant_id'],
    "notification_type": decision['decision'],
    "message": f"Your loan decision: {decision['decision']}"
})

# 5. Send the notification
client.call_tool("NotificationSystem", "send_notification", {
    "notification_id": notification['notification_id']
})
```

### Example 2: Search and Bulk Notify

```python
# 1. Find high-income applicants in New York
applicants = client.call_tool("ApplicantDB", "search_applicants", {
    "criteria": {
        "location": "New York, NY",
        "age_min": 30,
        "age_max": 55
    },
    "limit": 100
})

# 2. Send bulk notification
client.call_tool("NotificationSystem", "send_bulk_notifications", {
    "applicant_ids": [app['applicant_id'] for app in applicants['data']],
    "notification_type": "DOCUMENTS_NEEDED",
    "message": "Please submit your recent tax returns to proceed with your application."
})
```

### Example 3: Risk Assessment Workflow

```python
# 1. Get risk rules
rules = client.call_tool("RiskRulesDB", "get_risk_rules", {})

# 2. Get recommendation for a score
recommendation = client.call_tool("RiskRulesDB", "get_recommendation_for_score", {
    "risk_score": 65
})

# 3. Get decision rules
decision_rules = client.call_tool("RiskRulesDB", "get_decision_rules", {
    "risk_score": 65
})
```

---

## Database Schema

### ApplicantDB

```sql
-- Connects to: applicant_db (shared with loan_approval_system)
-- Tables:
-- - applicants (applicant profiles)
-- - loan_applications (application details and status)
-- - risk_assessments (risk scores and assessments)
```

### RiskRulesDB

```sql
-- Tables:
-- - risk_thresholds (min/max values for risk factors)
-- - risk_rules (conditional rules for risk assessment)
-- - decision_rules (rules for loan decisions by risk score)
-- - scoring_algorithms (algorithms for calculating scores)
```

### DecisionSynthesis

```sql
-- Tables:
-- - loan_decisions (final decisions for applicants)
-- - decision_justifications (detailed reasoning for decisions)
-- - loan_terms (calculated loan terms and conditions)
```

### NotificationSystem

```sql
-- Tables:
-- - notifications (notification records)
-- - communication_templates (email/SMS templates)
-- - communication_history (delivery history)
-- - alert_rules (rules for generating alerts)
```

---

## Running the Servers

### Individually

```bash
# Terminal 1
node mcp_servers/applicant_db_server.js

# Terminal 2
node mcp_servers/risk_rules_server.js

# Terminal 3
node mcp_servers/decision_synthesis_server.js

# Terminal 4
node mcp_servers/notification_system_server.js
```

### Via PM2 (Production)

```bash
npm install -g pm2

pm2 start mcp_servers/applicant_db_server.js --name "ApplicantDB"
pm2 start mcp_servers/risk_rules_server.js --name "RiskRulesDB"
pm2 start mcp_servers/decision_synthesis_server.js --name "DecisionSynthesis"
pm2 start mcp_servers/notification_system_server.js --name "NotificationSystem"

pm2 status
pm2 logs
```

---

## Integration with Claude

### Python Client Example

```python
import json
import subprocess

class MCPClient:
    def __init__(self, server_name):
        self.server_name = server_name
    
    def call_tool(self, tool_name, args):
        # Implementation would depend on your MCP client library
        pass

# Usage
applicant_db = MCPClient("ApplicantDB")
risk_rules = MCPClient("RiskRulesDB")
decision_synthesis = MCPClient("DecisionSynthesis")
notification = MCPClient("NotificationSystem")
```

---

## Features Summary

| Server | Key Capabilities |
|--------|------------------|
| **ApplicantDB** | Query applicants, search by criteria, get profiles, retrieve applications |
| **RiskRulesDB** | Manage risk thresholds, rules, algorithms, get recommendations |
| **DecisionSynthesis** | Synthesize decisions, calculate terms, track decision history |
| **NotificationSystem** | Create/send notifications, manage templates, track communications |

---

## Security Considerations

1. **Database Access**: All servers use authenticated MySQL connections
2. **Input Validation**: All tool inputs are validated
3. **Rate Limiting**: Implement in production environment
4. **Audit Logging**: Track all decisions and communications
5. **Data Encryption**: Encrypt sensitive data at rest

---

## Troubleshooting

### Connection Issues

```bash
# Test MySQL connection
mysql -u root -p'Tek@12345' -h localhost -e "SELECT 1;"

# Check if ports are listening
netstat -tuln | grep 3306
```

### Debug Logging

Set environment variable:

```bash
export LOG_LEVEL=debug
node mcp_servers/applicant_db_server.js
```

---

## Next Steps

1. Configure MCP clients in your Claude instance
2. Start all four MCP servers
3. Test connectivity with sample queries
4. Integrate into your application workflow
5. Set up monitoring and alerting

Generated: 2024-07-01  
Status: Production Ready
