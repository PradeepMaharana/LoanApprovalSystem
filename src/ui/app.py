#!/usr/bin/env python3

"""
Loan Application Form - Enhanced Streamlit UI
Complete form for submitting loan applications with real-time validation
and database persistence via FastAPI backend
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import sys
import requests

sys.path.insert(0, str(Path(__file__).parent))
from streamlit_integration import LoanAPIClient

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="🏦 Loan Application Form",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI/UX
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

    .summary-table {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
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
    if "last_submission" not in st.session_state:
        st.session_state.last_submission = None
    if "api_client" not in st.session_state:
        st.session_state.api_client = LoanAPIClient()


init_session_state()

# ============================================================================
# Helper Functions
# ============================================================================

def submit_to_api(form_data):
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


# ============================================================================
# Main Application
# ============================================================================

def render_header():
    """Render page header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Loan Application Form</h1>
        <p>Submit your loan application with comprehensive financial information</p>
    </div>
    """, unsafe_allow_html=True)


def render_form():
    """Render the loan application form"""
    st.markdown("### 📝 Application Details")

    col1, col2 = st.columns(2)

    # =========== Applicant Information Section ===========
    with col1:
        st.markdown('<div class="form-section"><h4>👤 Applicant Information</h4></div>', unsafe_allow_html=True)

        applicant_id = st.text_input(
            "Applicant ID *",
            value=st.session_state.current_form['applicant_id'],
            placeholder="APP-2024-001001",
            key="applicant_id"
        )
        st.session_state.current_form['applicant_id'] = applicant_id

        location = st.text_input(
            "Location *",
            value=st.session_state.current_form['location'],
            placeholder="New York, NY",
            key="location"
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

    # =========== Applicant Profile Section ===========
    st.markdown('<div class="form-section"><h4>📊 Applicant Profile</h4></div>', unsafe_allow_html=True)

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        age = st.number_input(
            "Age (years) *",
            min_value=18,
            max_value=100,
            value=st.session_state.current_form['age'],
            key="age"
        )
        st.session_state.current_form['age'] = age

    with col_p2:
        income = st.number_input(
            "Annual Income ($) *",
            min_value=0,
            step=5000,
            value=st.session_state.current_form['income'],
            key="income"
        )
        st.session_state.current_form['income'] = income

    with col_p3:
        employment_type = st.selectbox(
            "Employment Type *",
            options=["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"],
            index=0 if not st.session_state.current_form['employment_type'] else
                  ["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"].index(st.session_state.current_form['employment_type']),
            key="employment_type"
        )
        st.session_state.current_form['employment_type'] = employment_type

    # =========== Credit & Loan Details Section ===========
    st.markdown('<div class="form-section"><h4>💰 Credit & Loan Details</h4></div>', unsafe_allow_html=True)

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        credit_score = st.number_input(
            "Credit Score *",
            min_value=300,
            max_value=850,
            value=st.session_state.current_form['credit_score'],
            key="credit_score"
        )
        st.session_state.current_form['credit_score'] = credit_score

        # Credit score indicator
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
            key="loan_amount"
        )
        st.session_state.current_form['loan_amount'] = loan_amount

    with col_c3:
        tenure = st.number_input(
            "Loan Tenure (months) *",
            min_value=3,
            max_value=360,
            value=st.session_state.current_form['tenure'],
            key="tenure"
        )
        st.session_state.current_form['tenure'] = tenure

        # Monthly payment calculation
        if tenure > 0:
            monthly_payment = loan_amount / tenure
            st.metric("Monthly Payment", f"${monthly_payment:,.2f}")

    # =========== Financial Obligations Section ===========
    st.markdown('<div class="form-section"><h4>📈 Financial Obligations</h4></div>', unsafe_allow_html=True)

    liabilities = st.number_input(
        "Existing Liabilities ($) *",
        min_value=0,
        step=1000,
        value=st.session_state.current_form['liabilities'],
        key="liabilities"
    )
    st.session_state.current_form['liabilities'] = liabilities

    # Financial summary
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

    # =========== Application Summary ===========
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
        st.write(f"💰 Loan Amount: ${loan_amount:,.0f}")
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

    # =========== Buttons ===========
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("✅ Submit Application", use_container_width=True, type="primary"):
            # Validate required fields
            if not applicant_id or not employment_type or not location:
                st.error("❌ Please fill in all required fields")
            else:
                with st.spinner("📤 Submitting application..."):
                    result = submit_to_api(st.session_state.current_form)

                    if result['status'] == 'success':
                        response_data = result['data']
                        st.session_state.applications.append(st.session_state.current_form.copy())
                        st.session_state.last_submission = response_data

                        st.markdown(f"""
                        <div class="success-message">
                        ✅ <strong>Application submitted successfully!</strong><br>
                        Application ID: <strong>{response_data.get('application_id', 'N/A')}</strong><br>
                        Status: <strong>{response_data.get('status', 'N/A')}</strong><br>
                        Risk Score: <strong>{response_data.get('risk_assessment', {}).get('risk_score', 'N/A')}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                        st.success("💬 Go to Chatbot UI at http://localhost:8503 and enter your Applicant ID to analyze this application!")

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


def render_history():
    """Render application history"""
    if st.session_state.get('show_history', False) and st.session_state.applications:
        st.markdown("---")
        st.subheader("📋 Application History")

        df_apps = pd.DataFrame(st.session_state.applications)
        display_df = df_apps[['applicant_id', 'age', 'income', 'credit_score', 'loan_amount', 'tenure', 'location', 'timestamp']].copy()
        display_df.columns = ['Applicant ID', 'Age', 'Income', 'Credit Score', 'Loan Amount', 'Tenure (mo)', 'Location', 'Timestamp']

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Export option
        csv = df_apps.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def render_instructions():
    """Render instructions"""
    with st.sidebar:
        st.header("📖 Instructions")

        with st.expander("How to Submit Application", expanded=False):
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
               - Financial metrics are calculated automatically

            3. **Submit Application**:
               - Click "✅ Submit Application"
               - Application is saved to database

            4. **Analyze in Chatbot**:
               - Go to http://localhost:8503
               - Enter your Applicant ID
               - Click "Analyze Application"
               - View comprehensive agent analysis

            ### Tips:
            - All fields marked with * are required
            - Credit score range: 300-850
            - DTI should ideally be < 43%
            - Monthly payment is auto-calculated
            """)

        with st.expander("About This Form", expanded=False):
            st.markdown("""
            This form collects comprehensive loan application information:

            **Applicant Profile**:
            - Personal demographics
            - Income information
            - Employment details

            **Loan Details**:
            - Requested loan amount
            - Repayment tenure
            - Credit score

            **Financial Status**:
            - Existing liabilities
            - Debt-to-income ratio
            - Loan-to-income ratio

            All data is validated and persisted to the database via FastAPI backend.
            """)

        with st.expander("System Status", expanded=False):
            st.subheader("🔍 Service Health")

            col1, col2 = st.columns(2)

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

        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown("""
        - [Chatbot UI](http://localhost:8503)
        - [API Status](http://localhost:8000/health)
        - [GitHub](https://github.com/PradeepMaharana/LoanApprovalSystem)
        """)


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application"""
    render_header()
    render_form()
    render_history()
    render_instructions()


if __name__ == "__main__":
    main()
