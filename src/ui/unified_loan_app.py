#!/usr/bin/env python3

"""
Unified Loan Application & AI Assistant
Combines loan application form submission with AI-powered loan analysis
Single integrated interface for complete loan lifecycle
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
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
    page_title="🏦 Loan Application Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .form-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .analysis-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state"""
    if "current_form" not in st.session_state:
        st.session_state.current_form = {
            'applicant_id': '',
            'age': 30,
            'income': 50000,
            'employment_type': '',
            'credit_score': 700,
            'loan_amount': 100000,
            'tenure': 60,
            'liabilities': 0,
            'location': '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    if "applications" not in st.session_state:
        st.session_state.applications = []
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None
    if "search_applicant_id" not in st.session_state:
        st.session_state.search_applicant_id = ''
    if "api_client" not in st.session_state:
        st.session_state.api_client = LoanAPIClient()
    if "tab_selection" not in st.session_state:
        st.session_state.tab_selection = 'submit_application'


init_session_state()

# ============================================================================
# Helper Functions
# ============================================================================

def submit_application_to_api(form_data: Dict) -> Dict[str, Any]:
    """Submit form data to API"""
    try:
        api_request = {
            "applicant": {
                "applicant_id": form_data['applicant_id'],
                "age": int(form_data['age']),
                "income": float(form_data['income']),
                "employment_type": form_data['employment_type'],
                "location": form_data['location']
            },
            "loan_details": {
                "credit_score": int(form_data['credit_score']),
                "loan_amount": float(form_data['loan_amount']),
                "tenure": int(form_data['tenure']),
                "liabilities": float(form_data['liabilities'])
            },
            "timestamp": form_data['timestamp']
        }

        response = requests.post(
            f"{API_BASE_URL}/api/v1/applications",
            json=api_request,
            timeout=10
        )

        if response.status_code == 201:
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "error": f"API error: {response.status_code}"}

    except requests.ConnectionError:
        return {"status": "error", "error": "Cannot connect to API server at http://localhost:8000"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def fetch_and_analyze_applicant(applicant_id: str) -> Dict[str, Any]:
    """Fetch applicant and get AI analysis"""
    try:
        if not applicant_id or applicant_id.strip() == '':
            return {"status": "error", "error": "Please enter an Applicant ID"}

        # First, fetch applicant profile
        profile_response = requests.get(
            f"{API_BASE_URL}/api/v1/applicants/{applicant_id}",
            timeout=10
        )

        if profile_response.status_code != 200:
            return {"status": "error", "error": f"Applicant {applicant_id} not found"}

        applicant_data = profile_response.json()

        # Then, get AI analysis
        analysis_response = requests.get(
            f"{API_BASE_URL}/api/v1/analyze/{applicant_id}",
            timeout=30
        )

        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()
            return {
                "status": "success",
                "applicant": applicant_data,
                "analysis": analysis_data
            }
        else:
            return {
                "status": "partial",
                "applicant": applicant_data,
                "analysis": None,
                "error": "Could not fetch AI analysis"
            }

    except requests.ConnectionError:
        return {"status": "error", "error": "Cannot connect to API server"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def load_applicant_to_form(applicant_data: Dict):
    """Load applicant data into form for editing"""
    st.session_state.current_form = {
        'applicant_id': applicant_data.get('applicant_id', ''),
        'age': applicant_data.get('age', 30),
        'income': applicant_data.get('income', 50000),
        'employment_type': applicant_data.get('employment_type', ''),
        'credit_score': applicant_data.get('credit_score', 700),
        'loan_amount': applicant_data.get('loan_amount', 100000),
        'tenure': applicant_data.get('tenure_months', 60),
        'liabilities': applicant_data.get('existing_liabilities', 0),
        'location': applicant_data.get('location', ''),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.success("✅ Applicant data loaded into form for editing")


# ============================================================================
# UI Components - Header
# ============================================================================

def render_header():
    """Render page header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Loan Application Assistant</h1>
        <p>Submit loan applications or analyze existing applications with AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# UI Components - Tab 1: Submit New Application
# ============================================================================

def render_submit_application_tab():
    """Render tab for submitting new applications"""
    st.markdown("### 📝 Submit New Loan Application")

    col1, col2 = st.columns(2)

    # Applicant Information Section
    with col1:
        st.markdown('<div class="form-section"><h4>👤 Applicant Information</h4></div>', unsafe_allow_html=True)

        applicant_id = st.text_input(
            "Applicant ID *",
            value=st.session_state.current_form['applicant_id'],
            placeholder="APP-2024-001001",
            key="submit_applicant_id"
        )
        st.session_state.current_form['applicant_id'] = applicant_id

        location = st.text_input(
            "Location *",
            value=st.session_state.current_form['location'],
            placeholder="New York, NY",
            key="submit_location"
        )
        st.session_state.current_form['location'] = location

    with col2:
        st.markdown('<div class="form-section"><h4>📅 Application Timestamp</h4></div>', unsafe_allow_html=True)

        app_date = st.date_input(
            "Application Date",
            value=datetime.strptime(st.session_state.current_form['timestamp'][:10], '%Y-%m-%d').date()
        )

        app_time = st.time_input(
            "Application Time",
            value=datetime.strptime(st.session_state.current_form['timestamp'], '%Y-%m-%d %H:%M:%S').time()
        )

        timestamp_str = f"{app_date.strftime('%Y-%m-%d')} {app_time.strftime('%H:%M:%S')}"
        st.session_state.current_form['timestamp'] = timestamp_str

    # Applicant Profile Section
    st.markdown('<div class="form-section"><h4>📊 Applicant Profile</h4></div>', unsafe_allow_html=True)

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        age = st.number_input(
            "Age (years) *",
            min_value=18,
            max_value=100,
            value=st.session_state.current_form['age'],
            key="submit_age"
        )
        st.session_state.current_form['age'] = age

    with col_p2:
        income = st.number_input(
            "Annual Income ($) *",
            min_value=0,
            step=5000,
            value=st.session_state.current_form['income'],
            key="submit_income"
        )
        st.session_state.current_form['income'] = income

    with col_p3:
        employment_type = st.selectbox(
            "Employment Type *",
            options=["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"],
            index=0 if not st.session_state.current_form['employment_type'] else
                  ["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"].index(st.session_state.current_form['employment_type']),
            key="submit_employment"
        )
        st.session_state.current_form['employment_type'] = employment_type

    # Credit & Loan Details Section
    st.markdown('<div class="form-section"><h4>💰 Credit & Loan Details</h4></div>', unsafe_allow_html=True)

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        credit_score = st.number_input(
            "Credit Score *",
            min_value=300,
            max_value=850,
            value=st.session_state.current_form['credit_score'],
            key="submit_credit_score"
        )
        st.session_state.current_form['credit_score'] = credit_score

        if credit_score >= 750:
            st.success("✅ Excellent (750+)")
        elif credit_score >= 700:
            st.info("ℹ️ Good (700-749)")
        elif credit_score >= 650:
            st.warning("⚠️ Fair (650-699)")
        else:
            st.error("❌ Poor (<650)")

    with col_c2:
        loan_amount = st.number_input(
            "Loan Amount ($) *",
            min_value=1000,
            step=5000,
            value=st.session_state.current_form['loan_amount'],
            key="submit_loan_amount"
        )
        st.session_state.current_form['loan_amount'] = loan_amount

    with col_c3:
        tenure = st.number_input(
            "Loan Tenure (months) *",
            min_value=3,
            max_value=360,
            value=st.session_state.current_form['tenure'],
            key="submit_tenure"
        )
        st.session_state.current_form['tenure'] = tenure

        if tenure > 0:
            monthly_payment = loan_amount / tenure
            st.metric("Monthly Payment", f"${monthly_payment:,.2f}")

    # Financial Obligations Section
    st.markdown('<div class="form-section"><h4>📈 Financial Obligations</h4></div>', unsafe_allow_html=True)

    liabilities = st.number_input(
        "Existing Liabilities ($) *",
        min_value=0,
        step=1000,
        value=st.session_state.current_form['liabilities'],
        key="submit_liabilities"
    )
    st.session_state.current_form['liabilities'] = liabilities

    # Financial Summary
    st.markdown("**Financial Metrics:**")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        total_debt = liabilities + loan_amount
        st.metric("Total Debt", f"${total_debt:,.0f}")

    with col_f2:
        dti = ((liabilities + loan_amount) / max(income, 1)) * 100
        st.metric("Debt-to-Income", f"{dti:.1f}%")

    with col_f3:
        lti = (loan_amount / max(income, 1)) * 100
        st.metric("Loan-to-Income", f"{lti:.1f}%")

    # Application Summary
    st.markdown('<div class="form-section"><h4>✓ Application Summary</h4></div>', unsafe_allow_html=True)

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.markdown("**Personal Information**")
        st.write(f"🆔 ID: {applicant_id if applicant_id else '⚠️ Required'}")
        st.write(f"📍 Location: {location if location else '⚠️ Required'}")
        st.write(f"👤 Age: {age} years")
        st.write(f"💼 Employment: {employment_type if employment_type else '⚠️ Required'}")

    with summary_col2:
        st.markdown("**Loan Information**")
        st.write(f"💵 Loan Amount: ${loan_amount:,.0f}")
        st.write(f"📅 Tenure: {tenure} months")
        if tenure > 0:
            st.write(f"📊 Monthly Payment: ${loan_amount/tenure:,.2f}")
        st.write(f"📆 Application: {timestamp_str}")

    with summary_col3:
        st.markdown("**Credit & Financial**")
        st.write(f"📈 Credit Score: {credit_score}")
        st.write(f"💵 Annual Income: ${income:,.0f}")
        st.write(f"📉 Liabilities: ${liabilities:,.0f}")
        st.write(f"⚖️ DTI: {dti:.1f}%")

    # Submit Buttons
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("✅ Submit Application", use_container_width=True, type="primary"):
            if not applicant_id or not employment_type or not location:
                st.error("❌ Please fill in all required fields")
            else:
                with st.spinner("📤 Submitting application..."):
                    result = submit_application_to_api(st.session_state.current_form)

                    if result['status'] == 'success':
                        response_data = result['data']
                        st.session_state.applications.append(st.session_state.current_form.copy())

                        st.markdown(f"""
                        <div class="success-message">
                        ✅ <strong>Application submitted successfully!</strong><br>
                        Application ID: <strong>{response_data.get('application_id', 'N/A')}</strong><br>
                        Status: <strong>{response_data.get('status', 'N/A')}</strong><br>
                        Risk Score: <strong>{response_data.get('risk_assessment', {}).get('risk_score', 'N/A')}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                        st.info("💡 Switch to 'Analyze Application' tab to see AI-powered loan analysis!")

                        # Auto-populate the analysis tab with this applicant
                        st.session_state.search_applicant_id = applicant_id
                        st.session_state.tab_selection = 'analyze_application'

                    else:
                        st.error(f"❌ Submission failed: {result.get('error', 'Unknown error')}")

    with col_btn2:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.current_form = {
                'applicant_id': '',
                'age': 30,
                'income': 50000,
                'employment_type': '',
                'credit_score': 700,
                'loan_amount': 100000,
                'tenure': 60,
                'liabilities': 0,
                'location': '',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.rerun()

    with col_btn3:
        if st.button("📊 View History", use_container_width=True):
            st.session_state.show_history = not st.session_state.get('show_history', False)
            st.rerun()


# ============================================================================
# UI Components - Tab 2: Analyze Application
# ============================================================================

def render_analyze_application_tab():
    """Render tab for analyzing existing applications"""
    st.markdown("### 🔍 Analyze Loan Application")

    # Search Section
    st.markdown("**Enter Applicant ID to fetch and analyze:**")
    col_search1, col_search2, col_search3 = st.columns([3, 1, 1])

    with col_search1:
        search_id = st.text_input(
            "Applicant ID",
            value=st.session_state.search_applicant_id,
            placeholder="APP-2024-001001",
            label_visibility="collapsed"
        )
        st.session_state.search_applicant_id = search_id

    with col_search2:
        analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")

    with col_search3:
        clear_button = st.button("✖️ Clear", use_container_width=True)

    if clear_button:
        st.session_state.search_applicant_id = ''
        st.session_state.current_analysis = None
        st.rerun()

    # Perform analysis
    if analyze_button:
        if not search_id:
            st.error("❌ Please enter an Applicant ID")
        else:
            with st.spinner(f"🔄 Fetching and analyzing {search_id}..."):
                result = fetch_and_analyze_applicant(search_id)

                if result['status'] == 'success':
                    st.session_state.current_analysis = result
                    st.success(f"✅ Analysis complete for {search_id}")

                elif result['status'] == 'partial':
                    st.session_state.current_analysis = result
                    st.warning("⚠️ Applicant found but AI analysis unavailable")

                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Display Analysis Results
    if st.session_state.current_analysis:
        result = st.session_state.current_analysis

        if result['status'] in ['success', 'partial']:
            applicant = result.get('applicant', {})
            analysis = result.get('analysis', {})

            # Applicant Details Section
            st.markdown("---")
            st.subheader("👤 Applicant Details")

            col_detail1, col_detail2, col_detail3, col_detail4 = st.columns(4)

            with col_detail1:
                st.metric("📆 ID", applicant.get('applicant_id', 'N/A'))

            with col_detail2:
                st.metric("👤 Age", f"{applicant.get('age', 'N/A')} years")

            with col_detail3:
                st.metric("💼 Employment", applicant.get('employment_type', 'N/A'))

            with col_detail4:
                st.metric("📍 Location", applicant.get('location', 'N/A'))

            # Financial Details
            st.markdown("---")
            st.subheader("💰 Financial Details")

            col_fin1, col_fin2, col_fin3, col_fin4 = st.columns(4)

            with col_fin1:
                st.metric("💵 Annual Income", f"${applicant.get('income', 0):,.0f}")

            with col_fin2:
                st.metric("📊 Credit Score", applicant.get('credit_score', 'N/A'))

            with col_fin3:
                st.metric("💰 Loan Amount", f"${applicant.get('loan_amount', 0):,.0f}")

            with col_fin4:
                st.metric("📅 Tenure", f"{applicant.get('tenure_months', 'N/A')} months")

            # AI Analysis Section
            if analysis:
                st.markdown("---")
                st.subheader("🤖 AI Analysis & Decision")

                # Tabs for different analysis views
                analysis_tabs = st.tabs([
                    "📋 Decision",
                    "👤 Profile",
                    "💰 Financial",
                    "🎯 Factors",
                    "✅ Actions"
                ])

                with analysis_tabs[0]:  # Decision Tab
                    decision = analysis.get('decision', {})
                    classification = decision.get('classification', 'N/A')

                    if classification == 'APPROVE':
                        st.success(f"✅ DECISION: APPROVE")
                    elif classification == 'REJECT':
                        st.error(f"❌ DECISION: REJECT")
                    else:
                        st.warning(f"⚠️ DECISION: {classification}")

                    col_dec1, col_dec2, col_dec3 = st.columns(3)

                    with col_dec1:
                        risk_score = decision.get('risk_score', 0)
                        st.metric("📊 Risk Score", f"{risk_score}/100")

                    with col_dec2:
                        confidence = decision.get('confidence_level', 0)
                        st.metric("🎯 Confidence", f"{confidence}%")

                    with col_dec3:
                        reason = decision.get('classification_reason', '')
                        st.metric("💡 Reason", reason[:30] + "..." if len(reason) > 30 else reason)

                    if decision.get('explanation'):
                        st.markdown("**Explanation:**")
                        st.write(decision['explanation'])

                with analysis_tabs[1]:  # Profile Tab
                    profile = analysis.get('applicant_profile', {})
                    st.markdown("**Income Stability & Employment Analysis:**")

                    col_prof1, col_prof2 = st.columns(2)

                    with col_prof1:
                        stability = profile.get('income_stability_score', 0)
                        if stability >= 80:
                            st.success(f"✅ Income Stability: {stability}/100")
                        elif stability >= 60:
                            st.info(f"ℹ️ Income Stability: {stability}/100")
                        else:
                            st.warning(f"⚠️ Income Stability: {stability}/100")

                    with col_prof2:
                        employment_risk = profile.get('employment_risk_score', 0)
                        if employment_risk <= 40:
                            st.success(f"✅ Employment Risk: {employment_risk}/100 (Low)")
                        elif employment_risk <= 70:
                            st.info(f"ℹ️ Employment Risk: {employment_risk}/100 (Moderate)")
                        else:
                            st.warning(f"⚠️ Employment Risk: {employment_risk}/100 (High)")

                    st.write(f"**Credit Category:** {profile.get('credit_category', 'N/A')}")
                    st.write(f"**Application Status:** {profile.get('application_status', 'N/A')}")

                with analysis_tabs[2]:  # Financial Tab
                    financial = analysis.get('financial_analysis', {})
                    st.markdown("**Debt & Risk Metrics:**")

                    col_financial1, col_financial2, col_financial3 = st.columns(3)

                    with col_financial1:
                        dti = financial.get('dti_ratio', 0)
                        st.metric("📊 DTI Ratio", f"{dti:.2f}")

                    with col_financial2:
                        lti = financial.get('lti_ratio', 0)
                        st.metric("📈 LTI Ratio", f"{lti:.2f}")

                    with col_financial3:
                        monthly_est = financial.get('monthly_payment_estimate', 0)
                        st.metric("💵 Est. Monthly Payment", f"${monthly_est:,.2f}")

                with analysis_tabs[3]:  # Factors Tab
                    st.markdown("**Key Decision Factors:**")
                    factors = analysis.get('decision', {}).get('key_factors', [])

                    if factors:
                        factors_df = pd.DataFrame([
                            {
                                'Factor': f.get('factor', 'N/A'),
                                'Value': f.get('value', 'N/A'),
                                'Impact': f.get('impact', 'N/A'),
                                'Contribution': f.get('contribution_to_score', 0)
                            }
                            for f in factors
                        ])
                        st.dataframe(factors_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No factors available")

                with analysis_tabs[4]:  # Actions Tab
                    st.markdown("**Recommended Actions:**")
                    actions = analysis.get('decision', {}).get('recommended_actions', [])

                    if actions:
                        for i, action in enumerate(actions, 1):
                            st.markdown(f"{i}. {action}")
                    else:
                        st.info("No specific actions recommended")

            # Load to Form Button
            st.markdown("---")
            col_load1, col_load2 = st.columns(2)

            with col_load1:
                if st.button("📝 Load to Form for Editing", use_container_width=True):
                    load_applicant_to_form(applicant)
                    st.session_state.tab_selection = 'submit_application'
                    st.rerun()

            with col_load2:
                if st.button("📥 Download Analysis (JSON)", use_container_width=True):
                    json_data = json.dumps(result, indent=2)
                    st.download_button(
                        label="Download",
                        data=json_data,
                        file_name=f"analysis_{search_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application"""
    render_header()

    # Create tabs
    tab1, tab2 = st.tabs([
        "📝 Submit Application",
        "🔍 Analyze Application"
    ])

    with tab1:
        render_submit_application_tab()

    with tab2:
        render_analyze_application_tab()

    # Sidebar
    with st.sidebar:
        st.header("📖 Instructions & Help")

        with st.expander("📋 How to Submit Application", expanded=False):
            st.markdown("""
            ### Steps to Submit:
            1. **Fill Required Fields** (*):
               - Applicant ID (format: APP-2024-001001)
               - Age (18-100)
               - Annual Income
               - Employment Type
               - Credit Score (300-850)
               - Loan Amount
               - Tenure (3-360 months)
               - Location

            2. **Review Summary**:
               - Check all details before submitting
               - Financial metrics auto-calculated

            3. **Submit Application**:
               - Click "✅ Submit Application"
               - Application saved to database

            4. **AI Analysis**:
               - Switch to "Analyze Application" tab
               - Enter same Applicant ID
               - View comprehensive AI analysis
            """)

        with st.expander("🔍 How to Analyze Application", expanded=False):
            st.markdown("""
            ### Steps to Analyze:
            1. **Enter Applicant ID**:
               - Use exact ID from submitted application
               - Format: APP-2024-001001

            2. **Click Analyze**:
               - Fetches applicant data from database
               - Runs AI agents for comprehensive analysis
               - Displays results in organized tabs

            3. **View Analysis Tabs**:
               - **Decision**: Classification & Risk Score
               - **Profile**: Income Stability & Employment Risk
               - **Financial**: DTI & LTI Ratios
               - **Factors**: Key decision factors
               - **Actions**: Recommended actions

            4. **Next Steps**:
               - Load to form for editing
               - Download analysis as JSON
               - Submit updated application
            """)

        with st.expander("ℹ️ About This Application", expanded=False):
            st.markdown("""
            **Unified Loan Application Assistant** combines:

            - **📝 Loan Application Form**: Submit comprehensive loan applications
            - **🤖 AI Analysis**: Get intelligent loan analysis with confidence scores
            - **🎯 Decision Support**: Classification (Approve/Reject/Review), risk scores, factors
            - **📊 Financial Analysis**: DTI, LTI, income stability, employment risk
            - **✅ Complete Workflow**: From application to decision in one place

            All data is validated and persisted to the database.
            """)

        with st.expander("🔗 System Status", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                try:
                    response = requests.get(f"{API_BASE_URL}/health", timeout=2)
                    if response.status_code == 200:
                        st.success("✅ API Server")
                    else:
                        st.error("❌ API Server")
                except:
                    st.error("❌ API Server")

            with col2:
                st.info("💾 Database")

            with col3:
                st.info("🔧 Services")

        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown("""
        - [API Status](http://localhost:8000/health)
        - [GitHub](https://github.com/PradeepMaharana/LoanApprovalSystem)
        """)


if __name__ == "__main__":
    main()
