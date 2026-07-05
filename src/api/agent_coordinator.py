"""
Agent Coordinator: Orchestrates agents and synthesizes responses for Chatbot UI

Responsibilities:
1. Fetches contextual data from agents
2. Aggregates agent analysis results
3. Invokes LLM for synthesis
4. Returns comprehensive decision with all agent insights
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinates agent execution and response synthesis"""

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        self.agent_responses = {}

    def connect_database(self) -> bool:
        """Establish MySQL connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                logger.info("✅ AgentCoordinator: Connected to MySQL")
                return True
        except Error as e:
            logger.error(f"❌ Database connection error: {e}")
            return False

    def disconnect_database(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("✅ AgentCoordinator: Database disconnected")

    def fetch_applicant_profile_analysis(self, applicant_id: str) -> Dict[str, Any]:
        """
        Fetch and analyze applicant profile data
        Returns: Income Stability Score, Employment Risk Score, Credit Summary
        """
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Fetch applicant profile
            cursor.execute(
                "SELECT * FROM applicants WHERE applicant_id = %s",
                (applicant_id,)
            )
            applicant = cursor.fetchone()

            # Fetch loan application
            cursor.execute(
                "SELECT * FROM loan_applications WHERE applicant_id = %s",
                (applicant_id,)
            )
            application = cursor.fetchone()

            # Fetch risk assessment
            cursor.execute(
                "SELECT * FROM risk_assessments WHERE applicant_id = %s",
                (applicant_id,)
            )
            risk_assessment = cursor.fetchone()

            cursor.close()

            if not applicant:
                return {"error": f"Applicant {applicant_id} not found"}

            # Extract Applicant Profile Agent metrics
            profile_analysis = {
                "applicant_id": applicant_id,
                "age": applicant.get("age"),
                "income": applicant.get("income"),
                "employment_type": applicant.get("employment_type"),
                "location": applicant.get("location"),
                "income_stability_score": risk_assessment.get("income_stability_score", 0) if risk_assessment else 0,
                "employment_risk_score": risk_assessment.get("employment_risk_score", 0) if risk_assessment else 0,
                "credit_category": risk_assessment.get("credit_category", "Not Assessed") if risk_assessment else "Not Assessed",
                "application_status": application.get("application_status") if application else "SUBMITTED",
                "credit_score": application.get("credit_score") if application else 0,
                "loan_amount": application.get("loan_amount") if application else 0,
            }

            logger.info(f"✅ Applicant Profile Agent: Analyzed {applicant_id}")
            return {
                "agent": "ApplicantProfileAgent",
                "status": "success",
                "data": profile_analysis
            }

        except Error as e:
            logger.error(f"❌ Applicant Profile Agent error: {e}")
            return {"agent": "ApplicantProfileAgent", "status": "error", "error": str(e)}

    def fetch_financial_risk_analysis(self, applicant_id: str) -> Dict[str, Any]:
        """
        Fetch and analyze financial risk data
        Returns: DTI Ratio, LTI Ratio, Risk Factors
        """
        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM loan_applications WHERE applicant_id = %s",
                (applicant_id,)
            )
            application = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM risk_assessments WHERE applicant_id = %s",
                (applicant_id,)
            )
            risk_assessment = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM applicants WHERE applicant_id = %s",
                (applicant_id,)
            )
            applicant = cursor.fetchone()

            cursor.close()

            if not application:
                return {"error": f"No application found for {applicant_id}"}

            # Calculate financial metrics
            income = applicant.get("income", 1) if applicant else 1
            loan_amount = application.get("loan_amount", 0)
            existing_liabilities = application.get("existing_liabilities", 0)

            dti_ratio = (existing_liabilities + loan_amount) / income if income > 0 else 0
            lti_ratio = loan_amount / income if income > 0 else 0

            financial_risk = {
                "applicant_id": applicant_id,
                "dti_ratio": round(dti_ratio, 3),
                "lti_ratio": round(lti_ratio, 3),
                "debt_to_income_percentage": round(dti_ratio * 100, 2),
                "loan_to_income_percentage": round(lti_ratio * 100, 2),
                "existing_liabilities": existing_liabilities,
                "loan_amount": loan_amount,
                "monthly_payment_estimate": round(loan_amount / (application.get("tenure_months", 60) / 12), 2),
                "dti_impact": risk_assessment.get("dti_impact", 0) if risk_assessment else 0,
                "lti_impact": risk_assessment.get("lti_impact", 0) if risk_assessment else 0,
            }

            logger.info(f"✅ Financial Risk Agent: Analyzed {applicant_id}")
            return {
                "agent": "FinancialRiskAgent",
                "status": "success",
                "data": financial_risk
            }

        except Error as e:
            logger.error(f"❌ Financial Risk Agent error: {e}")
            return {"agent": "FinancialRiskAgent", "status": "error", "error": str(e)}

    def fetch_loan_decision_analysis(self, applicant_id: str, profile_data: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch and synthesize loan decision
        Returns: Classification, Risk Score, Confidence, Key Factors, Explanation
        """
        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM loan_applications WHERE applicant_id = %s",
                (applicant_id,)
            )
            application = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM risk_assessments WHERE applicant_id = %s",
                (applicant_id,)
            )
            risk_assessment = cursor.fetchone()

            cursor.close()

            if not application:
                return {"error": f"No application found for {applicant_id}"}

            # Calculate comprehensive risk score
            risk_score = application.get("risk_score", 50)
            credit_score = application.get("credit_score", 650)

            # Determine classification based on risk score
            if risk_score >= 75:
                classification = "APPROVE"
                confidence = 95
                explanation = "Applicant has strong financial profile with low risk indicators"
            elif risk_score >= 60:
                classification = "APPROVE"
                confidence = 80
                explanation = "Applicant meets approval criteria with acceptable risk level"
            elif risk_score >= 40:
                classification = "REVIEW"
                confidence = 65
                explanation = "Applicant requires manual review due to moderate risk factors"
            elif risk_score >= 20:
                classification = "REJECT"
                confidence = 75
                explanation = "Applicant presents elevated risk factors for approval"
            else:
                classification = "REJECT"
                confidence = 90
                explanation = "Applicant does not meet approval criteria"

            # Extract decision factors
            decision_factors = {
                "credit_score_factor": "Strong" if credit_score >= 750 else "Good" if credit_score >= 700 else "Fair" if credit_score >= 650 else "Poor",
                "dti_ratio_factor": "Acceptable" if financial_data.get("data", {}).get("dti_ratio", 1) <= 0.43 else "High",
                "income_stability": "Stable" if profile_data.get("data", {}).get("income_stability_score", 0) >= 70 else "Moderate" if profile_data.get("data", {}).get("income_stability_score", 0) >= 50 else "Low",
                "employment_risk": "Low" if profile_data.get("data", {}).get("employment_risk_score", 100) <= 30 else "Moderate" if profile_data.get("data", {}).get("employment_risk_score", 100) <= 70 else "High",
            }

            decision_data = {
                "applicant_id": applicant_id,
                "classification": classification,
                "risk_score": round(risk_score, 2),
                "confidence_level": confidence,
                "key_decision_factors": decision_factors,
                "explanation": explanation,
                "credit_score": credit_score,
                "recommended_actions": self._get_recommended_actions(classification, risk_score),
                "decision_timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Loan Decision Agent: {classification} decision for {applicant_id} (Risk: {risk_score}, Confidence: {confidence}%)")
            return {
                "agent": "LoanDecisionAgent",
                "status": "success",
                "data": decision_data
            }

        except Error as e:
            logger.error(f"❌ Loan Decision Agent error: {e}")
            return {"agent": "LoanDecisionAgent", "status": "error", "error": str(e)}

    def _get_recommended_actions(self, classification: str, risk_score: float) -> List[str]:
        """Get recommended actions based on classification"""
        actions = []

        if classification == "APPROVE":
            actions = [
                "Proceed with loan approval",
                "Generate loan offer letter",
                "Schedule documentation review",
            ]
        elif classification == "REVIEW":
            actions = [
                "Schedule manual review with underwriter",
                "Request additional documentation",
                "Conduct in-depth financial analysis",
            ]
        else:  # REJECT
            actions = [
                "Prepare rejection letter",
                "Provide feedback on improvement areas",
                "Suggest reapplication timeline",
            ]

        return actions

    def coordinate_agent_analysis(self, applicant_id: str) -> Dict[str, Any]:
        """
        Orchestrate all agents and synthesize comprehensive response
        """
        logger.info(f"🔄 AgentCoordinator: Starting analysis for {applicant_id}")

        # Step 1: Fetch Applicant Profile Analysis
        profile_response = self.fetch_applicant_profile_analysis(applicant_id)
        if profile_response.get("status") == "error":
            return {"error": "Failed to fetch applicant profile", "details": profile_response}

        # Step 2: Fetch Financial Risk Analysis
        financial_response = self.fetch_financial_risk_analysis(applicant_id)
        if financial_response.get("status") == "error":
            return {"error": "Failed to fetch financial risk analysis", "details": financial_response}

        # Step 3: Fetch Loan Decision Analysis (using data from previous agents)
        decision_response = self.fetch_loan_decision_analysis(
            applicant_id,
            profile_response,
            financial_response
        )
        if decision_response.get("status") == "error":
            return {"error": "Failed to fetch loan decision", "details": decision_response}

        # Step 4: Synthesize all responses
        synthesized_response = {
            "applicant_id": applicant_id,
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "applicant_profile_agent": profile_response.get("data", {}),
                "financial_risk_agent": financial_response.get("data", {}),
                "loan_decision_agent": decision_response.get("data", {}),
            },
            "synthesis": {
                "final_decision": decision_response.get("data", {}).get("classification"),
                "risk_assessment": {
                    "overall_risk_score": decision_response.get("data", {}).get("risk_score"),
                    "confidence_level": decision_response.get("data", {}).get("confidence_level"),
                },
                "applicant_profile_summary": {
                    "income_stability_score": profile_response.get("data", {}).get("income_stability_score"),
                    "employment_risk_score": profile_response.get("data", {}).get("employment_risk_score"),
                    "credit_category": profile_response.get("data", {}).get("credit_category"),
                    "employment_type": profile_response.get("data", {}).get("employment_type"),
                    "location": profile_response.get("data", {}).get("location"),
                },
                "financial_summary": {
                    "dti_ratio": financial_response.get("data", {}).get("dti_ratio"),
                    "lti_ratio": financial_response.get("data", {}).get("lti_ratio"),
                    "monthly_payment_estimate": financial_response.get("data", {}).get("monthly_payment_estimate"),
                },
                "decision_details": {
                    "key_factors": decision_response.get("data", {}).get("key_decision_factors"),
                    "explanation": decision_response.get("data", {}).get("explanation"),
                    "recommended_actions": decision_response.get("data", {}).get("recommended_actions"),
                },
            },
            "status": "success"
        }

        logger.info(f"✅ AgentCoordinator: Synthesis complete for {applicant_id}")
        return synthesized_response

    def to_chatbot_format(self, synthesized_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert synthesized response to Chatbot UI format"""
        if synthesized_response.get("status") != "success":
            return {
                "status": "error",
                "message": synthesized_response.get("error", "Unknown error"),
            }

        synthesis = synthesized_response.get("synthesis", {})
        decision = synthesized_response.get("agents", {}).get("loan_decision_agent", {})
        profile = synthesized_response.get("agents", {}).get("applicant_profile_agent", {})
        financial = synthesized_response.get("agents", {}).get("financial_risk_agent", {})

        return {
            "status": "success",
            "applicant_id": synthesized_response.get("applicant_id"),
            "decision": {
                "classification": synthesis.get("final_decision"),
                "risk_score": synthesis.get("risk_assessment", {}).get("overall_risk_score"),
                "confidence_level": synthesis.get("risk_assessment", {}).get("confidence_level"),
                "explanation": synthesis.get("decision_details", {}).get("explanation"),
                "key_factors": synthesis.get("decision_details", {}).get("key_factors"),
                "recommended_actions": synthesis.get("decision_details", {}).get("recommended_actions"),
            },
            "applicant_profile": {
                "income_stability_score": profile.get("income_stability_score"),
                "employment_risk_score": profile.get("employment_risk_score"),
                "credit_category": profile.get("credit_category"),
                "employment_type": profile.get("employment_type"),
                "age": profile.get("age"),
                "income": profile.get("income"),
                "location": profile.get("location"),
                "credit_score": profile.get("credit_score"),
            },
            "financial_analysis": {
                "dti_ratio": financial.get("dti_ratio"),
                "lti_ratio": financial.get("lti_ratio"),
                "debt_to_income_percentage": financial.get("debt_to_income_percentage"),
                "loan_to_income_percentage": financial.get("loan_to_income_percentage"),
                "monthly_payment_estimate": financial.get("monthly_payment_estimate"),
            },
            "timestamp": synthesized_response.get("timestamp"),
        }
