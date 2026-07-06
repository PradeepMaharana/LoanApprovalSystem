#!/usr/bin/env python3

"""
Multi-Agent Agentic Chatbot UI for Loan Application Analysis
Analyzes loan applications using multiple AI agents and displays results
in an interactive, conversational chatbot interface
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from streamlit_integration import LoanAPIClient

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000"
PROCESSING_TIMEOUT = 30

st.set_page_config(
    page_title="🤖 Loan Analysis Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .agent-message {
        background: #f0f2f5;
        padding: 1rem;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .decision-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #ddd;
        margin: 1rem 0;
    }

    .approve {
        border-color: #28a745;
        background: #f0f9f5;
    }

    .reject {
        border-color: #dc3545;
        background: #fdf5f7;
    }

    .review {
        border-color: #ffc107;
        background: #fffef5;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }

    .risk-gauge {
        width: 100%;
        height: 30px;
        background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
        border-radius: 15px;
        position: relative;
        margin: 10px 0;
    }

    .factor-positive {
        color: #28a745;
        font-weight: bold;
    }

    .factor-negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state"""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None
    if "applicant_id" not in st.session_state:
        st.session_state.applicant_id = ""
    if "show_details" not in st.session_state:
        st.session_state.show_details = {}
    if "agents_executed" not in st.session_state:
        st.session_state.agents_executed = []


init_session_state()

# ============================================================================
# Agent Orchestration Functions
# ============================================================================

def fetch_applicant_profile_agent_analysis(applicant_id: str) -> Dict[str, Any]:
    """Get Applicant Profile Agent analysis"""
    try:
        cursor = None
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Tek@12345',
                database='loan_approval_system'
            )
            cursor = conn.cursor(dictionary=True)

            # Fetch applicant data
            cursor.execute("SELECT * FROM applicants WHERE applicant_id = %s", (applicant_id,))
            applicant = cursor.fetchone()

            # Fetch loan application
            cursor.execute("SELECT * FROM loan_applications WHERE applicant_id = %s", (applicant_id,))
            application = cursor.fetchone()

            # Fetch risk assessment
            cursor.execute("SELECT * FROM risk_assessments WHERE applicant_id = %s", (applicant_id,))
            risk_assessment = cursor.fetchone()

            if applicant:
                # Calculate income stability score (0-100)
                income_stability_score = risk_assessment.get('income_stability_score', 70) if risk_assessment else 70

                # Calculate employment risk score (0-100, inverted)
                employment_risk_score = risk_assessment.get('employment_risk_score', 40) if risk_assessment else 40

                return {
                    "status": "success",
                    "agent_name": "ApplicantProfileAgent",
                    "applicant_id": applicant_id,
                    "income_stability_score": income_stability_score,
                    "employment_risk_score": employment_risk_score,
                    "credit_category": risk_assessment.get('credit_category', 'Not Assessed') if risk_assessment else 'Not Assessed',
                    "employment_stability": "High" if employment_risk_score < 40 else "Moderate" if employment_risk_score < 70 else "Low",
                    "income_trend": "Stable" if income_stability_score >= 75 else "Moderate" if income_stability_score >= 50 else "Unstable",
                    "age": applicant.get('age'),
                    "income": applicant.get('income'),
                    "employment_type": applicant.get('employment_type'),
                    "location": applicant.get('location')
                }
            else:
                return {"status": "error", "error": f"Applicant {applicant_id} not found"}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    except Exception as e:
        return {"status": "error", "error": str(e)}


