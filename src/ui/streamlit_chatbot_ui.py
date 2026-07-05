#!/usr/bin/env python3

"""
Enhanced Streamlit Chatbot UI for Loan Application
Displays comprehensive agent analysis including Income Stability, Employment Risk,
and Loan Decision details (Classification, Risk Score, Confidence, Factors, Explanation)
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from streamlit_integration import LoanAPIClient

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000"
PROCESSING_TIMEOUT = 120

st.set_page_config(
    page_title="🏦 Loan Application AI Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state"""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "agent_analysis" not in st.session_state:
        st.session_state.agent_analysis = None
    if "applicant_id" not in st.session_state:
        st.session_state.applicant_id = None
    if "show_raw_json" not in st.session_state:
        st.session_state.show_raw_json = False


init_session_state()

# ============================================================================
# Helper Functions
# ============================================================================

def get_agent_analysis(applicant_id: str) -> Dict[str, Any]:
    """Get comprehensive agent analysis from orchestrator"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/analyze/{applicant_id}",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"API error: {response.status_code}"}

    except requests.Timeout:
        return {"status": "error", "error": "Analysis timeout - request took too long"}
    except requests.ConnectionError:
        return {"status": "error", "error": "Failed to connect to API server"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def display_applicant_profile(profile: Dict[str, Any]):
    """Display applicant profile information"""
    st.subheader("👤 Applicant Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Income Stability Score", f"{profile.get('income_stability_score', 'N/A')}/100")
        st.metric("Age", f"{profile.get('age', 'N/A')} years")
        st.metric("Income", f"${profile.get('income', 0):,.0f}")

    with col2:
        st.metric("Employment Risk Score", f"{profile.get('employment_risk_score', 'N/A')}/100")
        st.metric("Credit Score", profile.get('credit_score', 'N/A'))
        st.metric("Credit Category", profile.get('credit_category', 'N/A'))

    with col3:
        st.metric("Employment Type", profile.get('employment_type', 'N/A'))
        st.metric("Location", profile.get('location', 'N/A'))

    st.divider()


def display_loan_decision(decision: Dict[str, Any]):
    """Display loan decision details"""
    st.subheader("🎯 Loan Decision")

    # Decision Classification Banner
    classification = decision.get('classification', 'N/A')
    if classification == 'APPROVE':
        st.success(f"✅ **DECISION: {classification}**")
    elif classification == 'REJECT':
        st.error(f"❌ **DECISION: {classification}**")
    else:
        st.warning(f"⏳ **DECISION: {classification}**")

    # Key Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Risk Score", f"{decision.get('risk_score', 'N/A')}/100")

    with col2:
        st.metric("Confidence Level", f"{decision.get('confidence_level', 'N/A')}%")

    with col3:
        st.metric("Application Status", "Analyzed")

    # Explanation
    st.markdown(f"**📝 Explanation:** {decision.get('explanation', 'No explanation available')}")

    st.divider()


def display_decision_factors(factors: Dict[str, Any]):
    """Display key decision factors"""
    st.subheader("📊 Key Decision Factors")

    if not factors:
        st.info("No decision factors available")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Factor Breakdown:**")
        for factor, value in factors.items():
            st.write(f"• **{factor.replace('_', ' ').title()}**: {value}")

    with col2:
        # Visual representation
        st.write("**Factor Analysis:**")
        factors_df = pd.DataFrame([
            {"Factor": k.replace('_', ' ').title(), "Assessment": str(v)}
            for k, v in factors.items()
        ])
        st.table(factors_df)

    st.divider()


def display_financial_analysis(financial: Dict[str, Any]):
    """Display financial analysis"""
    st.subheader("💰 Financial Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Debt-to-Income Ratio", f"{financial.get('dti_ratio', 'N/A'):.3f}")
        st.metric("DTI Percentage", f"{financial.get('debt_to_income_percentage', 'N/A'):.1f}%")

    with col2:
        st.metric("Loan-to-Income Ratio", f"{financial.get('lti_ratio', 'N/A'):.3f}")
        st.metric("LTI Percentage", f"{financial.get('loan_to_income_percentage', 'N/A'):.1f}%")

    st.markdown(f"**📋 Monthly Payment Estimate:** ${financial.get('monthly_payment_estimate', 'N/A'):,.2f}")

    st.divider()


def display_recommended_actions(actions: list):
    """Display recommended actions"""
    st.subheader("✨ Recommended Actions")

    if not actions:
        st.info("No recommended actions at this time")
        return

    for i, action in enumerate(actions, 1):
        st.write(f"{i}. {action}")

    st.divider()


def display_loan_status(analysis: Dict[str, Any]):
    """Display comprehensive loan application status"""
    st.header("📋 Loan Application Status & Analysis")

    applicant_id = analysis.get('applicant_id', 'Unknown')
    st.info(f"🔗 **Applicant ID**: {applicant_id}")

    # Tab interface for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Decision",
        "Applicant Profile",
        "Financial",
        "Factors",
        "Actions"
    ])

    decision = analysis.get('decision', {})
    profile = analysis.get('applicant_profile', {})
    financial = analysis.get('financial_analysis', {})

    with tab1:
        display_loan_decision(decision)

    with tab2:
        display_applicant_profile(profile)

    with tab3:
        display_financial_analysis(financial)

    with tab4:
        factors = decision.get('key_factors', {})
        if factors:
            display_decision_factors(factors)
        else:
            st.info("No decision factors available")

    with tab5:
        actions = decision.get('recommended_actions', [])
        if actions:
            display_recommended_actions(actions)
        else:
            st.info("No recommended actions at this time")


# ============================================================================
# Main UI Components
# ============================================================================

def render_header():
    """Render page header"""
    st.title("🏦 AI Loan Application Assistant")
    st.markdown("*Powered by Advanced Agent Analysis & LLM*")


def render_sidebar():
    """Render sidebar with controls"""
    with st.sidebar:
        st.header("🎮 Controls")

        # Applicant ID Input
        applicant_id = st.text_input(
            "Enter Applicant ID",
            placeholder="APP-2024-001",
            key="applicant_id_input"
        )

        # Analyze Button
        if st.button("🔍 Analyze Application", use_container_width=True, type="primary"):
            if applicant_id.strip():
                with st.spinner("🔄 Analyzing application..."):
                    analysis = get_agent_analysis(applicant_id.strip())

                    if analysis.get('status') == 'success':
                        st.session_state.agent_analysis = analysis
                        st.session_state.applicant_id = applicant_id.strip()
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    else:
                        st.error(f"❌ {analysis.get('error', 'Analysis failed')}")
            else:
                st.warning("⚠️ Please enter an Applicant ID")

        st.divider()

        # Display Stats
        st.subheader("📊 Analysis Stats")
        if st.session_state.agent_analysis:
            decision = st.session_state.agent_analysis.get('decision', {})
            st.metric("Classification", decision.get('classification', 'N/A'))
            st.metric("Risk Score", f"{decision.get('risk_score', 'N/A')}/100")
            st.metric("Confidence", f"{decision.get('confidence_level', 'N/A')}%")
        else:
            st.info("No analysis loaded yet")

        st.divider()

        # Raw JSON Toggle
        st.session_state.show_raw_json = st.checkbox(
            "📋 Show Raw JSON",
            value=st.session_state.show_raw_json
        )

        # Clear Button
        if st.button("🔄 Clear Analysis", use_container_width=True):
            st.session_state.agent_analysis = None
            st.session_state.applicant_id = None
            st.rerun()


def render_main_content():
    """Render main content area"""

    if not st.session_state.agent_analysis:
        st.info("👈 Enter an Applicant ID in the sidebar to analyze their application")

        # Display instructions
        with st.expander("📖 How to Use This Tool", expanded=True):
            st.markdown("""
            ### Steps:
            1. **Enter Applicant ID** - Use format like `APP-2024-001`
            2. **Click "Analyze Application"** - System will fetch and analyze the applicant
            3. **Review Results** - See decision, profile, financial data, and recommendations

            ### Data Displayed:
            - 👤 **Applicant Profile**: Income Stability Score, Employment Risk, Demographics
            - 🎯 **Loan Decision**: Classification (Approve/Reject/Review), Risk Score, Confidence
            - 💰 **Financial Analysis**: DTI, LTI ratios, monthly payment estimate
            - 📊 **Decision Factors**: Credit score, DTI ratio, income stability, employment risk
            - ✨ **Recommended Actions**: Next steps based on decision
            """)
        return

    # Display comprehensive analysis
    analysis = st.session_state.agent_analysis

    if analysis.get('status') == 'error':
        st.error(f"❌ Error: {analysis.get('error', 'Unknown error')}")
        return

    # Main analysis display
    display_loan_status(analysis)

    # Raw JSON section
    if st.session_state.show_raw_json:
        st.divider()
        st.subheader("📋 Raw Response JSON")
        st.json(analysis)


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main application flow"""
    render_header()
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()
