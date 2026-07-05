import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from streamlit_integration import LoanAPIClient

# Configure Streamlit page
st.set_page_config(
    page_title="Loan Approval Chatbot",
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

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .warning-message {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }

    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
    }

    .bot-message {
        background: #f5f5f5;
        border-left: 4px solid #667eea;
    }

    .application-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .input-label {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .summary-table {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions (defined early for use throughout)
def calculate_risk_score(credit_score, liabilities, income, loan_amount, age):
    """Calculate a risk score based on application metrics"""
    score = 100

    # Credit score factor (max -40)
    if credit_score < 600:
        score -= 40
    elif credit_score < 650:
        score -= 30
    elif credit_score < 700:
        score -= 15
    elif credit_score >= 750:
        score += 5

    # Debt-to-income ratio (max -30)
    if income > 0:
        dti = (liabilities + loan_amount) / income
        if dti > 0.6:
            score -= 30
        elif dti > 0.5:
            score -= 20
        elif dti > 0.4:
            score -= 10

    # Age factor (max -15)
    if age < 25 or age > 65:
        score -= 15
    elif age > 60:
        score -= 5

    # Loan-to-income ratio (max -20)
    if income > 0:
        lti = loan_amount / income
        if lti > 5:
            score -= 20
        elif lti > 3:
            score -= 10

    return max(0, min(100, score))


def get_risk_level(risk_score):
    """Determine risk level based on score"""
    if risk_score >= 75:
        return "Very Low Risk 🟢", "#4CAF50"
    elif risk_score >= 60:
        return "Low Risk 🟡", "#8BC34A"
    elif risk_score >= 40:
        return "Moderate Risk 🟠", "#FF9800"
    elif risk_score >= 20:
        return "High Risk 🔴", "#F44336"
    else:
        return "Very High Risk ⛔", "#B71C1C"


def get_applicant_data_from_db(applicant_id):
    """Retrieve applicant and application data from database using API"""
    try:
        api_client = st.session_state.api_client
        applicant_data = api_client.get_applicant_profile(applicant_id)
        return applicant_data
    except Exception as e:
        st.warning(f"⚠️ Could not retrieve data from database: {str(e)}")
        return None


def generate_bot_response(user_input, form_data, risk_score, applicant_id=None):
    """
    Generate contextual bot responses with database-retrieved data when available.

    Args:
        user_input: User's message
        form_data: Form data (from session or loaded from DB)
        risk_score: Calculated risk score
        applicant_id: Applicant ID to fetch live data from database
    """
    user_input_lower = user_input.lower()

    # Try to get live data from database if applicant_id provided
    if applicant_id:
        db_data = get_applicant_data_from_db(applicant_id)
        if db_data:
            # Use database data, fallback to form_data if fields missing
            credit_score = db_data.get('credit_score', form_data.get('credit_score'))
            income = db_data.get('income', form_data.get('income'))
            loan_amount = db_data.get('loan_amount', form_data.get('loan_amount'))
            location = db_data.get('location', form_data.get('location'))
            employment_type = db_data.get('employment_type', form_data.get('employment_type'))
            application_status = db_data.get('application_status', 'SUBMITTED')
        else:
            credit_score = form_data.get('credit_score')
            income = form_data.get('income')
            loan_amount = form_data.get('loan_amount')
            location = form_data.get('location')
            employment_type = form_data.get('employment_type')
            application_status = 'SUBMITTED'
    else:
        credit_score = form_data.get('credit_score')
        income = form_data.get('income')
        loan_amount = form_data.get('loan_amount')
        location = form_data.get('location')
        employment_type = form_data.get('employment_type')
        application_status = 'SUBMITTED'

    # Validate data
    if not credit_score or not income or not loan_amount:
        return "❌ Unable to retrieve your application data. Please ensure you have submitted an application or loaded an existing one."

    responses = {
        'approval': f"Based on your profile (Credit Score: {credit_score}, Income: ${income:,.0f}, Location: {location}), your approval chances look {'excellent' if risk_score > 75 else 'good' if risk_score > 60 else 'moderate' if risk_score > 40 else 'challenging'}. Current Status: {application_status}. Our team will review your application within 2-3 business days.",
        'timeline': "Standard loan applications are typically processed within 2-3 business days. We'll send you updates via email and SMS. You can check your status anytime using our search feature.",
        'documents': "You may need to provide: recent pay stubs, tax returns, bank statements, and employment verification. We'll contact you if additional documents are required for your application.",
        'interest': f"Interest rates vary based on your credit score ({credit_score}) and loan details. For your requested loan amount of ${loan_amount:,.0f}, you'll receive a formal quote after initial review.",
        'decline': f"We review each application individually. With your current profile (Employment: {employment_type}, Income: ${income:,.0f}), there's still a good chance of approval. If declined, we can discuss alternatives or improvements.",
        'modify': "You can modify your application up until it's fully approved. Please use the form above to update any information, or search for your existing application to reload it.",
        'status': f"Your current application status is: {application_status}. Loan Amount: ${loan_amount:,.0f}, Credit Score: {credit_score}. Last updated in our database.",
    }

    for keyword, response in responses.items():
        if keyword in user_input_lower:
            return response

    return f"Thank you for your inquiry. 📊 I'm reviewing your application:\n\n**Profile Details:**\n- Loan Amount: ${loan_amount:,.0f}\n- Credit Score: {credit_score}\n- Annual Income: ${income:,.0f}\n- Employment: {employment_type}\n- Location: {location}\n- Status: {application_status}\n- Risk Score: {risk_score:.1f}/100\n\nHow else can I assist you today?"


# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'applications' not in st.session_state:
    st.session_state.applications = []

if 'current_form' not in st.session_state:
    st.session_state.current_form = {
        'applicant_id': '',
        'age': None,
        'income': None,
        'employment_type': '',
        'credit_score': None,
        'loan_amount': None,
        'tenure': None,
        'liabilities': None,
        'location': '',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'show_search' not in st.session_state:
    st.session_state.show_search = False

if 'api_client' not in st.session_state:
    st.session_state.api_client = LoanAPIClient()

# Header
st.markdown("""
<div class="main-header">
    <h1>🏦 Loan Approval Chatbot</h1>
    <p>Interactive AI Assistant for Loan Application Processing</p>
</div>
""", unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📋 Application Form")

    # Applicant Information Section
    st.markdown('<div class="form-section"><h4>👤 Applicant Information</h4></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        applicant_id = st.text_input(
            "Applicant ID",
            value=st.session_state.current_form['applicant_id'],
            placeholder="e.g., APP-2024-001",
            key="applicant_id_input"
        )
        st.session_state.current_form['applicant_id'] = applicant_id

    with col_right:
        location = st.text_input(
            "Location",
            value=st.session_state.current_form['location'],
            placeholder="e.g., New York, NY",
            key="location_input"
        )
        st.session_state.current_form['location'] = location

    # Profile Section
    st.markdown('<div class="form-section"><h4>📊 Applicant Profile</h4></div>', unsafe_allow_html=True)

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=st.session_state.current_form['age'] or 30,
            key="age_input"
        )
        st.session_state.current_form['age'] = age

    with col_p2:
        income = st.number_input(
            "Annual Income ($)",
            min_value=0,
            step=5000,
            value=st.session_state.current_form['income'] or 50000,
            key="income_input"
        )
        st.session_state.current_form['income'] = income

    with col_p3:
        employment_type = st.selectbox(
            "Employment Type",
            options=["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"],
            index=0 if not st.session_state.current_form['employment_type'] else
                  ["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"].index(st.session_state.current_form['employment_type']),
            key="employment_input"
        )
        st.session_state.current_form['employment_type'] = employment_type

    # Credit & Loan Section
    st.markdown('<div class="form-section"><h4>💰 Credit & Loan Details</h4></div>', unsafe_allow_html=True)

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        credit_score = st.number_input(
            "Credit Score",
            min_value=300,
            max_value=850,
            value=st.session_state.current_form['credit_score'] or 700,
            key="credit_input"
        )
        st.session_state.current_form['credit_score'] = credit_score

    with col_c2:
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=1000,
            step=5000,
            value=st.session_state.current_form['loan_amount'] or 100000,
            key="loan_amount_input"
        )
        st.session_state.current_form['loan_amount'] = loan_amount

    with col_c3:
        tenure = st.number_input(
            "Tenure (months)",
            min_value=3,
            max_value=360,
            value=st.session_state.current_form['tenure'] or 60,
            key="tenure_input"
        )
        st.session_state.current_form['tenure'] = tenure

    # Liabilities Section
    st.markdown('<div class="form-section"><h4>📈 Financial Obligations</h4></div>', unsafe_allow_html=True)

    liabilities = st.number_input(
        "Existing Liabilities ($)",
        min_value=0,
        step=1000,
        value=st.session_state.current_form['liabilities'] or 0,
        key="liabilities_input"
    )
    st.session_state.current_form['liabilities'] = liabilities

    # Buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("✅ Submit Application", use_container_width=True, type="primary"):
            if not applicant_id or not employment_type or not location:
                st.markdown(
                    '<div class="error-message">❌ Please fill in all required fields (Applicant ID, Employment Type, Location)</div>',
                    unsafe_allow_html=True
                )
            else:
                application = st.session_state.current_form.copy()
                st.session_state.applications.append(application)

                # Add to chat history
                message = f"New application submitted: {applicant_id} - Loan Amount: ${loan_amount:,.2f}"
                st.session_state.chat_history.append({
                    "role": "user",
                    "message": message,
                    "timestamp": datetime.now().strftime('%H:%M:%S')
                })

                bot_response = f"Application #{applicant_id} received! Processing loan request for ${loan_amount:,.2f} with credit score {credit_score}. Expected decision time: 2-3 business days."
                st.session_state.chat_history.append({
                    "role": "bot",
                    "message": bot_response,
                    "timestamp": datetime.now().strftime('%H:%M:%S')
                })

                st.markdown(
                    '<div class="success-message">✅ Application submitted successfully! Please wait for approval notification.</div>',
                    unsafe_allow_html=True
                )
                st.rerun()

    with col_btn2:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.current_form = {
                'applicant_id': '',
                'age': None,
                'income': None,
                'employment_type': '',
                'credit_score': None,
                'loan_amount': None,
                'tenure': None,
                'liabilities': None,
                'location': '',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.rerun()

    with col_btn3:
        if st.button("📊 View Applications", use_container_width=True):
            st.session_state.show_applications = not st.session_state.get('show_applications', False)

with col2:
    st.markdown("### 📈 Quick Summary")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.metric("Debt-to-Income", f"{(liabilities / max(income, 1) * 100):.1f}%")

    with summary_col2:
        st.metric("Monthly Payment", f"${(loan_amount / max(tenure, 1)):.2f}")

    st.metric("Loan-to-Income", f"{(loan_amount / max(income, 1) * 100):.1f}%")

    # Risk indicator
    st.markdown('<div class="form-section"><h4>⚠️ Risk Assessment</h4></div>', unsafe_allow_html=True)

    risk_score = calculate_risk_score(
        credit_score,
        liabilities,
        income,
        loan_amount,
        age
    )

    risk_level, risk_color = get_risk_level(risk_score)

    st.markdown(f"""
    <div style="background: {risk_color}20; padding: 1rem; border-radius: 8px; border-left: 4px solid {risk_color};">
        <strong>Risk Level: {risk_level}</strong><br>
        Score: {risk_score:.1f}/100
    </div>
    """, unsafe_allow_html=True)

# Chat Interface
st.markdown("---")
st.markdown("### 💬 Application Chat Assistant")

# Info banner
applicant_id = st.session_state.current_form.get('applicant_id')
if applicant_id:
    st.info(f"🔗 **Chat Context**: Using data from Applicant ID: `{applicant_id}` (retrieved from database)")
else:
    st.warning("⚠️ **No Applicant ID**: Please submit or load an application first to use the chat assistant")

# Display chat history
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You ({msg['timestamp']}):</strong><br>
                {msg['message']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>🤖 Loan Assistant ({msg['timestamp']}):</strong><br>
                {msg['message']}
            </div>
            """, unsafe_allow_html=True)

# Chat input
col_chat1, col_chat2 = st.columns([4, 1])

with col_chat1:
    user_input = st.text_input(
        "Ask me anything about your application...",
        placeholder="e.g., What are my chances of approval?",
        key="chat_input"
    )

with col_chat2:
    send_button = st.button("Send", use_container_width=True, key="send_btn")

if send_button and user_input:
    st.session_state.chat_history.append({
        "role": "user",
        "message": user_input,
        "timestamp": datetime.now().strftime('%H:%M:%S')
    })

    # Get applicant ID from current form
    applicant_id = st.session_state.current_form.get('applicant_id')

    # Get data from database if applicant_id exists
    if applicant_id:
        try:
            db_data = get_applicant_data_from_db(applicant_id)
            if db_data:
                # Update form data with database values
                form_data = {
                    'applicant_id': db_data.get('applicant_id', applicant_id),
                    'age': db_data.get('age', st.session_state.current_form['age']),
                    'income': db_data.get('income', st.session_state.current_form['income']),
                    'employment_type': db_data.get('employment_type', st.session_state.current_form['employment_type']),
                    'credit_score': db_data.get('credit_score', st.session_state.current_form['credit_score']),
                    'loan_amount': db_data.get('loan_amount', st.session_state.current_form['loan_amount']),
                    'tenure': db_data.get('tenure_months', st.session_state.current_form['tenure']),
                    'liabilities': db_data.get('existing_liabilities', st.session_state.current_form['liabilities']),
                    'location': db_data.get('location', st.session_state.current_form['location']),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                form_data = st.session_state.current_form
        except Exception as e:
            st.warning(f"⚠️ Error retrieving data: {str(e)}")
            form_data = st.session_state.current_form
    else:
        form_data = st.session_state.current_form

    # Calculate risk score with available data
    credit_score = form_data.get('credit_score') or 700
    liabilities = form_data.get('liabilities') or 0
    income = form_data.get('income') or 50000
    loan_amount = form_data.get('loan_amount') or 100000
    age = form_data.get('age') or 35

    risk_score = calculate_risk_score(
        credit_score,
        liabilities,
        income,
        loan_amount,
        age
    )

    # Generate bot response based on input with database retrieval
    bot_response = generate_bot_response(
        user_input,
        form_data,
        risk_score,
        applicant_id=applicant_id
    )

    st.session_state.chat_history.append({
        "role": "bot",
        "message": bot_response,
        "timestamp": datetime.now().strftime('%H:%M:%S')
    })

    st.rerun()

# Applications History
if st.session_state.get('show_applications', False):
    st.markdown("---")
    st.markdown("### 📋 Application History")

    if st.session_state.applications:
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
    else:
        st.info("No applications submitted yet.")


# Search Section
st.markdown("---")
st.markdown("### 🔍 Search & Retrieve Applicants")

search_tab1, search_tab2 = st.tabs(["Search Applicants", "Database Statistics"])

with search_tab1:
    st.markdown("#### Search Criteria")

    search_col1, search_col2 = st.columns(2)

    with search_col1:
        search_applicant_id = st.text_input(
            "Applicant ID",
            placeholder="e.g., APP-2024-001",
            key="search_app_id"
        )
        search_location = st.text_input(
            "Location",
            placeholder="e.g., New York",
            key="search_location"
        )
        search_employment = st.selectbox(
            "Employment Type",
            options=["", "Salaried", "Self-Employed", "Freelancer", "Business Owner"],
            key="search_employment"
        )

    with search_col2:
        search_age_min = st.number_input(
            "Min Age",
            min_value=18,
            max_value=100,
            value=18,
            key="search_age_min"
        )
        search_age_max = st.number_input(
            "Max Age",
            min_value=18,
            max_value=100,
            value=100,
            key="search_age_max"
        )
        search_credit_min = st.number_input(
            "Min Credit Score",
            min_value=300,
            max_value=850,
            value=300,
            key="search_credit_min"
        )

    search_status = st.selectbox(
        "Application Status",
        options=["", "SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED", "PENDING_DOCUMENTS"],
        key="search_status"
    )

    search_btn_col1, search_btn_col2, search_btn_col3 = st.columns(3)

    with search_btn_col1:
        if st.button("🔎 Search", use_container_width=True, type="primary"):
            with st.spinner("Searching..."):
                api_client = st.session_state.api_client

                search_params = {}
                if search_applicant_id:
                    search_params['applicant_id'] = search_applicant_id
                if search_location:
                    search_params['location'] = search_location
                if search_employment:
                    search_params['employment_type'] = search_employment
                if search_age_min > 18:
                    search_params['age_min'] = search_age_min
                if search_age_max < 100:
                    search_params['age_max'] = search_age_max
                if search_credit_min > 300:
                    search_params['credit_score_min'] = search_credit_min
                if search_status:
                    search_params['application_status'] = search_status

                if not search_params:
                    st.warning("⚠️  Please enter at least one search criterion")
                else:
                    results = api_client.search_applicants(**search_params)

                    if results and results.get('data'):
                        st.session_state.search_results = results['data']
                        st.success(f"✅ Found {results.get('count', 0)} applicant(s)")
                    else:
                        st.session_state.search_results = []
                        st.info("No applicants found matching your criteria")

    with search_btn_col2:
        if st.button("📋 List All", use_container_width=True):
            with st.spinner("Loading..."):
                api_client = st.session_state.api_client
                results = api_client.list_all_applicants(page=1, limit=100)

                if results and results.get('data'):
                    st.session_state.search_results = results['data']
                    st.success(f"✅ Loaded {len(results['data'])} applicant(s)")
                else:
                    st.session_state.search_results = []
                    st.info("No applicants in database")

    # Display search results
    if st.session_state.search_results:
        st.markdown("#### Search Results")

        df_results = pd.DataFrame(st.session_state.search_results)
        display_cols = ['applicant_id', 'age', 'income', 'location', 'employment_type',
                        'credit_score', 'loan_amount', 'application_status']
        available_cols = [col for col in display_cols if col in df_results.columns]

        st.dataframe(
            df_results[available_cols],
            use_container_width=True,
            hide_index=True
        )

        # Load applicant to form for editing
        st.markdown("#### Load to Form")
        selected_app_id = st.selectbox(
            "Select applicant to load into form",
            options=[row['applicant_id'] for row in st.session_state.search_results],
            key="load_app_select"
        )

        if st.button("📝 Load to Form", use_container_width=True):
            selected_row = next(
                (row for row in st.session_state.search_results if row['applicant_id'] == selected_app_id),
                None
            )
            if selected_row:
                st.session_state.current_form = {
                    'applicant_id': selected_row.get('applicant_id', ''),
                    'age': selected_row.get('age'),
                    'income': selected_row.get('income'),
                    'employment_type': selected_row.get('employment_type', ''),
                    'credit_score': selected_row.get('credit_score'),
                    'loan_amount': selected_row.get('loan_amount'),
                    'tenure': None,
                    'liabilities': selected_row.get('existing_liabilities', 0),
                    'location': selected_row.get('location', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                st.success(f"✅ Loaded {selected_app_id} - Scroll up to edit and submit")
                st.rerun()

with search_tab2:
    st.markdown("#### Database Statistics")

    if st.button("📊 Refresh Statistics", use_container_width=True):
        with st.spinner("Loading statistics..."):
            api_client = st.session_state.api_client
            stats = api_client.get_statistics()

            if stats:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Applicants", stats.get('total_applicants', 0))

                with col2:
                    st.metric("Total Applications", stats.get('total_applications', 0))

                with col3:
                    st.metric("Session Applications", len(st.session_state.applications))

                st.markdown("##### Applications by Status")
                if stats.get('applications_by_status'):
                    status_data = stats['applications_by_status']
                    status_df = pd.DataFrame(list(status_data.items()), columns=['Status', 'Count'])
                    st.bar_chart(status_df.set_index('Status'))

                st.markdown("##### Applicants by Employment Type")
                if stats.get('applicants_by_employment'):
                    emp_data = stats['applicants_by_employment']
                    emp_df = pd.DataFrame(list(emp_data.items()), columns=['Employment Type', 'Count'])
                    st.bar_chart(emp_df.set_index('Employment Type'))
            else:
                st.error("❌ Failed to load statistics")