def fetch_financial_risk_agent_analysis(applicant_id: str) -> Dict[str, Any]:
    """Get Financial Risk Agent analysis"""
    try:
        cursor = None
        conn = None
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Tek@12345',
                database='loan_approval_system'
            )
            cursor = conn.cursor(dictionary=True)

            # Fetch applicant
            cursor.execute("SELECT * FROM applicants WHERE applicant_id = %s", (applicant_id,))
            applicant = cursor.fetchone()

            # Fetch loan application
            cursor.execute("SELECT * FROM loan_applications WHERE applicant_id = %s", (applicant_id,))
            application = cursor.fetchone()

            if applicant and application:
                income = applicant.get('income', 1)
                loan_amount = application.get('loan_amount', 0)
                liabilities = application.get('existing_liabilities', 0)
                credit_score = application.get('credit_score', 650)

                # Calculate DTI
                dti_ratio = (liabilities + loan_amount) / income if income > 0 else 1.0

                # Calculate LTI
                lti_ratio = loan_amount / income if income > 0 else 10.0

                # Calculate monthly payment
                tenure_months = application.get('tenure_months', 60)
                monthly_payment = loan_amount / tenure_months if tenure_months > 0 else 0

                return {
                    "status": "success",
                    "agent_name": "FinancialRiskAgent",
                    "applicant_id": applicant_id,
                    "dti_ratio": round(dti_ratio, 3),
                    "dti_percentage": round(dti_ratio * 100, 1),
                    "lti_ratio": round(lti_ratio, 3),
                    "lti_percentage": round(lti_ratio * 100, 1),
                    "monthly_payment_estimate": round(monthly_payment, 2),
                    "credit_score": credit_score,
                    "loan_amount": loan_amount,
                    "tenure_months": tenure_months,
                    "existing_liabilities": liabilities,
                    "financial_risk_level": "Low" if dti_ratio < 0.43 else "Moderate" if dti_ratio < 0.60 else "High"
                }
            else:
                return {"status": "error", "error": f"Applicant or application not found"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    except Exception as e:
        return {"status": "error", "error": str(e)}


def fetch_loan_decision_agent_analysis(applicant_id: str,
                                       profile_data: Dict[str, Any],
                                       financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get Loan Decision Agent analysis"""
    try:
        cursor = None
        conn = None
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Tek@12345',
                database='loan_approval_system'
            )
            cursor = conn.cursor(dictionary=True)

            # Fetch application data
            cursor.execute("SELECT * FROM loan_applications WHERE applicant_id = %s", (applicant_id,))
            application = cursor.fetchone()

            if application:
                # Get pre-calculated risk score from database
                risk_score = application.get('risk_score', 50)

                # Classify decision based on risk score
                if risk_score >= 75:
                    classification = "APPROVE"
                    confidence = 95
                elif risk_score >= 60:
                    classification = "APPROVE"
                    confidence = 80
                elif risk_score >= 45:
                    classification = "REVIEW"
                    confidence = 65
                elif risk_score >= 30:
                    classification = "REJECT"
                    confidence = 75
                else:
                    classification = "REJECT"
                    confidence = 90

                # Build key decision factors
                key_factors = []

                # Credit score factor
                credit_score = application.get('credit_score', 650)
                if credit_score >= 750:
                    key_factors.append({
                        "factor": "Credit Score",
                        "value": credit_score,
                        "impact": "Positive",
                        "contribution": 25,
                        "weight": 25
                    })
                else:
                    key_factors.append({
                        "factor": "Credit Score",
                        "value": credit_score,
                        "impact": "Negative" if credit_score < 650 else "Neutral",
                        "contribution": -15 if credit_score < 650 else 10,
                        "weight": 25
                    })

                # Income stability factor
                income_stability = profile_data.get('income_stability_score', 50)
                key_factors.append({
                    "factor": "Income Stability",
                    "value": income_stability,
                    "impact": "Positive" if income_stability >= 75 else "Negative" if income_stability < 50 else "Moderate",
                    "contribution": 20 if income_stability >= 75 else -20 if income_stability < 50 else 5,
                    "weight": 20
                })

                # Employment risk factor
                employment_risk = profile_data.get('employment_risk_score', 50)
                key_factors.append({
                    "factor": "Employment Risk",
                    "value": employment_risk,
                    "impact": "Positive" if employment_risk < 40 else "Negative" if employment_risk > 70 else "Moderate",
                    "contribution": 20 if employment_risk < 40 else -20 if employment_risk > 70 else 5,
                    "weight": 20
                })

                # DTI factor
                dti_ratio = financial_data.get('dti_ratio', 0.5)
                key_factors.append({
                    "factor": "Debt-to-Income Ratio",
                    "value": round(dti_ratio * 100, 1),
                    "impact": "Positive" if dti_ratio < 0.43 else "Negative" if dti_ratio > 0.60 else "Moderate",
                    "contribution": 15 if dti_ratio < 0.43 else -15 if dti_ratio > 0.60 else 0,
                    "weight": 15
                })

                # LTI factor
                lti_ratio = financial_data.get('lti_ratio', 2.0)
                key_factors.append({
                    "factor": "Loan-to-Income Ratio",
                    "value": round(lti_ratio, 2),
                    "impact": "Positive" if lti_ratio < 2 else "Negative" if lti_ratio > 5 else "Moderate",
                    "contribution": 10 if lti_ratio < 2 else -10 if lti_ratio > 5 else 0,
                    "weight": 10
                })

                # Generate explanation
                explanation = f"Applicant {applicant_id}: "
                if classification == "APPROVE":
                    explanation += f"Strong credit profile ({credit_score} credit score) with "
                    if income_stability >= 75:
                        explanation += "stable income. "
                    else:
                        explanation += "acceptable income stability. "
                    explanation += f"Financial metrics are within acceptable ranges (DTI: {financial_data.get('dti_percentage', 0):.1f}%). "
                    explanation += "Recommend approval with standard terms."
                elif classification == "REVIEW":
                    explanation += "Mixed signals detected. "
                    if income_stability < 50:
                        explanation += "Income stability concerns noted. "
                    if dti_ratio > 0.50:
                        explanation += "Debt levels are moderate-to-high. "
                    explanation += "Recommend manual underwriter review with possible conditions."
                else:  # REJECT
                    explanation += "Significant risk factors identified. "
                    if credit_score < 600:
                        explanation += f"Credit score ({credit_score}) below acceptable threshold. "
                    if employment_risk > 70:
                        explanation += "Employment risk is high. "
                    if dti_ratio > 0.70:
                        explanation += "Debt-to-income ratio is excessive. "
                    explanation += "Recommend rejection; applicant may reapply after improving credit profile."

                return {
                    "status": "success",
                    "agent_name": "LoanDecisionAgent",
                    "applicant_id": applicant_id,
                    "classification": classification,
                    "classification_reason": f"{classification} - {['Strong approval', 'Approval acceptable', 'Manual review', 'Rejection significant', 'Rejection high risk'][['APPROVE', 'APPROVE', 'REVIEW', 'REJECT', 'REJECT'].index(classification if risk_score >= 60 else 'APPROVE' if risk_score >= 60 else 'REVIEW' if risk_score >= 45 else 'REJECT')]}" if risk_score >= 60 or risk_score < 45 else "Requires Review",
                    "risk_score": round(risk_score, 2),
                    "confidence_level": confidence,
                    "key_decision_factors": key_factors,
                    "explanation": explanation,
                    "recommended_actions": [
                        "Proceed with standard approval process" if classification == "APPROVE" else
                        "Schedule for manual underwriter review" if classification == "REVIEW" else
                        "Consider rejection; applicant may reapply after 6 months"
                    ]
                }
            else:
                return {"status": "error", "error": f"Application not found"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    except Exception as e:
        return {"status": "error", "error": str(e)}


def orchestrate_analysis(applicant_id: str) -> Dict[str, Any]:
    """Orchestrate all agents for comprehensive analysis"""
    try:
        # Execute agents in sequence
        st.session_state.agents_executed = []

        # Step 1: Applicant Profile Agent
        with st.spinner("👤 Running Applicant Profile Agent..."):
            profile_analysis = fetch_applicant_profile_agent_analysis(applicant_id)
            if profile_analysis.get("status") != "success":
                return {"status": "error", "error": profile_analysis.get("error")}
            st.session_state.agents_executed.append(profile_analysis['agent_name'])

        # Step 2: Financial Risk Agent
        with st.spinner("💰 Running Financial Risk Agent..."):
            financial_analysis = fetch_financial_risk_agent_analysis(applicant_id)
            if financial_analysis.get("status") != "success":
                return {"status": "error", "error": financial_analysis.get("error")}
            st.session_state.agents_executed.append(financial_analysis['agent_name'])

        # Step 3: Loan Decision Agent
        with st.spinner("🎯 Running Loan Decision Agent..."):
            decision_analysis = fetch_loan_decision_agent_analysis(applicant_id, profile_analysis, financial_analysis)
            if decision_analysis.get("status") != "success":
                return {"status": "error", "error": decision_analysis.get("error")}
            st.session_state.agents_executed.append(decision_analysis['agent_name'])

        # Combine all results
        return {
            "status": "success",
            "applicant_id": applicant_id,
            "analysis_time": datetime.now().isoformat(),
            "applicant_profile": profile_analysis,
            "financial_analysis": financial_analysis,
            "decision": decision_analysis,
            "agents_executed": st.session_state.agents_executed
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============================================================================
# UI Components - Header
# ============================================================================

def render_header():
    """Render page header"""
    st.markdown("""
    <div class="chatbot-header">
        <h1>🤖 Loan Analysis Chatbot</h1>
        <p>Multi-Agent AI System for Intelligent Loan Application Analysis</p>
        <p style="font-size: 0.9rem;">Powered by: ApplicantProfileAgent • FinancialRiskAgent • LoanDecisionAgent</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# UI Components - Analysis Display
# ============================================================================

def display_decision_summary(decision: Dict[str, Any]):
    """Display decision summary with chatbot-style message"""
    classification = decision.get('classification', 'UNKNOWN')
    risk_score = decision.get('risk_score', 0)
    confidence = decision.get('confidence_level', 0)

    # Determine styling based on classification
    if classification == "APPROVE":
        decision_class = "approve"
        icon = "✅"
        color = "#28a745"
    elif classification == "REJECT":
        decision_class = "reject"
        icon = "❌"
        color = "#dc3545"
    else:
        decision_class = "review"
        icon = "⚠️"
        color = "#ffc107"

    st.markdown(f"""
    <div class="decision-card {decision_class}">
        <h2 style="color: {color}; margin: 0 0 1rem 0;">
            {icon} DECISION: {classification}
        </h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div>
                <strong>Risk Score:</strong><br>
                <span style="font-size: 1.5rem; color: {color};">{risk_score}/100</span>
            </div>
            <div>
                <strong>Confidence Level:</strong><br>
                <span style="font-size: 1.5rem; color: {color};">{confidence}%</span>
            </div>
        </div>
        <div class="risk-gauge" style="margin: 1rem 0;"></div>
        <p><strong>Reason:</strong> {decision.get('classification_reason', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Explanation
    st.markdown("**Detailed Explanation:**")
    st.info(decision.get('explanation', 'No explanation available'))


def display_applicant_profile_analysis(profile: Dict[str, Any]):
    """Display applicant profile agent analysis"""
    st.markdown("### 👤 Applicant Profile Analysis")
    st.markdown("<div class='agent-message'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        income_stability = profile.get('income_stability_score', 0)
        if income_stability >= 80:
            st.markdown(f"✅ **Income Stability Score**\n\n{income_stability}/100\n\nStable")
        elif income_stability >= 60:
            st.markdown(f"ℹ️ **Income Stability Score**\n\n{income_stability}/100\n\nModerate")
        else:
            st.markdown(f"⚠️ **Income Stability Score**\n\n{income_stability}/100\n\nUnstable")

    with col2:
        employment_risk = profile.get('employment_risk_score', 0)
        if employment_risk <= 40:
            st.markdown(f"✅ **Employment Risk Score**\n\n{employment_risk}/100\n\nLow Risk")
        elif employment_risk <= 70:
            st.markdown(f"ℹ️ **Employment Risk Score**\n\n{employment_risk}/100\n\nModerate Risk")
        else:
            st.markdown(f"⚠️ **Employment Risk Score**\n\n{employment_risk}/100\n\nHigh Risk")

    with col3:
        credit_category = profile.get('credit_category', 'Not Assessed')
        st.markdown(f"📊 **Credit Category**\n\n{credit_category}\n\n{profile.get('income_trend', 'Stable')} Trend")

    st.markdown("</div>", unsafe_allow_html=True)

    # Additional details
    with st.expander("📋 Detailed Applicant Profile", expanded=False):
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.write(f"**Age:** {profile.get('age', 'N/A')} years")
            st.write(f"**Employment Type:** {profile.get('employment_type', 'N/A')}")
            st.write(f"**Income Trend:** {profile.get('income_trend', 'N/A')}")

        with col_d2:
            st.write(f"**Annual Income:** ${profile.get('income', 0):,.0f}")
            st.write(f"**Employment Stability:** {profile.get('employment_stability', 'N/A')}")
            st.write(f"**Location:** {profile.get('location', 'N/A')}")


def display_financial_analysis(financial: Dict[str, Any]):
    """Display financial risk agent analysis"""
    st.markdown("### 💰 Financial Analysis")
    st.markdown("<div class='agent-message'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        dti = financial.get('dti_percentage', 0)
        if dti < 43:
            st.markdown(f"✅ **DTI Ratio**\n\n{dti:.1f}%\n\nHealthy")
        elif dti < 60:
            st.markdown(f"ℹ️ **DTI Ratio**\n\n{dti:.1f}%\n\nModerate")
        else:
            st.markdown(f"⚠️ **DTI Ratio**\n\n{dti:.1f}%\n\nConcerning")

    with col2:
        lti = financial.get('lti_percentage', 0)
        if lti < 200:
            st.markdown(f"✅ **LTI Ratio**\n\n{lti:.1f}%\n\nLow")
        elif lti < 400:
            st.markdown(f"ℹ️ **LTI Ratio**\n\n{lti:.1f}%\n\nModerate")
        else:
            st.markdown(f"⚠️ **LTI Ratio**\n\n{lti:.1f}%\n\nHigh")

    with col3:
        st.markdown(f"💵 **Monthly Payment**\n\n${financial.get('monthly_payment_estimate', 0):,.2f}\n\nEstimate")

    with col4:
        risk_level = financial.get('financial_risk_level', 'Unknown')
        if risk_level == "Low":
            st.markdown(f"✅ **Financial Risk**\n\n{risk_level}\n\nAcceptable")
        elif risk_level == "Moderate":
            st.markdown(f"ℹ️ **Financial Risk**\n\n{risk_level}\n\nCautious")
        else:
            st.markdown(f"⚠️ **Financial Risk**\n\n{risk_level}\n\nConcern")

    st.markdown("</div>", unsafe_allow_html=True)

    # Detailed breakdown
    with st.expander("📊 Financial Details Breakdown", expanded=False):
        col_fd1, col_fd2 = st.columns(2)

        with col_fd1:
            st.write(f"**Credit Score:** {financial.get('credit_score', 'N/A')}")
            st.write(f"**Loan Amount:** ${financial.get('loan_amount', 0):,.0f}")
            st.write(f"**Existing Liabilities:** ${financial.get('existing_liabilities', 0):,.0f}")

        with col_fd2:
            st.write(f"**Tenure:** {financial.get('tenure_months', 'N/A')} months")
            st.write(f"**DTI Ratio (Normalized):** {financial.get('dti_ratio', 0):.3f}")
            st.write(f"**LTI Ratio (Normalized):** {financial.get('lti_ratio', 0):.3f}")


def display_decision_factors(factors: List[Dict[str, Any]]):
    """Display key decision factors from Loan Decision Agent"""
    st.markdown("### 🎯 Key Decision Factors")
    st.markdown("<div class='agent-message'>", unsafe_allow_html=True)

    # Create factors dataframe
    factors_data = []
    for f in factors:
        factors_data.append({
            "Factor": f.get('factor', 'N/A'),
            "Value": str(f.get('value', 'N/A')),
            "Impact": f.get('impact', 'N/A'),
            "Contribution": f"{f.get('contribution', 0):+.0f} pts",
            "Weight": f"{f.get('weight', 0):.0f}%"
        })

    df = pd.DataFrame(factors_data)

    # Display with color coding
    for idx, row in df.iterrows():
        impact_class = "factor-positive" if row['Impact'] == "Positive" else "factor-negative" if row['Impact'] == "Negative" else ""
        st.markdown(f"""
        <div style="padding: 0.5rem; border-left: 3px solid {'#28a745' if row['Impact'] == 'Positive' else '#dc3545' if row['Impact'] == 'Negative' else '#ffc107'}; margin: 0.5rem 0;">
            <strong>{row['Factor']}</strong> | Value: {row['Value']} | <span class="{impact_class}">{row['Impact']}</span> ({row['Contribution']}) | Weight: {row['Weight']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def display_recommended_actions(actions: List[str]):
    """Display recommended actions"""
    st.markdown("### ✅ Recommended Actions")

    for i, action in enumerate(actions, 1):
        st.markdown(f"**{i}. {action}**")


def display_agents_executed(agents: List[str]):
    """Display which agents were executed"""
    st.markdown("### 🤖 Agents Executed")

    col1, col2, col3 = st.columns(3)

    with col1:
        if 'ApplicantProfileAgent' in agents:
            st.success("✅ Applicant Profile Agent")
        else:
            st.error("❌ Applicant Profile Agent")

    with col2:
        if 'FinancialRiskAgent' in agents:
            st.success("✅ Financial Risk Agent")
        else:
            st.error("❌ Financial Risk Agent")

    with col3:
        if 'LoanDecisionAgent' in agents:
            st.success("✅ Loan Decision Agent")
        else:
            st.error("❌ Loan Decision Agent")

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application"""
    render_header()

    # Sidebar for input
    with st.sidebar:
        st.header("🔍 Loan Analysis")

        # Application search
        st.markdown("**Enter Applicant ID to Analyze:**")
        col_s1, col_s2 = st.columns([3, 1])

        with col_s1:
            applicant_id = st.text_input(
                "Applicant ID",
                value=st.session_state.applicant_id,
                placeholder="APP-2024-001001",
                label_visibility="collapsed"
            )
            st.session_state.applicant_id = applicant_id

        with col_s2:
            analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")

        st.markdown("---")

        if analyze_button:
            if not applicant_id:
                st.error("❌ Please enter an Applicant ID")
            else:
                with st.spinner("🔄 Analyzing application..."):
                    result = orchestrate_analysis(applicant_id)

                    if result.get("status") == "success":
                        st.session_state.current_analysis = result
                        st.success("✅ Analysis complete!")
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

        st.markdown("---")

        # Help section
        with st.expander("📖 How to Use", expanded=False):
            st.markdown("""
            ### Steps:
            1. Enter Applicant ID (e.g., APP-2024-001001)
            2. Click "🔍 Analyze" button
            3. Wait for all agents to execute
            4. Review comprehensive analysis:
               - 👤 Applicant Profile (Income Stability, Employment Risk)
               - 💰 Financial Analysis (DTI, LTI, Payments)
               - 🎯 Decision Factors (Top 5 factors)
               - ✅ Recommended Actions

            ### Agent System:
            - **ApplicantProfileAgent**: Analyzes applicant stability and employment risk
            - **FinancialRiskAgent**: Calculates financial metrics (DTI, LTI)
            - **LoanDecisionAgent**: Makes final decision with confidence & factors
            """)

        with st.expander("🔗 Quick Links", expanded=False):
            st.markdown("""
            - [API Health](http://localhost:8000/health)
            - [Submit Application](http://localhost:8502)
            - [GitHub Repo](https://github.com/PradeepMaharana/LoanApprovalSystem)
            """)

    # Main content
    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis

        # Display decision summary prominently
        display_decision_summary(analysis['decision'])

        st.markdown("---")

        # Create tabs for different analysis views
        tabs = st.tabs([
            "👤 Applicant Profile",
            "💰 Financial Analysis",
            "🎯 Decision Factors",
            "✅ Actions",
            "🤖 Agents"
        ])

        with tabs[0]:
            display_applicant_profile_analysis(analysis['applicant_profile'])

        with tabs[1]:
            display_financial_analysis(analysis['financial_analysis'])

        with tabs[2]:
            display_decision_factors(analysis['decision'].get('key_decision_factors', []))

        with tabs[3]:
            display_recommended_actions(analysis['decision'].get('recommended_actions', []))

        with tabs[4]:
            display_agents_executed(analysis['agents_executed'])
            st.markdown("---")
            st.markdown("**Analysis Timestamp:**")
            st.write(analysis.get('analysis_time', 'N/A'))

        # Export option
        st.markdown("---")
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            if st.button("📥 Download Full Analysis (JSON)", use_container_width=True):
                json_data = json.dumps(analysis, indent=2, default=str)
                st.download_button(
                    label="Download",
                    data=json_data,
                    file_name=f"analysis_{applicant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col_exp2:
            if st.button("🔄 Analyze Another", use_container_width=True):
                st.session_state.current_analysis = None
                st.session_state.applicant_id = ""
                st.rerun()

    else:
        # Welcome message
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h2>👋 Welcome to Loan Analysis Chatbot</h2>
            <p style="font-size: 1.2rem;">Multi-Agent AI System for Loan Application Analysis</p>

            <div style="background: #f0f2f5; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
                <h3>🤖 How It Works:</h3>
                <p>Our system uses three intelligent agents to analyze loan applications:</p>

                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div style="background: white; padding: 1rem; border-radius: 8px;">
                        <h4>👤 Applicant Profile Agent</h4>
                        <p>Analyzes income stability and employment risk</p>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px;">
                        <h4>💰 Financial Risk Agent</h4>
                        <p>Calculates DTI, LTI, and financial metrics</p>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px;">
                        <h4>🎯 Loan Decision Agent</h4>
                        <p>Synthesizes decision with confidence and factors</p>
                    </div>
                </div>
            </div>

            <h3>📝 To Get Started:</h3>
            <p>1. Enter an Applicant ID in the sidebar (e.g., APP-2024-001001)</p>
            <p>2. Click "🔍 Analyze"</p>
            <p>3. Review the comprehensive analysis</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
