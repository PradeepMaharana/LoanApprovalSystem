#!/usr/bin/env python3

"""
Loan Decision Agent
Synthesizes loan decisions using DecisionSynthesis MCP Server
Outputs: Classification (Approve/Reject/Review), Risk Score, Confidence Level, Key Decision Factors, Explanation
"""

import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict, Any, List, Tuple
import sys

class LoanDecisionAgent:
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

    def fetch_decision_data(self, applicant_id: str) -> Dict[str, Any]:
        """Fetch complete decision data from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Fetch applicant data
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

    def calculate_risk_score(self, data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Calculate comprehensive risk score"""
        applicant = data.get('applicant', {})
        application = data.get('application', {})
        risk_assessment = data.get('risk_assessment', {})

        score = 50  # Base score
        factors = {}

        # 1. Credit Score Factor (25 points)
        credit_score = application.get('credit_score', 650)
        credit_factor = 0
        if credit_score >= 750:
            credit_factor = 25
        elif credit_score >= 700:
            credit_factor = 20
        elif credit_score >= 650:
            credit_factor = 10
        elif credit_score >= 600:
            credit_factor = -10
        else:
            credit_factor = -25

        factors['credit_score'] = {
            'value': credit_score,
            'weight': 0.25,
            'contribution': credit_factor
        }
        score += credit_factor

        # 2. Income Stability Factor (20 points)
        income_stability = risk_assessment.get('income_stability_score', 50)
        stability_factor = ((income_stability - 50) / 50) * 20
        factors['income_stability'] = {
            'value': income_stability,
            'weight': 0.20,
            'contribution': stability_factor
        }
        score += stability_factor

        # 3. Employment Risk Factor (20 points)
        employment_risk = risk_assessment.get('employment_risk_score', 50)
        employment_factor = ((50 - employment_risk) / 50) * 20
        factors['employment_risk'] = {
            'value': employment_risk,
            'weight': 0.20,
            'contribution': employment_factor
        }
        score += employment_factor

        # 4. DTI Ratio Factor (15 points)
        income = applicant.get('income', 50000)
        liabilities = applicant.get('liabilities', 0)
        loan_amount = application.get('loan_amount', 0)

        monthly_income = income / 12
        monthly_existing_debt = liabilities / 12
        estimated_payment = (loan_amount / 360) + (loan_amount * 0.06 / 12)
        projected_dti = (monthly_existing_debt + estimated_payment) / monthly_income if monthly_income > 0 else 1

        dti_factor = 0
        if projected_dti < 0.30:
            dti_factor = 15
        elif projected_dti < 0.50:
            dti_factor = 10
        elif projected_dti < 0.70:
            dti_factor = 0
        else:
            dti_factor = -15

        factors['dti_ratio'] = {
            'value': round(projected_dti, 3),
            'weight': 0.15,
            'contribution': dti_factor
        }
        score += dti_factor

        # 5. Loan-to-Income Factor (10 points)
        lti_ratio = loan_amount / income if income > 0 else 10
        lti_factor = 0
        if lti_ratio < 2:
            lti_factor = 10
        elif lti_ratio < 3:
            lti_factor = 5
        elif lti_ratio < 5:
            lti_factor = -5
        else:
            lti_factor = -10

        factors['loan_to_income'] = {
            'value': round(lti_ratio, 2),
            'weight': 0.10,
            'contribution': lti_factor
        }
        score += lti_factor

        return max(0, min(100, score)), factors

    def classify_decision(self, risk_score: float) -> Tuple[str, str]:
        """Classify loan decision based on risk score"""
        if risk_score >= 75:
            return 'APPROVE', 'Strong approval recommended - low risk profile'
        elif risk_score >= 60:
            return 'APPROVE', 'Approval recommended - acceptable risk profile'
        elif risk_score >= 45:
            return 'REVIEW', 'Manual review recommended - moderate risk'
        elif risk_score >= 30:
            return 'REJECT', 'Rejection recommended - significant concerns'
        else:
            return 'REJECT', 'Strong rejection recommended - very high risk'

    def calculate_interest_rate(self, risk_score: float, base_rate: float = 5.5) -> float:
        """Calculate recommended interest rate based on risk"""
        # Risk-based pricing
        if risk_score >= 75:
            adjustment = -1.0  # 0.5% discount
        elif risk_score >= 60:
            adjustment = -0.5  # 0.5% discount
        elif risk_score >= 45:
            adjustment = 0.0   # Base rate
        elif risk_score >= 30:
            adjustment = 1.5   # 1.5% premium
        else:
            adjustment = 3.0   # 3% premium

        final_rate = max(base_rate + adjustment, 3.0)  # Minimum 3%
        return round(final_rate, 2)

    def calculate_loan_terms(self, loan_amount: float, interest_rate: float,
                            risk_score: float) -> Dict[str, Any]:
        """Calculate recommended loan terms"""
        # Term length based on risk
        if risk_score >= 75:
            term_months = 360  # 30 years
        elif risk_score >= 60:
            term_months = 300  # 25 years
        elif risk_score >= 45:
            term_months = 240  # 20 years
        else:
            term_months = 180  # 15 years

        # Calculate monthly payment
        monthly_rate = interest_rate / 100 / 12
        if monthly_rate == 0:
            monthly_payment = loan_amount / term_months
        else:
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**term_months) / \
                            ((1 + monthly_rate)**term_months - 1)

        total_paid = monthly_payment * term_months
        total_interest = total_paid - loan_amount

        return {
            'term_months': term_months,
            'term_years': term_months / 12,
            'monthly_payment': round(monthly_payment, 2),
            'total_interest': round(total_interest, 2),
            'total_amount_paid': round(total_paid, 2)
        }

    def extract_key_factors(self, data: Dict[str, Any], factors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key decision factors"""
        key_factors = []

        # Rank factors by impact
        ranked_factors = sorted(
            factors.items(),
            key=lambda x: abs(x[1]['contribution']),
            reverse=True
        )

        for factor_name, factor_data in ranked_factors[:5]:
            contribution = factor_data['contribution']
            impact = 'Positive' if contribution > 0 else 'Negative'

            key_factors.append({
                'factor': factor_name.replace('_', ' ').title(),
                'value': factor_data['value'],
                'impact': impact,
                'contribution_to_score': round(contribution, 2),
                'weight': round(factor_data['weight'] * 100, 1)
            })

        return key_factors

    def generate_explanation(self, risk_score: float, decision: str,
                            factors: List[Dict], data: Dict) -> str:
        """Generate detailed explanation for the decision"""
        applicant = data.get('applicant', {})
        application = data.get('application', {})

        explanation = f"Loan decision synthesis for {applicant.get('full_name', 'Unknown')}: "
        explanation += f"Overall risk score is {risk_score:.0f}/100, resulting in a '{decision}' decision. "

        # Positive factors
        positive = [f for f in factors if f['impact'] == 'Positive']
        if positive:
            top_positive = positive[0]
            explanation += f"Strongest positive factor: {top_positive['factor']} ({top_positive['value']}). "

        # Negative factors
        negative = [f for f in factors if f['impact'] == 'Negative']
        if negative:
            top_negative = negative[0]
            explanation += f"Primary concern: {top_negative['factor']} ({top_negative['value']}). "

        if decision == 'APPROVE':
            explanation += "Applicant demonstrates acceptable creditworthiness and repayment capacity."
        elif decision == 'REVIEW':
            explanation += "Applicant requires additional review due to moderate risk factors."
        else:  # REJECT
            explanation += "Applicant presents significant risk factors requiring rejection."

        return explanation

    def calculate_confidence_level(self, data: Dict[str, Any]) -> float:
        """Calculate confidence level of the decision"""
        confidence = 100

        # Data completeness
        if not data.get('applicant'):
            confidence -= 20
        if not data.get('application'):
            confidence -= 20
        if not data.get('risk_assessment'):
            confidence -= 10

        # Credit score availability
        if not data.get('application', {}).get('credit_score'):
            confidence -= 5

        return max(50, confidence)  # Minimum 50% confidence

    def synthesize_loan_decision(self, applicant_id: str) -> Dict[str, Any]:
        """Synthesize complete loan decision"""
        self.applicant_id = applicant_id

        # Fetch data from database
        data = self.fetch_decision_data(applicant_id)
        if not data or not data['applicant']:
            return {"error": f"Applicant {applicant_id} not found"}

        # Calculate risk score
        risk_score, factors = self.calculate_risk_score(data)

        # Classify decision
        classification, classification_reason = self.classify_decision(risk_score)

        # Calculate terms
        application = data.get('application', {})
        loan_amount = application.get('loan_amount', 0)
        interest_rate = self.calculate_interest_rate(risk_score)
        loan_terms = self.calculate_loan_terms(loan_amount, interest_rate, risk_score)

        # Extract key factors
        key_factors = self.extract_key_factors(data, factors)

        # Generate explanation
        explanation = self.generate_explanation(risk_score, classification, key_factors, data)

        # Calculate confidence
        confidence = self.calculate_confidence_level(data)

        decision_output = {
            "applicant_id": applicant_id,
            "timestamp": datetime.now().isoformat(),
            "decision": {
                "classification": classification,
                "classification_reason": classification_reason,
                "risk_score": round(risk_score, 2),
                "confidence_level": round(confidence, 1)
            },
            "key_decision_factors": key_factors,
            "financial_breakdown": {
                "requested_loan_amount": loan_amount,
                "recommended_interest_rate": interest_rate,
                "recommended_term": f"{int(loan_terms['term_years'])} years ({loan_terms['term_months']} months)",
                "estimated_monthly_payment": loan_terms['monthly_payment'],
                "total_interest_cost": loan_terms['total_interest'],
                "total_amount_to_repay": loan_terms['total_amount_paid']
            },
            "conditions": self.generate_conditions(classification, risk_score, data),
            "explanation": explanation,
            "recommendation_for_processor": self.generate_processor_recommendation(
                classification, risk_score, key_factors
            )
        }

        return decision_output

    def generate_conditions(self, classification: str, risk_score: float, data: Dict) -> List[str]:
        """Generate conditions for the loan if applicable"""
        conditions = []

        if classification == 'APPROVE':
            conditions.append("Standard loan terms apply")
            if risk_score < 70:
                conditions.append("Recommend automatic payment setup")

        elif classification == 'REVIEW':
            conditions.append("Requires manual underwriter review")
            if risk_score < 50:
                conditions.append("May require co-signer")
                conditions.append("Consider reducing loan amount")
            conditions.append("Request additional employment verification")

        else:  # REJECT
            conditions.append("Recommend rejection")
            risk_assessment = data.get('risk_assessment', {})
            if risk_assessment.get('employment_risk_score', 50) > 70:
                conditions.append("Employment risk too high")
            if data.get('application', {}).get('credit_score', 0) < 600:
                conditions.append("Credit score below acceptable threshold")

        return conditions

    def generate_processor_recommendation(self, classification: str, risk_score: float, factors: List) -> str:
        """Generate recommendation for loan processor"""
        if classification == 'APPROVE':
            return "Process immediately with standard terms"
        elif classification == 'REVIEW':
            return "Schedule for manual review; consider requesting additional documentation"
        else:
            return "Proceed with rejection; applicant may reapply after 6 months with improved credit"

    def print_report(self, decision: Dict[str, Any]):
        """Print formatted decision report"""
        print("\n" + "="*80)
        print("LOAN DECISION SYNTHESIS REPORT")
        print("="*80)

        print(f"\n📋 APPLICANT ID: {decision.get('applicant_id')}")
        print(f"⏰ DECISION TIME: {decision.get('timestamp')}")

        decision_info = decision.get('decision', {})
        print(f"\n🎯 DECISION CLASSIFICATION:")
        print(f"   Decision: {decision_info.get('classification')}")
        print(f"   Risk Score: {decision_info.get('risk_score')}/100")
        print(f"   Confidence Level: {decision_info.get('confidence_level')}%")
        print(f"   Reason: {decision_info.get('classification_reason')}")

        print(f"\n📊 KEY DECISION FACTORS:")
        for i, factor in enumerate(decision.get('key_decision_factors', []), 1):
            print(f"   {i}. {factor.get('factor')}")
            print(f"      Value: {factor.get('value')} | Impact: {factor.get('impact')} | Weight: {factor.get('weight')}%")

        financial = decision.get('financial_breakdown', {})
        print(f"\n💰 FINANCIAL BREAKDOWN:")
        print(f"   Loan Amount: ${financial.get('requested_loan_amount'):,.2f}")
        print(f"   Interest Rate: {financial.get('recommended_interest_rate')}%")
        print(f"   Term: {financial.get('recommended_term')}")
        print(f"   Monthly Payment: ${financial.get('estimated_monthly_payment'):,.2f}")
        print(f"   Total Interest: ${financial.get('total_interest_cost'):,.2f}")
        print(f"   Total to Repay: ${financial.get('total_amount_to_repay'):,.2f}")

        print(f"\n⚠️  CONDITIONS:")
        for condition in decision.get('conditions', []):
            print(f"   • {condition}")

        print(f"\n💡 EXPLANATION:")
        print(f"   {decision.get('explanation')}")

        print(f"\n✅ RECOMMENDATION FOR PROCESSOR:")
        print(f"   {decision.get('recommendation_for_processor')}")

        print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',
        'database': 'loan_approval_system'
    }

    agent = LoanDecisionAgent(db_config)

    if not agent.connect_database():
        sys.exit(1)

    try:
        # Example: Synthesize decision for first applicant
        applicant_id = 'APP-2026-000001'

        print(f"\n🔍 Synthesizing loan decision for {applicant_id}...")
        decision = agent.synthesize_loan_decision(applicant_id)

        if 'error' not in decision:
            agent.print_report(decision)

            # Output as JSON
            print(json.dumps(decision, indent=2, default=str))
        else:
            print(f"❌ {decision['error']}")

    finally:
        agent.disconnect_database()


if __name__ == "__main__":
    main()
