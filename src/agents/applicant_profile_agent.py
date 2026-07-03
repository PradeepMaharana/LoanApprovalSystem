#!/usr/bin/env python3

"""
Applicant Profile Agent
Analyzes applicant profiles using ApplicantDB MCP Server
Outputs: Income Stability Score, Employment Risk, Credit History Summary, Application Completeness Flags
"""

import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict, Any
import sys

class ApplicantProfileAgent:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        self.applicant_id = None

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

    def fetch_applicant_data(self, applicant_id: str) -> Dict[str, Any]:
        """Fetch complete applicant data from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Fetch applicant profile
            cursor.execute(
                "SELECT * FROM applicants WHERE applicant_id = %s",
                (applicant_id,)
            )
            applicant = cursor.fetchone()

            # Fetch loan application
            cursor.execute(
                "SELECT * FROM loan_applications WHERE applicant_id = %s",
                (applicant_id,)
            )
            application = cursor.fetchone()

            # Fetch risk assessment
            cursor.execute(
                "SELECT * FROM risk_assessments WHERE applicant_id = %s",
                (applicant_id,)
            )
            risk_assessment = cursor.fetchone()

            cursor.close()

            return {
                'applicant': applicant,
                'application': application,
                'risk_assessment': risk_assessment
            }
        except Error as e:
            print(f"❌ Database query error: {e}")
            return None

    def analyze_applicant_profile(self, applicant_id: str) -> Dict[str, Any]:
        """Analyze complete applicant profile"""
        self.applicant_id = applicant_id

        # Fetch data from database
        data = self.fetch_applicant_data(applicant_id)
        if not data or not data['applicant']:
            return {"error": f"Applicant {applicant_id} not found"}

        applicant = data['applicant']
        application = data['application'] or {}
        risk = data['risk_assessment'] or {}

        # Extract risk assessment metrics
        income_stability_score = risk.get('income_stability_score', 'N/A')
        employment_risk_score = risk.get('employment_risk_score', 'N/A')
        credit_category = risk.get('credit_category', 'Not Assessed')
        credit_recommendation = risk.get('credit_recommendation', 'N/A')
        warning_flags = risk.get('warning_flags', '[]')

        # Parse warning flags
        try:
            if isinstance(warning_flags, str):
                flags = json.loads(warning_flags)
            else:
                flags = warning_flags or []
        except:
            flags = []

        # Calculate application completeness
        required_fields = {
            'full_name': applicant.get('full_name'),
            'date_of_birth': applicant.get('date_of_birth'),
            'email': applicant.get('email'),
            'phone': applicant.get('phone'),
            'address': applicant.get('address'),
            'credit_score': application.get('credit_score'),
            'loan_amount': application.get('loan_amount'),
            'income': applicant.get('income')
        }

        completeness_flags = {
            'missing_fields': [k for k, v in required_fields.items() if not v],
            'documents_verified': application.get('documents_verified', False),
            'employment_verified': application.get('employment_verified', False),
            'income_verified': application.get('income_verified', False)
        }

        # Build comprehensive profile output
        profile_output = {
            "applicant_id": applicant_id,
            "timestamp": datetime.now().isoformat(),
            "applicant_info": {
                "name": applicant.get('full_name', 'N/A'),
                "age": self.calculate_age(applicant.get('date_of_birth')),
                "location": applicant.get('location', 'N/A'),
                "employment_type": applicant.get('employment_type', 'N/A'),
                "annual_income": applicant.get('income', 0)
            },
            "income_stability_score": {
                "score": income_stability_score,
                "range": "0-100",
                "interpretation": self.interpret_income_stability(income_stability_score),
                "factors": {
                    "employment_type": applicant.get('employment_type'),
                    "employment_years": applicant.get('employment_years', 'N/A'),
                    "income_level": "High" if applicant.get('income', 0) > 100000 else "Medium" if applicant.get('income', 0) > 50000 else "Low"
                }
            },
            "employment_risk": {
                "score": employment_risk_score,
                "range": "0-100 (higher = more risk)",
                "risk_level": self.interpret_employment_risk(employment_risk_score),
                "factors": {
                    "employment_type": applicant.get('employment_type'),
                    "industry": applicant.get('industry', 'Unknown'),
                    "employment_duration": applicant.get('employment_years', 0)
                }
            },
            "credit_history_summary": {
                "category": credit_category,
                "description": self.get_credit_description(credit_category),
                "credit_score": application.get('credit_score', 'N/A'),
                "recommendation": credit_recommendation,
                "liabilities": applicant.get('liabilities', 0),
                "debt_accounts": application.get('debt_accounts', 0)
            },
            "application_completeness": {
                "completion_percentage": self.calculate_completeness_percentage(completeness_flags),
                "missing_fields": completeness_flags['missing_fields'],
                "verifications": {
                    "documents_verified": completeness_flags['documents_verified'],
                    "employment_verified": completeness_flags['employment_verified'],
                    "income_verified": completeness_flags['income_verified']
                },
                "warning_flags": flags,
                "status": "Ready for Processing" if len(completeness_flags['missing_fields']) == 0 else "Incomplete - Requires Additional Information"
            },
            "application_status": {
                "status": application.get('application_status', 'Pending'),
                "loan_amount_requested": application.get('loan_amount', 0),
                "date_submitted": application.get('date_submitted', 'N/A')
            }
        }

        return profile_output

    def calculate_age(self, dob):
        """Calculate age from date of birth"""
        if not dob:
            return 'N/A'
        try:
            from datetime import date
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except:
            return 'N/A'

    def interpret_income_stability(self, score):
        """Interpret income stability score"""
        if isinstance(score, str) or score == 'N/A':
            return "Not Available"
        if score >= 80:
            return "Very Stable - Consistent income history, low volatility"
        elif score >= 60:
            return "Stable - Reasonably consistent income"
        elif score >= 40:
            return "Moderate - Some income fluctuation"
        elif score >= 20:
            return "Unstable - Significant income volatility"
        else:
            return "Very Unstable - High income volatility or recent changes"

    def interpret_employment_risk(self, score):
        """Interpret employment risk score"""
        if isinstance(score, str) or score == 'N/A':
            return "Not Available"
        if score <= 25:
            return "Low Risk - Stable employment"
        elif score <= 50:
            return "Moderate Risk - Some employment risk"
        elif score <= 75:
            return "High Risk - Significant employment uncertainty"
        else:
            return "Very High Risk - Critical employment concerns"

    def get_credit_description(self, category):
        """Get description for credit category"""
        descriptions = {
            'Excellent': 'Exceptional credit history with on-time payments',
            'Very Good': 'Strong credit profile with minimal late payments',
            'Good': 'Acceptable credit history with few issues',
            'Fair': 'Credit history with some negative marks',
            'Poor': 'Problematic credit history with significant issues'
        }
        return descriptions.get(category, 'Not Assessed')

    def calculate_completeness_percentage(self, flags):
        """Calculate application completeness percentage"""
        total_fields = 8
        missing = len(flags['missing_fields'])
        verification_gaps = sum([1 for v in flags['verifications'].values() if not v])

        complete_items = total_fields - missing - verification_gaps
        percentage = max(0, (complete_items / (total_fields + 3)) * 100)
        return round(percentage, 1)

    def print_report(self, profile: Dict[str, Any]):
        """Print formatted profile report"""
        print("\n" + "="*80)
        print("APPLICANT PROFILE ANALYSIS REPORT")
        print("="*80)

        print(f"\n📋 APPLICANT ID: {profile.get('applicant_id')}")
        print(f"⏰ ANALYSIS TIME: {profile.get('timestamp')}")

        applicant_info = profile.get('applicant_info', {})
        print(f"\n👤 APPLICANT INFORMATION:")
        print(f"   Name: {applicant_info.get('name')}")
        print(f"   Age: {applicant_info.get('age')}")
        print(f"   Location: {applicant_info.get('location')}")
        print(f"   Employment: {applicant_info.get('employment_type')}")
        print(f"   Annual Income: ${applicant_info.get('annual_income'):,.2f}")

        income_stability = profile.get('income_stability_score', {})
        print(f"\n💰 INCOME STABILITY SCORE:")
        print(f"   Score: {income_stability.get('score')}/100")
        print(f"   Status: {income_stability.get('interpretation')}")

        employment_risk = profile.get('employment_risk', {})
        print(f"\n⚠️  EMPLOYMENT RISK:")
        print(f"   Score: {employment_risk.get('score')}/100")
        print(f"   Risk Level: {employment_risk.get('risk_level')}")

        credit_summary = profile.get('credit_history_summary', {})
        print(f"\n📊 CREDIT HISTORY SUMMARY:")
        print(f"   Category: {credit_summary.get('category')}")
        print(f"   Score: {credit_summary.get('credit_score')}")
        print(f"   Recommendation: {credit_summary.get('recommendation')}")
        print(f"   Liabilities: ${credit_summary.get('liabilities'):,.2f}")

        completeness = profile.get('application_completeness', {})
        print(f"\n✅ APPLICATION COMPLETENESS:")
        print(f"   Completion: {completeness.get('completion_percentage')}%")
        print(f"   Status: {completeness.get('status')}")
        if completeness.get('missing_fields'):
            print(f"   Missing: {', '.join(completeness.get('missing_fields'))}")
        print(f"   Documents Verified: {'Yes' if completeness.get('verifications', {}).get('documents_verified') else 'No'}")
        print(f"   Employment Verified: {'Yes' if completeness.get('verifications', {}).get('employment_verified') else 'No'}")
        print(f"   Income Verified: {'Yes' if completeness.get('verifications', {}).get('income_verified') else 'No'}")

        print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',
        'database': 'loan_approval_system'
    }

    agent = ApplicantProfileAgent(db_config)

    if not agent.connect_database():
        sys.exit(1)

    try:
        # Example: Analyze first applicant
        applicant_id = 'APP-2026-000001'

        print(f"\n🔍 Analyzing applicant profile for {applicant_id}...")
        profile = agent.analyze_applicant_profile(applicant_id)

        if 'error' not in profile:
            agent.print_report(profile)

            # Output as JSON
            print(json.dumps(profile, indent=2, default=str))
        else:
            print(f"❌ {profile['error']}")

    finally:
        agent.disconnect_database()


if __name__ == "__main__":
    main()
