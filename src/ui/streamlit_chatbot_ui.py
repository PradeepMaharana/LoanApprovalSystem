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

# Additional imports needed for better error handling
logger = None

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
        st.info(f"🔄 Fetching agent analysis for {applicant_id}...")
        response = requests.get(
            f"{API_BASE_URL}/api/v1/analyze/{applicant_id}",
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Agent analysis retrieved successfully")
            return result
        elif response.status_code == 404:
            return {"status": "error", "error": f"Applicant {applicant_id} not found in database"}
        else:
            return {"status": "error", "error": f"API error: {response.status_code}", "details": response.text}

    except requests.Timeout:
        return {"status": "error", "error": "Analysis timeout - request took too long (>30s)"}
    except requests.ConnectionError:
        return {"status": "error", "error": "Failed to connect to API server at http://localhost:8000"}
    except Exception as e:
        return {"status": "error", "error": f"Unexpected error: {str(e)}"}


def display_applicant_profile(profile: Dict[str, Any]):
    """Display applicant profile information from ApplicantProfileAgent"""
    st.subheader("👤 Applicant Profile Analysis")

    # Key Stability Metrics (From ApplicantProfileAgent)
    st.markdown("**📊 Agent Analysis Metrics:**")
    col1, col2 = st.columns(2)

    with col1:
        income_stability = profile.get('income_stability_score', 0)
        # Color code based on score
        if income_stability >= 80:
            st.success(f"✅ Income Stability Score: {income_stability}/100 (Stable)")
        elif income_stability >= 60:
            st.info(f"ℹ️ Income Stability Score: {income_stability}/100 (Moderate)")
        else:
            st.warning(f"⚠️ Income Stability Score: {income_stability}/100 (Low)")

    with col2:
        employment_risk = profile.get('employment_risk_score', 0)
        # Color code based on score (inverted - lower is better)
        if employment_risk <= 30:
            st.success(f"✅ Employment Risk Score: {employment_risk}/100 (Low Risk)")
        elif employment_risk <= 70:
            st.info(f"ℹ️ Employment Risk Score: {employment_risk}/100 (Moderate Risk)")
        else:
            st.warning(f"⚠️ Employment Risk Score: {employment_risk}/100 (High Risk)")

    # Detailed Profile Information
    st.markdown("**📋 Applicant Details:**")
    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.write(f"**Age**: {profile.get('age', 'N/A')} years")
        st.write(f"**Income**: ${profile.get('income', 0):,.0f}/year")
        st.write(f"**Employment**: {profile.get('employment_type', 'N/A')}")

    with col_p2:
        st.write(f"**Credit Score**: {profile.get('credit_score', 'N/A')}")
        st.write(f"**Credit Category**: {profile.get('credit_category', 'N/A')}")
        st.write(f"**Location**: {profile.get('location', 'N/A')}")

    with col_p3:
        st.write(f"**Application Status**: {profile.get('application_status', 'N/A')}")
        st.write(f"**Loan Amount**: ${profile.get('loan_amount', 0):,.0f}")

    st.divider()


def display_loan_decision(decision: Dict[str, Any]):
    """Display loan decision details from LoanDecisionAgent"""
    st.subheader("🎯 Loan Decision Agent Analysis")

    # Decision Classification Banner (from LoanDecisionAgent)
    classification = decision.get('classification', 'N/A')
    if classification == 'APPROVE':
        st.success(f"✅ **DECISION: {classification}**", icon="✅")
    elif classification == 'REJECT':
        st.error(f"❌ **DECISION: {classification}**", icon="❌")
    else:
        st.warning(f"⏳ **DECISION: {classification}**", icon="⏳")

    # Key Decision Metrics (from LoanDecisionAgent)
    st.markdown("**📊 Decision Metrics from LoanDecisionAgent:**")
    col1, col2, col3 = st.columns(3)

    with col1:
        risk_score = decision.get('risk_score', 0)
        st.metric(
            "Risk Score",
            f"{risk_score}/100",
            delta=f"{'✅ Low' if risk_score >= 75 else '⚠️ Moderate' if risk_score >= 40 else '❌ High'}",
            help="Overall risk assessment (0-100, higher is better)"
        )

    with col2:
        confidence = decision.get('confidence_level', 0)
        st.metric(
            "Confidence Level",
            f"{confidence}%",
            delta=f"{'Very High' if confidence >= 90 else 'High' if confidence >= 75 else 'Moderate' if confidence >= 50 else 'Low'}",
            help="Confidence in the decision (0-100%)"
        )

    with col3:
        st.metric(
            "Classification",
            classification,
            help=f"Final decision: {classification}"
        )

    # Detailed Explanation (from LoanDecisionAgent)
    st.markdown("**📝 Decision Explanation:**")
    st.info(decision.get('explanation', 'No explanation available'), icon="ℹ️")

    st.divider()


def display_decision_factors(factors: Dict[str, Any]):
    """Display key decision factors from LoanDecisionAgent"""
    st.subheader("📊 Key Decision Factors from LoanDecisionAgent")

    if not factors:
        st.info("No decision factors available", icon="ℹ️")
        return

    # Create detailed factor analysis
    st.markdown("**Factor Assessment Breakdown:**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Individual Factors:**")
        for factor_key, factor_value in factors.items():
            # Clean up factor name
            factor_name = factor_key.replace('_', ' ').title()

            # Color code based on factor value
            if "strong" in str(factor_value).lower() or "stable" in str(factor_value).lower() or "low" in str(factor_value).lower():
                st.success(f"✅ **{factor_name}**: {factor_value}")
            elif "acceptable" in str(factor_value).lower() or "moderate" in str(factor_value).lower():
                st.info(f"ℹ️ **{factor_name}**: {factor_value}")
            else:
                st.warning(f"⚠️ **{factor_name}**: {factor_value}")

    with col2:
        # Visual representation with table
        st.markdown("**Factor Summary Table:**")
        factors_df = pd.DataFrame([
            {
                "Factor": k.replace('_', ' ').title(),
                "Assessment": str(v),
                "Status": "✅" if "strong" in str(v).lower() or "stable" in str(v).lower() or "low" in str(v).lower()
                         else "ℹ️" if "acceptable" in str(v).lower() or "moderate" in str(v).lower()
                         else "⚠️"
            }
            for k, v in factors.items()
        ])
        st.dataframe(factors_df, use_container_width=True, hide_index=True)

    # Key Insights
    st.markdown("**💡 Factor Insights:**")
    insights = []
    for factor_key, factor_value in factors.items():
        insights.append(f"• {factor_key.replace('_', ' ').title()}: {factor_value}")

    for insight in insights:
        st.write(insight)

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
        st.header("🎮 Chatbot Controls")

        st.markdown("### 📥 Fetch & Analyze")

        # Applicant ID Input
        applicant_id = st.text_input(
            "Enter Applicant ID",
            placeholder="APP-2024-001001",
            key="applicant_id_input",
            help="Enter the Applicant ID from a submitted loan application"
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
                        error_msg = analysis.get('error', 'Analysis failed')
                        st.error(f"❌ {error_msg}")

                        # Provide helpful suggestions
                        if "not found" in error_msg.lower():
                            st.info("💡 **Tip**: Make sure you've submitted the application through the Loan Form at http://localhost:8501")
                        elif "connect" in error_msg.lower():
                            st.warning("⚠️ **API Server**: Make sure the API is running on http://localhost:8000")
            else:
                st.warning("⚠️ Please enter an Applicant ID")

        st.divider()

        # Display Stats
        st.subheader("📊 Current Analysis")
        if st.session_state.agent_analysis:
            try:
                decision = st.session_state.agent_analysis.get('decision', {})
                classification = decision.get('classification', 'N/A')
                risk_score = decision.get('risk_score', 'N/A')
                confidence = decision.get('confidence_level', 'N/A')

                # Color-coded classification metric
                if classification == 'APPROVE':
                    st.metric("✅ Classification", classification)
                elif classification == 'REJECT':
                    st.metric("❌ Classification", classification)
                else:
                    st.metric("⏳ Classification", classification)

                st.metric("📊 Risk Score", f"{risk_score}/100" if risk_score != 'N/A' else risk_score)
                st.metric("💯 Confidence", f"{confidence}%" if confidence != 'N/A' else confidence)

                # Applicant info
                st.divider()
                profile = st.session_state.agent_analysis.get('applicant_profile', {})
                applicant_id_display = st.session_state.applicant_id or profile.get('applicant_id', 'Unknown')
                st.caption(f"📌 Applicant ID: {applicant_id_display}")

            except Exception as e:
                st.error(f"Error displaying stats: {str(e)}")
        else:
            st.info("No analysis loaded yet\n\nEnter an Applicant ID above to get started")

        st.divider()

        # Options
        st.subheader("⚙️ Options")

        st.session_state.show_raw_json = st.checkbox(
            "📋 Show Raw JSON",
            value=st.session_state.show_raw_json,
            help="Display the complete JSON response from agents"
        )

        # Clear Button
        if st.button("🔄 Clear Analysis", use_container_width=True):
            st.session_state.agent_analysis = None
            st.session_state.applicant_id = None
            st.rerun()

        st.divider()

        # Quick Links
        st.subheader("🔗 Quick Links")
        st.markdown("""
        - 🏦 [Loan Form](http://localhost:8501)
        - 📊 [API Status](http://localhost:8000/health)
        - 📖 [Documentation](https://github.com/PradeepMaharana/LoanApprovalSystem)
        """)


def render_main_content():
    """Render main content area"""

    if not st.session_state.agent_analysis:
        # Main welcome message
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <h2>👈 Ready to Analyze</h2>
            <p style="font-size: 1.1rem; color: #666;">
                Enter an Applicant ID in the sidebar to analyze their loan application
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Display instructions
        with st.expander("📖 How to Use This Tool", expanded=True):
            st.markdown("""
            ### 🚀 Getting Started:

            **Step 1: Get an Applicant ID**
            1. Go to the [Loan Application Form](http://localhost:8501)
            2. Fill in all required fields and submit
            3. Copy the Applicant ID from the success message

            **Step 2: Analyze in Chatbot**
            1. Enter the Applicant ID in the sidebar text field
            2. Click "🔍 Analyze Application" button
            3. Wait for analysis to complete

            **Step 3: Review Results**
            The analysis displays across 5 tabs:

            - **Decision**: Approval decision + Risk Score + Confidence + Explanation
            - **Applicant Profile**: Income Stability Score + Employment Risk Score + Demographics
            - **Financial**: DTI/LTI Ratios + Monthly Payment
            - **Decision Factors**: Breakdown of factors used in decision
            - **Recommended Actions**: Next steps based on decision

            ### ℹ️ About This Tool:
            This chatbot integrates three specialized agents:
            - **ApplicantProfileAgent**: Income Stability Score + Employment Risk Score
            - **FinancialRiskAgent**: DTI + LTI calculations
            - **LoanDecisionAgent**: Classification + Risk Score + Confidence + Explanation

            ### 💡 Tips:
            - Check "Show Raw JSON" to see the complete agent response
            - Use the Quick Links sidebar to navigate to other tools
            - Refresh the page if you encounter issues
            """)

        # Status check section
        st.markdown("---")
        st.subheader("🔍 System Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    st.success("✅ API Server")
                else:
                    st.error("❌ API Server")
            except:
                st.error("❌ API Server")

        with col2:
            st.info("💾 Database")

        with col3:
            st.success("✅ Chatbot UI")

        return

    # Display comprehensive analysis
    analysis = st.session_state.agent_analysis

    if analysis.get('status') == 'error':
        st.error(f"❌ Error: {analysis.get('error', 'Unknown error')}")
        if analysis.get('details'):
            st.info(f"📋 Details: {analysis.get('details')}")
        return

    # Main analysis display
    display_loan_status(analysis)

    # Agent Output Data Section
    st.divider()
    st.subheader("🤖 Agent Analysis Output Data")

    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.show_raw_json:
            st.info("Raw JSON output shown below")
        else:
            if st.button("📋 Show Raw JSON Data", use_container_width=True):
                st.session_state.show_raw_json = True
                st.rerun()

    with col2:
        if st.session_state.show_raw_json:
            if st.button("🙈 Hide Raw JSON", use_container_width=True):
                st.session_state.show_raw_json = False
                st.rerun()

    # Raw JSON section
    if st.session_state.show_raw_json:
        st.markdown("**Complete Agent Response (JSON)**")
        st.json(analysis)

        # Export option
        json_str = json.dumps(analysis, indent=2, default=str)
        st.download_button(
            label="📥 Download Analysis as JSON",
            data=json_str,
            file_name=f"agent_analysis_{st.session_state.applicant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


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
