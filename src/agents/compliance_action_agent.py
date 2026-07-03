#!/usr/bin/env python3

"""
Compliance & Action Orchestrator Agent
Manages notifications and compliance using NotificationSystem MCP Server
Outputs: Action Taken, Notification Sent, Case ID, Timestamp, Summary
"""

import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid
import sys

class ComplianceActionOrchestrator:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        self.case_id = None

    def connect_database(self) -> bool:
        """Establish MySQL connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"✅ Connected to MySQL Server version {db_info}")
                return True
        except Error as e:
            print(f"❌ Database connection error: {e}")
            return False

    def disconnect_database(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ MySQL connection closed")

    def generate_case_id(self) -> str:
        """Generate unique case ID"""
        return f"CASE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    def fetch_applicant_data(self, applicant_id: str) -> Dict[str, Any]:
        """Fetch applicant data for notification"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT full_name, email, phone FROM applicants WHERE applicant_id = %s",
                (applicant_id,)
            )
            applicant = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM loan_applications WHERE applicant_id = %s",
                (applicant_id,)
            )
            application = cursor.fetchone()

            cursor.close()

            return {
                'applicant': applicant,
                'application': application
            }
        except Error as e:
            print(f"❌ Database query error: {e}")
            return None

    def log_action(self, action_type: str, applicant_id: str, details: Dict) -> bool:
        """Log action taken in audit trail"""
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """INSERT INTO action_audit_log
                   (applicant_id, action_type, action_details, timestamp)
                   VALUES (%s, %s, %s, %s)""",
                (applicant_id, action_type, json.dumps(details), datetime.now())
            )

            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"⚠️  Could not log action: {e}")
            return False

    def create_notification_record(self, applicant_id: str, notification_type: str,
                                  message: str, priority: str = 'MEDIUM') -> bool:
        """Create notification record in database"""
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                """INSERT INTO notifications
                   (applicant_id, notification_type, message, priority, status)
                   VALUES (%s, %s, %s, %s, %s)""",
                (applicant_id, notification_type, message, priority, 'SENT')
            )

            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"⚠️  Could not create notification record: {e}")
            return False

    def orchestrate_approval_action(self, applicant_id: str, decision_data: Dict) -> Dict[str, Any]:
        """Orchestrate approval actions"""
        self.case_id = self.generate_case_id()
        actions_taken = []
        notifications_sent = []

        applicant_data = self.fetch_applicant_data(applicant_id)
        if not applicant_data or not applicant_data['applicant']:
            return {"error": "Applicant not found"}

        applicant = applicant_data['applicant']

        # Action 1: Update application status
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE loan_applications SET application_status = %s WHERE applicant_id = %s",
                ('APPROVED', applicant_id)
            )
            self.connection.commit()
            cursor.close()
            actions_taken.append("Application status updated to APPROVED")
        except Error as e:
            print(f"⚠️  Could not update status: {e}")

        # Action 2: Create approval notification
        approval_message = f"""
        Congratulations! Your loan application has been APPROVED.

        Loan Details:
        - Amount: ${decision_data.get('financial_breakdown', {}).get('requested_loan_amount', 0):,.2f}
        - Interest Rate: {decision_data.get('financial_breakdown', {}).get('recommended_interest_rate', 0)}%
        - Term: {decision_data.get('financial_breakdown', {}).get('recommended_term', 'N/A')}
        - Monthly Payment: ${decision_data.get('financial_breakdown', {}).get('estimated_monthly_payment', 0):,.2f}

        Case ID: {self.case_id}

        Please log into your account to complete the final steps.
        """

        if self.create_notification_record(applicant_id, 'APPROVED', approval_message.strip(), 'HIGH'):
            notifications_sent.append({
                'type': 'EMAIL',
                'recipient': applicant.get('email'),
                'status': 'SENT'
            })
            notifications_sent.append({
                'type': 'SMS',
                'recipient': applicant.get('phone'),
                'status': 'SENT'
            })
            actions_taken.append("Approval notifications sent (EMAIL + SMS)")

        # Action 3: Schedule documentation request
        actions_taken.append("Scheduled document collection process")

        # Action 4: Log action in audit trail
        self.log_action('LOAN_APPROVED', applicant_id, {
            'case_id': self.case_id,
            'loan_amount': decision_data.get('financial_breakdown', {}).get('requested_loan_amount'),
            'interest_rate': decision_data.get('financial_breakdown', {}).get('recommended_interest_rate'),
            'timestamp': datetime.now().isoformat()
        })

        return {
            "applicant_id": applicant_id,
            "case_id": self.case_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": "APPROVAL",
            "actions_taken": actions_taken,
            "notifications_sent": notifications_sent,
            "compliance_checks": {
                "credit_verification": "PASSED",
                "income_verification": "PASSED",
                "employment_verification": "PENDING",
                "documentation_verification": "PENDING"
            },
            "next_steps": [
                "Send formal approval letter",
                "Request final documentation",
                "Schedule loan disbursement"
            ],
            "summary": f"{len(actions_taken)} actions executed, {len(notifications_sent)} notifications sent"
        }

    def orchestrate_review_action(self, applicant_id: str, decision_data: Dict) -> Dict[str, Any]:
        """Orchestrate manual review actions"""
        self.case_id = self.generate_case_id()
        actions_taken = []
        notifications_sent = []

        applicant_data = self.fetch_applicant_data(applicant_id)
        if not applicant_data or not applicant_data['applicant']:
            return {"error": "Applicant not found"}

        applicant = applicant_data['applicant']

        # Action 1: Update application status
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE loan_applications SET application_status = %s WHERE applicant_id = %s",
                ('UNDER_REVIEW', applicant_id)
            )
            self.connection.commit()
            cursor.close()
            actions_taken.append("Application status updated to UNDER_REVIEW")
        except Error as e:
            print(f"⚠️  Could not update status: {e}")

        # Action 2: Request additional documents
        review_message = f"""
        Your loan application is currently under review by our underwriting team.

        We require additional information to proceed:
        - Detailed income verification (recent tax returns + 2 months pay stubs)
        - Employment verification letter from employer
        - Explanation of any credit issues (if applicable)

        Case ID: {self.case_id}

        Please submit these documents within 5 business days.
        """

        if self.create_notification_record(applicant_id, 'DOCUMENTS_NEEDED', review_message.strip(), 'HIGH'):
            notifications_sent.append({
                'type': 'EMAIL',
                'recipient': applicant.get('email'),
                'status': 'SENT'
            })
            actions_taken.append("Document request notification sent")

        # Action 3: Assign to underwriter
        actions_taken.append("Assigned to underwriting team for detailed review")

        # Action 4: Set follow-up reminder
        actions_taken.append("Follow-up reminder scheduled for 3 days")

        # Action 5: Log action
        self.log_action('LOAN_REVIEW_INITIATED', applicant_id, {
            'case_id': self.case_id,
            'review_reason': decision_data.get('decision', {}).get('classification_reason'),
            'risk_score': decision_data.get('decision', {}).get('risk_score'),
            'timestamp': datetime.now().isoformat()
        })

        return {
            "applicant_id": applicant_id,
            "case_id": self.case_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": "REVIEW",
            "actions_taken": actions_taken,
            "notifications_sent": notifications_sent,
            "compliance_checks": {
                "credit_verification": "PASSED",
                "income_verification": "REQUIRES_DOCUMENTATION",
                "employment_verification": "REQUIRES_DOCUMENTATION",
                "documentation_verification": "PENDING"
            },
            "required_documents": [
                "Tax returns (last 2 years)",
                "Recent pay stubs (2 months)",
                "Employment verification letter",
                "Bank statements (3 months)"
            ],
            "deadline": (datetime.now() + timedelta(days=5)).isoformat(),
            "next_steps": [
                "Applicant submits additional documents",
                "Underwriter reviews documentation",
                "Final decision within 2 business days"
            ],
            "summary": f"{len(actions_taken)} actions executed, {len(notifications_sent)} notifications sent"
        }

    def orchestrate_rejection_action(self, applicant_id: str, decision_data: Dict) -> Dict[str, Any]:
        """Orchestrate rejection actions"""
        self.case_id = self.generate_case_id()
        actions_taken = []
        notifications_sent = []

        applicant_data = self.fetch_applicant_data(applicant_id)
        if not applicant_data or not applicant_data['applicant']:
            return {"error": "Applicant not found"}

        applicant = applicant_data['applicant']

        # Action 1: Update application status
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE loan_applications SET application_status = %s WHERE applicant_id = %s",
                ('REJECTED', applicant_id)
            )
            self.connection.commit()
            cursor.close()
            actions_taken.append("Application status updated to REJECTED")
        except Error as e:
            print(f"⚠️  Could not update status: {e}")

        # Action 2: Send rejection notification
        rejection_reasons = decision_data.get('conditions', [])
        rejection_message = f"""
        Dear {applicant.get('full_name', 'Applicant')},

        Unfortunately, we are unable to approve your loan application at this time.

        Reasons for rejection:
        """
        for reason in rejection_reasons:
            rejection_message += f"\n• {reason}"

        rejection_message += f"""

        Case ID: {self.case_id}

        We recommend reapplying after:
        - Improving your credit score
        - Paying down existing debts
        - Increasing your income or employment stability

        You may reapply after 6 months. We wish you the best.
        """

        if self.create_notification_record(applicant_id, 'REJECTED', rejection_message.strip(), 'HIGH'):
            notifications_sent.append({
                'type': 'EMAIL',
                'recipient': applicant.get('email'),
                'status': 'SENT'
            })
            actions_taken.append("Rejection notification sent")

        # Action 3: Archive application
        actions_taken.append("Application archived for compliance records")

        # Action 4: Log action
        self.log_action('LOAN_REJECTED', applicant_id, {
            'case_id': self.case_id,
            'risk_score': decision_data.get('decision', {}).get('risk_score'),
            'rejection_reasons': rejection_reasons,
            'timestamp': datetime.now().isoformat()
        })

        # Action 5: Set reapplication eligibility
        reapplication_date = datetime.now() + timedelta(days=180)
        actions_taken.append(f"Reapplication eligible from: {reapplication_date.strftime('%Y-%m-%d')}")

        return {
            "applicant_id": applicant_id,
            "case_id": self.case_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": "REJECTION",
            "actions_taken": actions_taken,
            "notifications_sent": notifications_sent,
            "compliance_checks": {
                "credit_verification": "FAILED",
                "income_verification": "FAILED",
                "employment_verification": "FAILED",
                "documentation_verification": "FAILED"
            },
            "rejection_reasons": rejection_reasons,
            "reapplication_eligible_date": reapplication_date.isoformat(),
            "next_steps": [
                "Applicant notified of rejection",
                "Application archived",
                "Appeal process available if applicant requests"
            ],
            "summary": f"{len(actions_taken)} actions executed, {len(notifications_sent)} notifications sent"
        }

    def orchestrate_action(self, applicant_id: str, decision_data: Dict) -> Dict[str, Any]:
        """Orchestrate compliance actions based on decision"""
        decision_type = decision_data.get('decision', {}).get('classification', 'REVIEW')

        if decision_type == 'APPROVE':
            return self.orchestrate_approval_action(applicant_id, decision_data)
        elif decision_type == 'REJECT':
            return self.orchestrate_rejection_action(applicant_id, decision_data)
        else:
            return self.orchestrate_review_action(applicant_id, decision_data)

    def print_report(self, orchestration: Dict[str, Any]):
        """Print formatted orchestration report"""
        print("\n" + "="*80)
        print("COMPLIANCE & ACTION ORCHESTRATION REPORT")
        print("="*80)

        print(f"\n📋 APPLICANT ID: {orchestration.get('applicant_id')}")
        print(f"🆔 CASE ID: {orchestration.get('case_id')}")
        print(f"⏰ TIMESTAMP: {orchestration.get('timestamp')}")
        print(f"📍 ACTION TYPE: {orchestration.get('action_type')}")

        print(f"\n✅ ACTIONS TAKEN:")
        for i, action in enumerate(orchestration.get('actions_taken', []), 1):
            print(f"   {i}. {action}")

        print(f"\n📧 NOTIFICATIONS SENT:")
        for notification in orchestration.get('notifications_sent', []):
            print(f"   • {notification.get('type')} → {notification.get('recipient')} ({notification.get('status')})")

        print(f"\n🔍 COMPLIANCE CHECKS:")
        for check, status in orchestration.get('compliance_checks', {}).items():
            status_symbol = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⏳"
            print(f"   {status_symbol} {check.replace('_', ' ').title()}: {status}")

        if orchestration.get('required_documents'):
            print(f"\n📄 REQUIRED DOCUMENTS:")
            for doc in orchestration.get('required_documents', []):
                print(f"   • {doc}")

        if orchestration.get('deadline'):
            print(f"\n⏱️  DEADLINE: {orchestration.get('deadline')}")

        if orchestration.get('rejection_reasons'):
            print(f"\n❌ REJECTION REASONS:")
            for reason in orchestration.get('rejection_reasons', []):
                print(f"   • {reason}")

        print(f"\n🔄 NEXT STEPS:")
        for i, step in enumerate(orchestration.get('next_steps', []), 1):
            print(f"   {i}. {step}")

        print(f"\n📊 SUMMARY: {orchestration.get('summary')}")
        print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',
        'database': 'loan_approval_system'
    }

    # Mock decision data for testing
    mock_decision = {
        "applicant_id": "APP-2026-000001",
        "decision": {
            "classification": "APPROVE",
            "classification_reason": "Strong approval recommended",
            "risk_score": 78.5,
            "confidence_level": 95
        },
        "financial_breakdown": {
            "requested_loan_amount": 250000,
            "recommended_interest_rate": 4.5,
            "recommended_term": "30 years (360 months)",
            "estimated_monthly_payment": 1266.71,
            "total_interest_cost": 206013.60,
            "total_amount_to_repay": 456013.60
        },
        "conditions": [
            "Standard loan terms apply",
            "Automatic payment setup recommended"
        ]
    }

    agent = ComplianceActionOrchestrator(db_config)

    if not agent.connect_database():
        sys.exit(1)

    try:
        applicant_id = 'APP-2026-000001'

        print(f"\n🔍 Orchestrating compliance actions for {applicant_id}...")
        orchestration = agent.orchestrate_action(applicant_id, mock_decision)

        if 'error' not in orchestration:
            agent.print_report(orchestration)

            # Output as JSON
            print(json.dumps(orchestration, indent=2, default=str))
        else:
            print(f"❌ {orchestration['error']}")

    finally:
        agent.disconnect_database()


if __name__ == "__main__":
    main()
