#!/usr/bin/env python3

"""
LangGraph-based AI Orchestration Engine
Orchestrates multi-agent loan processing workflow using LangGraph and LangChain
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from mcp_client import LocalMCPClient

# Initialize Claude Sonnet 4.6
llm = ChatAnthropic(model="claude-sonnet-4-6")

# ============================================================================
# State Management
# ============================================================================

class DecisionState(Enum):
    """Loan decision states"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVIEW = "REVIEW"


class LoanApplicationState(BaseModel):
    """State for loan application processing"""
    applicant_id: str
    application_data: Dict[str, Any] = Field(default_factory=dict)
    applicant_profile: Dict[str, Any] = Field(default_factory=dict)
    financial_risk: Dict[str, Any] = Field(default_factory=dict)
    loan_decision: Dict[str, Any] = Field(default_factory=dict)
    compliance_actions: Dict[str, Any] = Field(default_factory=dict)
    final_recommendation: Dict[str, Any] = Field(default_factory=dict)
    errors: list = Field(default_factory=list)
    processing_stages: list = Field(default_factory=list)


# ============================================================================
# Agent Nodes
# ============================================================================

class LoanOrchestrator:
    """Multi-agent orchestrator using LangGraph"""

    def __init__(self, use_local_agents: bool = True):
        """
        Initialize orchestrator

        Args:
            use_local_agents: Use local agents instead of MCP servers
        """
        self.mcp_client = LocalMCPClient()
        self.use_local_agents = use_local_agents
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("fetch_application_data", self.node_fetch_application)
        workflow.add_node("applicant_profile_analysis", self.node_applicant_profile)
        workflow.add_node("financial_risk_analysis", self.node_financial_risk)
        workflow.add_node("loan_decision_synthesis", self.node_loan_decision)
        workflow.add_node("compliance_orchestration", self.node_compliance_actions)
        workflow.add_node("llm_synthesis", self.node_llm_synthesis)
        workflow.add_node("final_recommendation", self.node_final_recommendation)

        # Add edges
        workflow.add_edge("fetch_application_data", "applicant_profile_analysis")
        workflow.add_edge("applicant_profile_analysis", "financial_risk_analysis")
        workflow.add_edge("financial_risk_analysis", "loan_decision_synthesis")
        workflow.add_edge("loan_decision_synthesis", "compliance_orchestration")
        workflow.add_edge("compliance_orchestration", "llm_synthesis")
        workflow.add_edge("llm_synthesis", "final_recommendation")
        workflow.add_edge("final_recommendation", END)

        workflow.set_entry_point("fetch_application_data")

        return workflow.compile()

    def node_fetch_application(self, state: dict) -> dict:
        """Fetch application data from database"""
        applicant_id = state.get("applicant_id")

        state["processing_stages"].append({
            "stage": "Fetch Application Data",
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS"
        })

        try:
            # In real scenario, fetch from database
            state["application_data"] = {
                "applicant_id": applicant_id,
                "status": "PENDING",
                "created_at": datetime.now().isoformat()
            }

            state["processing_stages"][-1]["status"] = "COMPLETED"
            return state
        except Exception as e:
            state["errors"].append(f"Failed to fetch application: {str(e)}")
            state["processing_stages"][-1]["status"] = "FAILED"
            return state

    def node_applicant_profile(self, state: dict) -> dict:
        """Invoke Applicant Profile Agent"""
        applicant_id = state.get("applicant_id")

        state["processing_stages"].append({
            "stage": "Applicant Profile Analysis",
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS"
        })

        try:
            profile = self.mcp_client.get_applicant_profile(applicant_id)

            if "error" not in profile:
                state["applicant_profile"] = profile
                state["processing_stages"][-1]["status"] = "COMPLETED"
            else:
                state["errors"].append(f"Profile analysis error: {profile['error']}")
                state["processing_stages"][-1]["status"] = "FAILED"

            return state
        except Exception as e:
            state["errors"].append(f"Applicant profile agent failed: {str(e)}")
            state["processing_stages"][-1]["status"] = "FAILED"
            return state

    def node_financial_risk(self, state: dict) -> dict:
        """Invoke Financial Risk Analysis Agent"""
        applicant_id = state.get("applicant_id")

        state["processing_stages"].append({
            "stage": "Financial Risk Analysis",
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS"
        })

        try:
            risk_analysis = self.mcp_client.get_financial_risk(applicant_id)

            if "error" not in risk_analysis:
                state["financial_risk"] = risk_analysis
                state["processing_stages"][-1]["status"] = "COMPLETED"
            else:
                state["errors"].append(f"Risk analysis error: {risk_analysis['error']}")
                state["processing_stages"][-1]["status"] = "FAILED"

            return state
        except Exception as e:
            state["errors"].append(f"Financial risk agent failed: {str(e)}")
            state["processing_stages"][-1]["status"] = "FAILED"
            return state

    def node_loan_decision(self, state: dict) -> dict:
        """Invoke Loan Decision Agent"""
        applicant_id = state.get("applicant_id")

        state["processing_stages"].append({
            "stage": "Loan Decision Synthesis",
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS"
        })

        try:
            decision = self.mcp_client.get_loan_decision(applicant_id)

            if "error" not in decision:
                state["loan_decision"] = decision
                state["processing_stages"][-1]["status"] = "COMPLETED"
            else:
                state["errors"].append(f"Decision synthesis error: {decision['error']}")
                state["processing_stages"][-1]["status"] = "FAILED"

            return state
        except Exception as e:
            state["errors"].append(f"Loan decision agent failed: {str(e)}")
            state["processing_stages"][-1]["status"] = "FAILED"
            return state

    def node_compliance_actions(self, state: dict) -> dict:
        """Invoke Compliance & Action Orchestrator Agent"""
        applicant_id = state.get("applicant_id")
        decision_data = state.get("loan_decision", {})

        state["processing_stages"].append({
            "stage": "Compliance & Action Orchestration",
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS"
        })

        try:
            compliance = self.mcp_client.orchestrate_compliance(applicant_id, decision_data)

            if "error" not in compliance:
                state["compliance_actions"] = compliance
                state["processing_stages"][-1]["status"] = "COMPLETED"
            else:
                state["errors"].append(f"Compliance orchestration error: {compliance['error']}")
                state["processing_stages"][-1]["status"] = "FAILED"

            return state
        except Exception as e:
            state["errors"].append(f"Compliance agent failed: {str(e)}")
            state["processing_stages"][-1]["status"] = "FAILED"
            return state

    def node_llm_synthesis(self, state: dict) -> dict:
        """Invoke LLM (Claude Sonnet) for synthesis and reasoning"""
        state["processing_stages"].append({
            "stage": "LLM Synthesis & Reasoning",
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS"
        })

        try:
            # Prepare context for Claude
            profile_summary = self._summarize_profile(state.get("applicant_profile", {}))
            risk_summary = self._summarize_risk(state.get("financial_risk", {}))
            decision_summary = self._summarize_decision(state.get("loan_decision", {}))

            # Build prompt for Claude
            system_prompt = """You are a senior loan officer synthesizing comprehensive loan application analysis.

Your role is to:
1. Review the applicant profile, financial risk analysis, and loan decision
2. Provide deep reasoning about the decision
3. Identify key risk factors and strengths
4. Generate a personalized recommendation letter
5. Suggest next steps and conditions

Be professional, thorough, and fair in your assessment."""

            user_prompt = f"""
Please synthesize the following loan application analysis:

APPLICANT PROFILE:
{profile_summary}

FINANCIAL RISK ANALYSIS:
{risk_summary}

LOAN DECISION:
{decision_summary}

Based on this analysis, please provide:
1. Executive Summary (2-3 sentences)
2. Key Strengths (3-5 bullet points)
3. Key Concerns (if any)
4. Risk Assessment Reasoning
5. Recommended Conditions or Next Steps
6. Personalized Recommendation Letter (formal tone)

Respond in JSON format with keys: executive_summary, key_strengths, key_concerns, risk_reasoning, conditions, recommendation_letter
"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = llm.invoke(messages)

            # Parse Claude's response
            try:
                llm_output = json.loads(response.content)
                state["final_recommendation"] = llm_output
            except json.JSONDecodeError:
                state["final_recommendation"] = {
                    "executive_summary": response.content,
                    "raw_response": response.content
                }

            state["processing_stages"][-1]["status"] = "COMPLETED"
            return state

        except Exception as e:
            state["errors"].append(f"LLM synthesis failed: {str(e)}")
            state["processing_stages"][-1]["status"] = "FAILED"
            return state

    def node_final_recommendation(self, state: dict) -> dict:
        """Generate final recommendation"""
        state["processing_stages"].append({
            "stage": "Final Recommendation",
            "timestamp": datetime.now().isoformat(),
            "status": "COMPLETED"
        })

        return state

    def _summarize_profile(self, profile: dict) -> str:
        """Summarize applicant profile"""
        if not profile:
            return "No profile data available"

        summary = f"""
