"""
API Test Suite
Comprehensive tests for the Loan Approval System API
"""

import requests
import json
from typing import Dict, Any
import time

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}")


def print_success(text: str):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text: str):
    print(f"{RED}✗ {text}{RESET}")


def print_info(text: str):
    print(f"{YELLOW}ℹ {text}{RESET}")


class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_prefix = API_PREFIX
        self.applications = []

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ):
        """Make HTTP request"""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return response
        except Exception as e:
            print_error(f"Request failed: {str(e)}")
            return None

    def test_health_check(self):
        """Test health endpoint"""
        print_header("Testing Health Check")

        url = f"{self.base_url}/health"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed: {data['status']}")
                print(f"  Service: {data['service']}")
                print(f"  Timestamp: {data['timestamp']}")
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Health check error: {str(e)}")
            return False

    def test_submit_application(self, app_data: Dict[str, Any] = None):
        """Test application submission"""
        print_header("Testing Application Submission")

        if not app_data:
            app_data = {
                "applicant": {
                    "applicant_id": "TEST-APP-001",
                    "age": 35,
                    "income": 120000,
                    "employment_type": "Salaried",
                    "location": "New York, NY"
                },
                "loan_details": {
                    "credit_score": 750,
                    "loan_amount": 300000,
                    "tenure": 360,
                    "liabilities": 50000
                }
            }

        response = self._make_request("POST", "/applications", data=app_data)

        if not response:
            print_error("Failed to submit application")
            return None

        if response.status_code == 201:
            app = response.json()
            print_success(f"Application submitted successfully")
            print(f"  Application ID: {app['application_id']}")
            print(f"  Status: {app['status']}")
            print(f"  Risk Level: {app['risk_assessment']['risk_level']}")
            print(f"  Risk Score: {app['risk_assessment']['risk_score']:.1f}")
            print(f"  DTI Ratio: {app['risk_assessment']['dti_ratio']:.2f}")
            print(f"  LTI Ratio: {app['risk_assessment']['lti_ratio']:.2f}")
            print(f"  Message: {app['message']}")

            self.applications.append(app)
            return app
        else:
            print_error(f"Submission failed with status {response.status_code}")
            if response.text:
                print(f"  Response: {response.text}")
            return None

    def test_invalid_submission(self):
        """Test invalid application submission"""
        print_header("Testing Invalid Application (Expected to Fail)")

        invalid_data = {
            "applicant": {
                "applicant_id": "INVALID",
                "age": 15,  # Too young
                "income": -1000,  # Negative income
                "employment_type": "InvalidType",
                "location": ""
            },
            "loan_details": {
                "credit_score": 250,  # Too low
                "loan_amount": -5000,  # Negative
                "tenure": 100,  # Not multiple of 3
                "liabilities": -100
            }
        }

        response = self._make_request("POST", "/applications", data=invalid_data)

        if response and response.status_code != 201:
            print_success("Validation correctly rejected invalid data")
            print(f"  Status Code: {response.status_code}")
            if response.text:
                print(f"  Errors: {response.text[:200]}...")
            return True
        else:
            print_error("Validation did not catch invalid data")
            return False

    def test_get_application(self, application_id: str):
        """Test retrieving specific application"""
        print_header(f"Testing Get Application: {application_id}")

        response = self._make_request("GET", f"/applications/{application_id}")

        if not response:
            print_error("Failed to retrieve application")
            return None

        if response.status_code == 200:
            app = response.json()
            print_success("Application retrieved successfully")
            print(f"  Application ID: {app['application_id']}")
            print(f"  Status: {app['status']}")
            print(f"  Applicant ID: {app['applicant_id']}")
            return app
        elif response.status_code == 404:
            print_error(f"Application not found: {application_id}")
            return None
        else:
            print_error(f"Retrieval failed with status {response.status_code}")
            return None

    def test_list_applications(self, page: int = 1, page_size: int = 10):
        """Test listing applications"""
        print_header("Testing List Applications")

        params = {
            "page": page,
            "page_size": page_size
        }

        response = self._make_request("GET", "/applications", params=params)

        if not response:
            print_error("Failed to list applications")
            return None

        if response.status_code == 200:
            data = response.json()
            print_success(f"Applications listed successfully")
            print(f"  Total Count: {data['total_count']}")
            print(f"  Page: {data['page']}")
            print(f"  Page Size: {data['page_size']}")
            print(f"  Applications Returned: {len(data['applications'])}")

            for app in data['applications'][:3]:  # Show first 3
                print(f"    - {app['application_id']}: {app['status']}")

            return data
        else:
            print_error(f"Listing failed with status {response.status_code}")
            return None

    def test_validate_application(self, app_data: Dict[str, Any] = None):
        """Test application validation without submission"""
        print_header("Testing Application Validation (Without Submission)")

        if not app_data:
            app_data = {
                "applicant": {
                    "applicant_id": "VALIDATION-TEST",
                    "age": 28,
                    "income": 85000,
                    "employment_type": "Self-Employed",
                    "location": "San Francisco, CA"
                },
                "loan_details": {
                    "credit_score": 680,
                    "loan_amount": 200000,
                    "tenure": 240,
                    "liabilities": 30000
                }
            }

        response = self._make_request("POST", "/validate-application", data=app_data)

        if not response:
            print_error("Failed to validate application")
            return None

        if response.status_code == 200:
            risk = response.json()
            print_success("Application validated successfully")
            print(f"  Risk Score: {risk['risk_score']:.1f}")
            print(f"  Risk Level: {risk['risk_level']}")
            print(f"  DTI Ratio: {risk['dti_ratio']:.2f}")
            print(f"  LTI Ratio: {risk['lti_ratio']:.2f}")

            print("  Risk Factors:")
            for factor_name, factor_data in risk['factors'].items():
                print(f"    - {factor_data['description']}: {factor_data['value']:.2f} (Impact: {factor_data['impact']:+.0f})")

            return risk
        else:
            print_error(f"Validation failed with status {response.status_code}")
            return None

    def test_chat_message(self, user_id: str = "test-user", message: str = "What are my approval chances?", app_id: str = None):
        """Test chat functionality"""
        print_header("Testing Chat Message")

        chat_data = {
            "user_id": user_id,
            "message": message,
            "application_id": app_id
        }

        response = self._make_request("POST", "/chat", data=chat_data)

        if not response:
            print_error("Failed to send chat message")
            return None

        if response.status_code == 200:
            chat = response.json()
            print_success("Chat message processed successfully")
            print(f"  Message ID: {chat['message_id']}")
            print(f"  User ID: {chat['user_id']}")
            print(f"  User Message: {chat['user_message']}")
            print(f"  Bot Response: {chat['bot_response']}")

            if chat.get('application_context'):
                print(f"  Has Application Context: Yes")

            return chat
        else:
            print_error(f"Chat failed with status {response.status_code}")
            return None

    def test_multiple_applications(self):
        """Test submitting multiple applications"""
        print_header("Testing Multiple Applications")

        test_cases = [
            {
                "name": "High Risk Applicant",
                "data": {
                    "applicant": {
                        "applicant_id": "HIGH-RISK-001",
                        "age": 25,
                        "income": 35000,
                        "employment_type": "Freelancer",
                        "location": "Austin, TX"
                    },
                    "loan_details": {
                        "credit_score": 550,
                        "loan_amount": 500000,
                        "tenure": 360,
                        "liabilities": 150000
                    }
                }
            },
            {
                "name": "Low Risk Applicant",
                "data": {
                    "applicant": {
                        "applicant_id": "LOW-RISK-001",
                        "age": 45,
                        "income": 250000,
                        "employment_type": "Business Owner",
                        "location": "Seattle, WA"
                    },
                    "loan_details": {
                        "credit_score": 800,
                        "loan_amount": 400000,
                        "tenure": 240,
                        "liabilities": 50000
                    }
                }
            }
        ]

        for test_case in test_cases:
            print_info(f"Submitting {test_case['name']}")
            app = self.test_submit_application(test_case['data'])

            if app:
                print(f"  Result: {app['status']}")

            time.sleep(0.5)

    def run_full_test_suite(self):
        """Run complete test suite"""
        print(f"\n{BLUE}┌{'─'*58}┐")
        print(f"│ Loan Approval System API Test Suite{' '*21}│")
        print(f"│ Base URL: {self.base_url}{' '*(46-len(self.base_url))}│")
        print(f"└{'─'*58}┘{RESET}")

        # Test health
        if not self.test_health_check():
            print_error("API is not running. Please start it first.")
            return

        # Test submissions
        app1 = self.test_submit_application()
        self.test_invalid_submission()

        if app1:
            # Test retrieval
            self.test_get_application(app1['application_id'])

            # Test chat with application context
            self.test_chat_message(app_id=app1['application_id'])

        # Test list
        self.test_list_applications()

        # Test validation
        self.test_validate_application()

        # Test chat without context
        self.test_chat_message(message="How long does processing take?")

        # Test multiple applications
        self.test_multiple_applications()

        # Summary
        print_header("Test Suite Summary")
        print_success(f"Total applications created: {len(self.applications)}")
        print_success("Test suite completed!")


if __name__ == "__main__":
    tester = APITester()
    tester.run_full_test_suite()
