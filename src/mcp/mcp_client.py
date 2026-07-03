#!/usr/bin/env python3

"""
MCP Client for LangGraph Orchestrator
Handles communication with MCP servers for agent invocation
"""

import json
import asyncio
from typing import Dict, Any, Optional
import httpx

class MCPClient:
    """Client for communicating with MCP servers"""

    def __init__(self, servers_config: Dict[str, Dict[str, Any]]):
        """
        Initialize MCP client with server configurations

        Args:
            servers_config: Dictionary with server configs
        """
        self.servers_config = servers_config
        self.clients = {}

    async def initialize(self):
        """Initialize HTTP clients for all servers"""
        for server_name, config in self.servers_config.items():
            try:
                self.clients[server_name] = httpx.AsyncClient(
                    base_url=config.get('base_url', f"http://localhost:{config.get('port')}")
                )
                print(f"✅ MCP Client initialized for {server_name}")
            except Exception as e:
                print(f"⚠️  Failed to initialize {server_name}: {e}")

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on a specific MCP server

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool response
        """
        try:
            if server_name not in self.clients:
                return {"error": f"Server {server_name} not initialized"}

            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }

            response = await self.clients[server_name].post(
                "/rpc",
                json=payload,
                timeout=30.0
            )

            return response.json()
        except Exception as e:
            return {"error": f"MCP call failed: {str(e)}"}

    async def get_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """Get applicant profile from ApplicantDB"""
        return await self.call_tool("ApplicantDB", "get_applicant_profile", {
            "applicant_id": applicant_id
        })

    async def search_applicants(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Search applicants in ApplicantDB"""
        return await self.call_tool("ApplicantDB", "search_applicants", {
            "criteria": criteria
        })

    async def get_risk_thresholds(self) -> Dict[str, Any]:
        """Get risk thresholds from RiskRulesDB"""
        return await self.call_tool("RiskRulesDB", "get_risk_thresholds", {})

    async def get_risk_rules(self, rule_type: Optional[str] = None) -> Dict[str, Any]:
        """Get risk rules from RiskRulesDB"""
        args = {}
        if rule_type:
            args["rule_type"] = rule_type
        return await self.call_tool("RiskRulesDB", "get_risk_rules", args)

    async def get_recommendation_for_score(self, risk_score: float) -> Dict[str, Any]:
        """Get recommendation from RiskRulesDB"""
        return await self.call_tool("RiskRulesDB", "get_recommendation_for_score", {
            "risk_score": risk_score
        })

    async def synthesize_loan_decision(self, applicant_id: str, income_stability_score: float,
                                      employment_risk_score: float, credit_score: int,
                                      loan_amount: float, income: float) -> Dict[str, Any]:
        """Synthesize loan decision from DecisionSynthesis"""
        return await self.call_tool("DecisionSynthesis", "synthesize_loan_decision", {
            "applicant_id": applicant_id,
            "income_stability_score": income_stability_score,
            "employment_risk_score": employment_risk_score,
            "credit_score": credit_score,
            "loan_amount": loan_amount,
            "income": income
        })

    async def calculate_loan_terms(self, principal_amount: float, interest_rate: float,
                                   term_months: int) -> Dict[str, Any]:
        """Calculate loan terms from DecisionSynthesis"""
        return await self.call_tool("DecisionSynthesis", "calculate_loan_terms", {
            "principal_amount": principal_amount,
            "interest_rate": interest_rate,
            "term_months": term_months
        })

    async def create_notification(self, applicant_id: str, notification_type: str,
                                 message: str, priority: str = "MEDIUM",
                                 channels: list = None) -> Dict[str, Any]:
        """Create notification in NotificationSystem"""
        if channels is None:
            channels = ["EMAIL", "IN_APP"]

        return await self.call_tool("NotificationSystem", "create_notification", {
            "applicant_id": applicant_id,
            "notification_type": notification_type,
            "message": message,
            "priority": priority,
            "channels": channels
        })

    async def send_notification(self, notification_id: int) -> Dict[str, Any]:
        """Send notification from NotificationSystem"""
        return await self.call_tool("NotificationSystem", "send_notification", {
            "notification_id": notification_id
        })

    async def send_bulk_notifications(self, applicant_ids: list, notification_type: str,
                                     message: str) -> Dict[str, Any]:
        """Send bulk notifications from NotificationSystem"""
        return await self.call_tool("NotificationSystem", "send_bulk_notifications", {
            "applicant_ids": applicant_ids,
            "notification_type": notification_type,
            "message": message
        })

    async def close(self):
        """Close all client connections"""
        for client in self.clients.values():
            await client.aclose()


class LocalMCPClient:
    """Local MCP Client for direct agent invocation (for development/testing)"""

    def __init__(self):
        """Initialize local agents"""
        from agents.applicant_profile_agent import ApplicantProfileAgent
        from agents.financial_risk_agent import FinancialRiskAgent
        from agents.loan_decision_agent import LoanDecisionAgent
        from agents.compliance_action_agent import ComplianceActionOrchestrator

        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Tek@12345',
            'database': 'loan_approval_system'
        }

        self.applicant_agent = ApplicantProfileAgent(self.db_config)
        self.risk_agent = FinancialRiskAgent(self.db_config)
        self.decision_agent = LoanDecisionAgent(self.db_config)
        self.compliance_agent = ComplianceActionOrchestrator(self.db_config)

    def initialize(self) -> bool:
        """Initialize all agents"""
        if not self.applicant_agent.connect_database():
            return False
        if not self.risk_agent.connect_database():
            return False
        if not self.decision_agent.connect_database():
            return False
        if not self.compliance_agent.connect_database():
            return False
        return True

    def get_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """Get applicant profile"""
        return self.applicant_agent.analyze_applicant_profile(applicant_id)

    def get_financial_risk(self, applicant_id: str) -> Dict[str, Any]:
        """Get financial risk analysis"""
        return self.risk_agent.analyze_financial_risk(applicant_id)

    def get_loan_decision(self, applicant_id: str) -> Dict[str, Any]:
        """Get loan decision"""
        return self.decision_agent.synthesize_loan_decision(applicant_id)

    def orchestrate_compliance(self, applicant_id: str, decision_data: Dict) -> Dict[str, Any]:
        """Orchestrate compliance actions"""
        return self.compliance_agent.orchestrate_action(applicant_id, decision_data)

    def close(self):
        """Close all agent connections"""
        self.applicant_agent.disconnect_database()
        self.risk_agent.disconnect_database()
        self.decision_agent.disconnect_database()
        self.compliance_agent.disconnect_database()