Name: {profile.get('applicant_info', {}).get('name', 'N/A')}
Age: {profile.get('applicant_info', {}).get('age', 'N/A')}
Location: {profile.get('applicant_info', {}).get('location', 'N/A')}
Employment: {profile.get('applicant_info', {}).get('employment_type', 'N/A')}
Annual Income: ${profile.get('applicant_info', {}).get('annual_income', 0):,.0f}

Income Stability Score: {profile.get('income_stability_score', {}).get('score', 'N/A')}/100
Employment Risk: {profile.get('employment_risk', {}).get('risk_level', 'N/A')}
Credit Category: {profile.get('credit_history_summary', {}).get('category', 'N/A')}
Application Completeness: {profile.get('application_completeness', {}).get('completion_percentage', 0)}%
"""
        return summary

    def _summarize_risk(self, risk: dict) -> str:
        """Summarize financial risk"""
        if not risk:
            return "No risk analysis data available"

        summary = f"""
Annual Income: ${risk.get('financial_overview', {}).get('annual_income', 0):,.0f}
Total Liabilities: ${risk.get('financial_overview', {}).get('total_liabilities', 0):,.0f}
Loan Amount Requested: ${risk.get('financial_overview', {}).get('requested_loan_amount', 0):,.0f}

DTI Ratio: {risk.get('debt_to_income_analysis', {}).get('current_dti_ratio', 0):.1%}
Credit Score: {risk.get('credit_score_risk_level', {}).get('score', 'N/A')}
Credit Risk Level: {risk.get('credit_score_risk_level', {}).get('risk_level', 'N/A')}

