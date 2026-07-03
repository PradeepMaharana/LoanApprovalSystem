"""
Streamlit integration module for API client
Provides helper functions to interact with FastAPI backend from Streamlit frontend
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LoanAPIClient:
    """Client for interacting with Loan Approval API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Is it running on http://localhost:8000?")
            return None
        except requests.exceptions.Timeout:
            st.error("❌ API request timed out. Please try again.")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API Error: {e.response.status_code}")
            return None
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"API Error: {str(e)}")
            return None

    def submit_application(self, app_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Submit loan application"""
        return self._make_request("POST", "/applications", data=app_data)

    def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get application details"""
        return self._make_request("GET", f"/applications/{application_id}")

    def list_applications(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """List all applications with pagination"""
        params = {
            "page": page,
            "page_size": page_size,
        }
        if status:
            params["status_filter"] = status

        return self._make_request("GET", "/applications", params=params)

    def validate_application(self, app_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate application without submitting"""
        return self._make_request("POST", "/validate-application", data=app_data)

    def send_chat_message(self, chat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send chat message"""
        return self._make_request("POST", "/chat", data=chat_data)

    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


# Streamlit helper functions
@st.cache_resource
def get_api_client() -> LoanAPIClient:
    """Get cached API client instance"""
    return LoanAPIClient()


def format_application_response(response: Dict[str, Any]) -> str:
    """Format application response for display"""
    if not response:
        return "Error: Unable to process application"

    status = response.get("status", "UNKNOWN")
    app_id = response.get("application_id", "N/A")
    risk_level = response.get("risk_assessment", {}).get("risk_level", "N/A")
    message = response.get("message", "")

    return f"""
    **Application ID:** {app_id}
    **Status:** {status}
    **Risk Level:** {risk_level}
    **Message:** {message}
    """


def display_risk_assessment(risk_data: Dict[str, Any]) -> None:
    """Display risk assessment in Streamlit"""
    if not risk_data:
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Risk Score",
            f"{risk_data.get('risk_score', 0):.1f}",
            delta="out of 100"
        )

    with col2:
        st.metric(
            "DTI Ratio",
            f"{risk_data.get('dti_ratio', 0):.2f}"
        )

    with col3:
        st.metric(
            "LTI Ratio",
            f"{risk_data.get('lti_ratio', 0):.2f}"
        )

    with col4:
        st.metric(
            "Risk Level",
            risk_data.get('risk_level', 'N/A')
        )

    # Display factors
    factors = risk_data.get('factors', {})
    if factors:
        st.subheader("Risk Factors Breakdown")
        for factor_name, factor_data in factors.items():
            impact = factor_data.get('impact', 0)
            color = "🔴" if impact < 0 else "🟢"
            st.write(
                f"{color} {factor_data.get('description', factor_name)}: "
                f"{factor_data.get('value', 0):.2f} (Impact: {impact:+.0f})"
            )


def display_applications_table(applications: list) -> None:
    """Display applications in table format"""
    if not applications:
        st.info("No applications to display")
        return

    data = []
    for app in applications:
        data.append({
            "Application ID": app.get("application_id", "N/A"),
            "Applicant ID": app.get("applicant_id", "N/A"),
            "Loan Amount": f"${app.get('loan_amount', 0):,.2f}",
            "Status": app.get("status", "N/A"),
            "Risk Level": app.get("risk_assessment", {}).get("risk_level", "N/A"),
            "Created": app.get("created_at", "N/A")[:10]
        })

    st.dataframe(data, use_container_width=True, hide_index=True)


def format_chat_response(response: Dict[str, Any]) -> str:
    """Format chat response for display"""
    if not response:
        return "Error processing message"

    bot_response = response.get("bot_response", "")
    return bot_response


# Validation helpers
def validate_form_data(form_data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate form data before submission"""
    errors = []

    # Applicant validation
    if not form_data.get("applicant", {}).get("applicant_id"):
        errors.append("Applicant ID is required")

    if not form_data.get("applicant", {}).get("employment_type"):
        errors.append("Employment Type is required")

    if not form_data.get("applicant", {}).get("location"):
        errors.append("Location is required")

    # Loan details validation
    if form_data.get("loan_details", {}).get("loan_amount", 0) <= 0:
        errors.append("Loan amount must be greater than 0")

    if form_data.get("loan_details", {}).get("credit_score", 0) < 300:
        errors.append("Credit score must be at least 300")

    return len(errors) == 0, "; ".join(errors) if errors else ""


# Session state helpers
def init_api_session_state() -> None:
    """Initialize API-related session state"""
    if 'api_client' not in st.session_state:
        st.session_state.api_client = get_api_client()

    if 'last_application' not in st.session_state:
        st.session_state.last_application = None

    if 'api_messages' not in st.session_state:
        st.session_state.api_messages = []
