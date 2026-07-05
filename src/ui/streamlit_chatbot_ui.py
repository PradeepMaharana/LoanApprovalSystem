#!/usr/bin/env python3

"""
Streamlit Chatbot UI for Loan Application
Integrates with FastAPI orchestrator for end-to-end processing
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from streamlit_integration import LoanAPIClient

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8001"
PROCESSING_TIMEOUT = 120  # seconds

st.set_page_config(
    page_title="AI Loan Assistant",
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
    if "current_application" not in st.session_state:
        st.session_state.current_application = {}
    if "processing_result" not in st.session_state:
        st.session_state.processing_result = None
    if "applicant_id" not in st.session_state:
        st.session_state.applicant_id = None
    if "show_raw_json" not in st.session_state:
        st.session_state.show_raw_json = False


init_session_state()

# ============================================================================
# Helper Functions
# ============================================================================

def add_message(role: str, content: str):
    """Add message to conversation history"""
    st.session_state.conversation_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })


def submit_to_orchestrator(applicant_id: str) -> Dict[str, Any]:
    """Submit application to orchestrator API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/process",
            json={"applicant_id": applicant_id},
            timeout=PROCESSING_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code} - {response.text}"}

    except requests.Timeout:
        return {"error": "Processing timeout - request took too long"}
    except requests.ConnectionError:
        return {"error": "Failed to connect to orchestrator API"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


def get_processing_status(applicant_id: str) -> Dict[str, Any]:
    """Get processing status from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/status/{applicant_id}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status not found"}

    except Exception as e:
        return {"error": str(e)}


def format_processing_result(result: Dict[str, Any]) -> str:
    """Format processing result for display"""
    output = ""

    # Decision
    output += f"### 🎯 Loan Decision: {result.get('decision', 'PENDING')}\n\n"

    # Risk Score & Confidence
    output += f"**Risk Score:** {result.get('risk_score', 'N/A')}/100 | "
    output += f"**Confidence:** {result.get('confidence', 'N/A')}%\n\n"

    # Case ID
    if result.get('case_id'):
        output += f"**Case ID:** `{result.get('case_id')}`\n\n"

    # Processing Stages
    output += "### 📊 Processing Stages\n"
    for stage in result.get('processing_stages', []):
        status_emoji = "✅" if stage.get('status') == "COMPLETED" else "⏳" if stage.get('status') == "IN_PROGRESS" else "❌"
        output += f"{status_emoji} **{stage.get('stage')}** - {stage.get('status')}\n"

    output += "\n"

    # LLM Analysis
    if result.get('llm_analysis'):
        analysis = result['llm_analysis']
        if analysis.get('executive_summary'):
            output += f"### 📝 Executive Summary\n{analysis.get('executive_summary')}\n\n"

        if analysis.get('key_strengths'):
            output += "### ✅ Key Strengths\n"
            for strength in analysis.get('key_strengths', []):
                output += f"• {strength}\n"
            output += "\n"

        if analysis.get('key_concerns'):
            output += "### ⚠️ Key Concerns\n"
            for concern in analysis.get('key_concerns', []):
                output += f"• {concern}\n"
            output += "\n"

        if analysis.get('recommendation_letter'):
            output += f"### 💌 Recommendation Letter\n{analysis.get('recommendation_letter')}\n\n"

    # Errors
    if result.get('errors'):
        output += "### ❌ Errors\n"
        for error in result['errors']:
            output += f"• {error}\n"

    return output


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render header"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("🏦 AI Loan Assistant")
        st.markdown("*Powered by LangGraph, LangChain & Claude Sonnet 4.6*")

    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.current_application = {}
            st.session_state.processing_result = None
            st.rerun()


def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.header("📋 Application Info")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Processing")
            if st.session_state.applicant_id:
                st.info(f"ID: {st.session_state.applicant_id}")
            else:
                st.warning("No applicant loaded")

        with col2:
            st.subheader("Status")
            if st.session_state.processing_result:
                decision = st.session_state.processing_result.get('decision', 'UNKNOWN')
                if decision == "APPROVE":
                    st.success(decision)
                elif decision == "REJECT":
                    st.error(decision)
                else:
                    st.warning(decision)
            else:
                st.info("Pending")

        st.divider()

        st.subheader("🔍 Quick Search")

        api_client = LoanAPIClient(base_url="http://localhost:8000")

        search_app_id = st.text_input(
            "Search Applicant ID",
            placeholder="APP-2024-001",
            key="sidebar_search_id"
        )

        if st.button("Search", use_container_width=True, key="sidebar_search_btn"):
            if search_app_id:
                with st.spinner("Searching..."):
                    results = api_client.search_applicants(applicant_id=search_app_id)
                    if results and results.get('data'):
                        st.success(f"✅ Found applicant!")
                        applicant = results['data'][0]
                        st.session_state.applicant_id = applicant.get('applicant_id')
                        st.rerun()
                    else:
                        st.warning("❌ Applicant not found")
            else:
                st.warning("Please enter an applicant ID")

        st.divider()

        st.subheader("⚙️ Settings")

        api_url = st.text_input(
            "API URL",
            value=API_BASE_URL,
            help="FastAPI orchestrator URL",
            key="settings_api_url"
        )

        st.session_state.show_raw_json = st.checkbox(
            "Show Raw JSON",
            value=st.session_state.show_raw_json,
            help="Display raw API responses",
            key="show_raw_json_checkbox"
        )

        st.divider()

        st.subheader("📊 Quick Stats")

        if st.button("Get Analytics", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL}/analytics/summary", timeout=10)
                if response.status_code == 200:
                    analytics = response.json()
                    st.metric("Total Processed", analytics.get('total_processed', 0))
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Approved", analytics.get('approved', 0))
                    with col2:
                        st.metric("Rejected", analytics.get('rejected', 0))
                    with col3:
                        st.metric("Under Review", analytics.get('under_review', 0))
            except Exception as e:
                st.error(f"Error fetching analytics: {str(e)}")


def render_chat_interface():
    """Render chat interface"""
    st.subheader("💬 Chat")

    # Display conversation history
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input area
    st.divider()

    user_input = st.text_input(
        "Enter applicant ID or ask a question:",
        placeholder="APP-2026-000001 or 'Process applicant APP-2026-000001'",
        label_visibility="collapsed",
        key="chat_input_main"
    )

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        submit_button = st.button("▶️ Send", use_container_width=True, type="primary", key="send_main")
    with col_btn2:
        clear_button = st.button("🔄 Clear Chat", use_container_width=True, key="clear_chat_btn")
    with col_btn3:
        pass

    if clear_button:
        st.session_state.conversation_history = []
        st.session_state.processing_result = None
        st.rerun()

    if submit_button and user_input:
        # Add user message
        add_message("user", user_input)

        with st.chat_message("user"):
            st.write(user_input)

        # Process request
        with st.spinner("🔄 Processing..."):
            # Parse input
            if user_input.startswith("APP-"):
                applicant_id = user_input
            elif "APP-" in user_input:
                applicant_id = user_input.split("APP-")[1].split()[0]
                applicant_id = "APP-" + applicant_id
            else:
                add_message("assistant", "❌ Please provide a valid applicant ID (e.g., APP-2026-000001)")
                st.rerun()

            st.session_state.applicant_id = applicant_id

            # Submit to orchestrator
            result = submit_to_orchestrator(applicant_id)

            if "error" not in result:
                st.session_state.processing_result = result

                # Format response
                response_text = format_processing_result(result)
                add_message("assistant", response_text)

                with st.chat_message("assistant"):
                    st.markdown(response_text)

                # Show raw JSON if enabled
                if st.session_state.get("show_raw_json"):
                    with st.expander("📋 Raw Response JSON"):
                        st.json(result)

            else:
                error_message = f"❌ Error: {result['error']}"
                add_message("assistant", error_message)
                with st.chat_message("assistant"):
                    st.error(error_message)

        st.rerun()


def render_results_panel():
    """Render detailed results panel"""
    if st.session_state.processing_result:
        st.header("📊 Processing Results")

        result = st.session_state.processing_result

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Stages", "Analysis", "Details"])

        with tab1:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Decision", result.get("decision", "N/A"))

            with col2:
                st.metric("Risk Score", f"{result.get('risk_score', 'N/A')}/100")

            with col3:
                st.metric("Confidence", f"{result.get('confidence', 'N/A')}%")

            with col4:
                st.metric("Case ID", result.get('case_id', 'N/A')[:10] + "...")

        with tab2:
            st.subheader("Processing Pipeline")

            for i, stage in enumerate(result.get('processing_stages', []), 1):
                status_color = "green" if stage.get('status') == "COMPLETED" else "orange" if stage.get('status') == "IN_PROGRESS" else "red"

                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.write(f"**{stage.get('stage')}**")

                    with col2:
                        st.write(f":{status_color}[{stage.get('status')}]")

                    with col3:
                        st.caption(stage.get('timestamp', 'N/A'))

        with tab3:
            analysis = result.get('llm_analysis', {})

            if analysis:
                if analysis.get('executive_summary'):
                    st.subheader("📝 Executive Summary")
                    st.info(analysis['executive_summary'])

                if analysis.get('key_strengths'):
                    st.subheader("✅ Strengths")
                    for strength in analysis['key_strengths']:
                        st.write(f"• {strength}")

                if analysis.get('key_concerns'):
                    st.subheader("⚠️ Concerns")
                    for concern in analysis['key_concerns']:
                        st.write(f"• {concern}")

                if analysis.get('recommendation_letter'):
                    st.subheader("💌 Recommendation")
                    with st.expander("View Full Letter"):
                        st.write(analysis['recommendation_letter'])
            else:
                st.info("No LLM analysis available")

        with tab4:
            st.subheader("Full Response")
            st.json(result)


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main app"""
    render_header()
    render_sidebar()

    # Main content
    col_chat, col_results = st.columns([2, 2])

    with col_chat:
        render_chat_interface()

    with col_results:
        render_results_panel()


if __name__ == "__main__":
    main()