Loan Amount Risk: {risk.get('loan_amount_risk_assessment', {}).get('risk_level', 'N/A')}
Overall Financial Risk Score: {risk.get('overall_financial_risk', {}).get('risk_score', 'N/A')}/100
Anomalies Detected: {risk.get('anomaly_detection', {}).get('total_anomalies', 0)}
"""
        return summary

    def _summarize_decision(self, decision: dict) -> str:
        """Summarize loan decision"""
        if not decision:
            return "No decision data available"

        summary = f"""
Decision: {decision.get('decision', {}).get('classification', 'N/A')}
Risk Score: {decision.get('decision', {}).get('risk_score', 'N/A')}/100
Confidence Level: {decision.get('decision', {}).get('confidence_level', 0)}%

Loan Amount: ${decision.get('financial_breakdown', {}).get('requested_loan_amount', 0):,.0f}
Interest Rate: {decision.get('financial_breakdown', {}).get('recommended_interest_rate', 0)}%
Term: {decision.get('financial_breakdown', {}).get('recommended_term', 'N/A')}
Monthly Payment: ${decision.get('financial_breakdown', {}).get('estimated_monthly_payment', 0):,.0f}

Key Factors:
"""
        for factor in decision.get('key_decision_factors', [])[:3]:
            summary += f"- {factor.get('factor')}: {factor.get('value')} ({factor.get('impact')})\n"

        return summary

    async def process_application(self, applicant_id: str) -> dict:
        """
        Process loan application through orchestration engine

        Args:
            applicant_id: Applicant ID to process

        Returns:
            Final processing result
        """
        # Initialize MCP client
        if not self.mcp_client.initialize():
            return {"error": "Failed to initialize MCP client"}

        # Create initial state
        initial_state = {
            "applicant_id": applicant_id,
            "application_data": {},
            "applicant_profile": {},
            "financial_risk": {},
            "loan_decision": {},
            "compliance_actions": {},
            "final_recommendation": {},
            "errors": [],
            "processing_stages": []
        }

        try:
            # Execute workflow
            result = await asyncio.to_thread(self.workflow.invoke, initial_state)
            return result
        finally:
            # Cleanup
            self.mcp_client.close()

    def process_application_sync(self, applicant_id: str) -> dict:
        """
        Synchronous version of process_application

        Args:
            applicant_id: Applicant ID to process

        Returns:
            Final processing result
        """
        # Initialize MCP client
        if not self.mcp_client.initialize():
            return {"error": "Failed to initialize MCP client"}

        # Create initial state
        initial_state = {
            "applicant_id": applicant_id,
            "application_data": {},
            "applicant_profile": {},
            "financial_risk": {},
            "loan_decision": {},
            "compliance_actions": {},
            "final_recommendation": {},
            "errors": [],
            "processing_stages": []
        }

        try:
            # Execute workflow
            result = self.workflow.invoke(initial_state)
            return result
        finally:
            # Cleanup
            self.mcp_client.close()


# ============================================================================
# Utility Functions
# ============================================================================

def format_workflow_result(result: dict) -> dict:
    """Format workflow result for API response"""
    return {
        "applicant_id": result.get("applicant_id"),
        "processing_stages": result.get("processing_stages", []),
        "decision": result.get("loan_decision", {}).get("decision", {}).get("classification"),
        "risk_score": result.get("loan_decision", {}).get("decision", {}).get("risk_score"),
        "confidence": result.get("loan_decision", {}).get("decision", {}).get("confidence_level"),
        "case_id": result.get("compliance_actions", {}).get("case_id"),
        "llm_analysis": result.get("final_recommendation", {}),
        "errors": result.get("errors", []),
        "timestamp": datetime.now().isoformat()
    }
