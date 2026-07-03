#!/usr/bin/env python3

"""
Financial Risk Analysis Agent
Analyzes financial risk using RiskRulesDB MCP Server
Outputs: Debt-to-Income Ratio, Credit Score Risk Level, Loan Amount Risk, Anomaly Detection, Reasoning
"""

import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict, Any, Tuple
import sys

class FinancialRiskAgent:
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

    def fetch_financial_data(self, applicant_id: str) -> Dict[str, Any]:
        """Fetch complete financial data from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            # Fetch applicant financial info
            cursor.execute(
                "SELECT income, liabilities FROM applicants WHERE applicant_id = %s",
                (applicant_id,)
            )
            applicant = cursor.fetchone()

            # Fetch application info
            cursor.execute(
                "SELECT credit_score, loan_amount, debt_accounts FROM loan_applications WHERE applicant_id = %s",
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

    def calculate_dti_ratio(self, monthly_income: float, monthly_debt: float) -> Tuple[float, str]:
        """Calculate Debt-to-Income ratio"""
        if monthly_income == 0:
            return 0, "Invalid Income"

        dti = monthly_debt / monthly_income

        if dti < 0.15:
            status = "Excellent"
        elif dti < 0.30:
            status = "Good"
        elif dti < 0.50:
            status = "Acceptable"
        elif dti < 0.70:
            status = "High"
        else:
            status = "Very High Risk"

        return round(dti, 3), status

    def evaluate_credit_risk(self, credit_score: int) -> Dict[str, Any]:
        """Evaluate credit score risk level"""
        if not credit_score:
            return {
                'score': 'N/A',
                'risk_level': 'Unknown',
                'recommendation': 'Credit score not provided'
            }

        if credit_score >= 750:
            risk_level = "Low Risk"
            recommendation = "Excellent credit profile, minimal risk"
            approval_likelihood = 0.95
        elif credit_score >= 700:
            risk_level = "Low-Medium Risk"
            recommendation = "Good credit, standard terms recommended"
            approval_likelihood = 0.85
        elif credit_score >= 650:
            risk_level = "Medium Risk"
            recommendation = "Fair credit, consider higher rates or lower amounts"
            approval_likelihood = 0.65
        elif credit_score >= 600:
            risk_level = "High Risk"
            recommendation = "Poor credit, significant conditions required"
            approval_likelihood = 0.35
        else:
            risk_level = "Very High Risk"
            recommendation = "Very poor credit, recommend rejection or significant collateral"
            approval_likelihood = 0.10

        return {
            'score': credit_score,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'approval_likelihood': approval_likelihood
        }

    def evaluate_loan_amount_risk(self, loan_amount: float, annual_income: float,
                                 credit_score: int, existing_liabilities: float) -> Dict[str, Any]:
        """Evaluate loan amount risk"""
        if annual_income == 0:
            return {'error': 'No income data'}

        # Calculate loan-to-income ratio
        lti_ratio = loan_amount / annual_income

        # Calculate monthly debt obligations (estimated)
        monthly_income = annual_income / 12
        monthly_liabilities = existing_liabilities / 12
        projected_monthly_payment = (loan_amount / 360) + (loan_amount * 0.06 / 12)  # Estimate
        total_monthly_debt = monthly_liabilities + projected_monthly_payment

        # DTI with new loan
        projected_dti, dti_status = self.calculate_dti_ratio(monthly_income, total_monthly_debt)

        # Risk assessment
        risk_factors = []
        risk_score = 0

        if lti_ratio > 5:
            risk_factors.append("Loan exceeds 5x annual income")
            risk_score += 30
        elif lti_ratio > 3:
            risk_factors.append("Loan exceeds 3x annual income")
            risk_score += 15

        if projected_dti > 0.5:
            risk_factors.append("Projected DTI exceeds 50%")
            risk_score += 25

        if credit_score < 650:
            risk_factors.append("Credit score below 650")
            risk_score += 20

        # Risk classification
        if risk_score >= 50:
            risk_level = "High Risk"
        elif risk_score >= 30:
            risk_level = "Medium Risk"
        elif risk_score >= 15:
            risk_level = "Low-Medium Risk"
        else:
            risk_level = "Low Risk"

        return {
            'loan_amount': loan_amount,
            'loan_to_income_ratio': round(lti_ratio, 2),
            'monthly_debt_service_estimate': round(projected_monthly_payment, 2),
            'projected_dti': round(projected_dti, 3),
            'projected_dti_status': dti_status,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendation': 'Consider lower amount' if risk_score >= 50 else 'Acceptable' if risk_score < 30 else 'Review carefully'
        }

    def detect_anomalies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect financial anomalies"""
        applicant = data.get('applicant', {})
        application = data.get('application', {})
        risk_assessment = data.get('risk_assessment', {})

        anomalies = []

        # Check for unusual patterns
        income = applicant.get('income', 0)
        liabilities = applicant.get('liabilities', 0)
        loan_amount = application.get('loan_amount', 0)
        credit_score = application.get('credit_score', 0)

        # Anomaly 1: High liabilities relative to income
        if income > 0 and liabilities > income * 0.5:
            anomalies.append({
                'type': 'High Debt Load',
                'severity': 'High',
                'details': f'Liabilities ({liabilities}) exceed 50% of annual income ({income})',
                'action': 'Detailed income verification required'
            })

        # Anomaly 2: Large loan request relative to income
        if income > 0 and loan_amount > income * 5:
            anomalies.append({
                'type': 'Excessive Loan Request',
                'severity': 'High',
                'details': f'Loan amount exceeds 5x annual income',
                'action': 'Request lower amount or higher income verification'
            })

        # Anomaly 3: Credit score vs debt mismatch
        if credit_score > 700 and liabilities > income * 0.5:
            anomalies.append({
                'type': 'Credit-Debt Mismatch',
                'severity': 'Medium',
                'details': f'High credit score ({credit_score}) but high debt levels',
                'action': 'Verify income stability and recent payment history'
            })

        # Anomaly 4: Very low credit score with large loan
        if credit_score < 600 and loan_amount > income * 2:
            anomalies.append({
                'type': 'Low Credit + Large Loan',
                'severity': 'Critical',
                'details': f'Credit score {credit_score} with large loan request',
                'action': 'Recommend rejection or significant collateral requirement'
            })

        # Anomaly 5: Recent high-risk employment with significant credit drop
        employment_risk = risk_assessment.get('employment_risk_score') if risk_assessment else None
        if employment_risk and employment_risk > 70:
            anomalies.append({
                'type': 'High Employment Risk',
                'severity': 'High',
                'details': f'Employment risk score: {employment_risk}/100',
                'action': 'Consider lower loan amount or require co-signer'
            })

        return {
            'total_anomalies': len(anomalies),
            'severity_distribution': self.get_severity_distribution(anomalies),
            'anomalies': anomalies
        }

    def get_severity_distribution(self, anomalies):
        """Get distribution of anomaly severities"""
        distribution = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'Low')
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution

    def analyze_financial_risk(self, applicant_id: str) -> Dict[str, Any]:
        """Perform comprehensive financial risk analysis"""
        self.applicant_id = applicant_id

        # Fetch data from database
        data = self.fetch_financial_data(applicant_id)
        if not data or not data['applicant']:
            return {"error": f"Applicant {applicant_id} not found"}

        applicant = data['applicant']
        application = data['application'] or {}

        income = applicant.get('income', 0)
        liabilities = applicant.get('liabilities', 0)
        loan_amount = application.get('loan_amount', 0)
        credit_score = application.get('credit_score', 0)

        # Calculate monthly figures
        monthly_income = income / 12 if income > 0 else 0
        monthly_liabilities = liabilities / 12 if liabilities > 0 else 0

        # Calculate DTI ratio
        dti_ratio, dti_status = self.calculate_dti_ratio(monthly_income, monthly_liabilities)

        # Evaluate risks
        credit_risk = self.evaluate_credit_risk(credit_score)
        loan_amount_risk = self.evaluate_loan_amount_risk(loan_amount, income, credit_score, liabilities)
        anomalies = self.detect_anomalies(data)

        # Overall risk score calculation
        overall_risk_score = self.calculate_overall_risk_score(
            dti_ratio, credit_score, loan_amount_risk, anomalies
        )

        risk_output = {
            "applicant_id": applicant_id,
            "timestamp": datetime.now().isoformat(),
            "financial_overview": {
                "annual_income": income,
                "monthly_income": round(monthly_income, 2),
                "total_liabilities": liabilities,
                "monthly_liabilities": round(monthly_liabilities, 2),
                "requested_loan_amount": loan_amount
            },
            "debt_to_income_analysis": {
                "current_dti_ratio": dti_ratio,
                "current_dti_status": dti_status,
                "interpretation": self.interpret_dti(dti_ratio)
            },
            "credit_score_risk_level": credit_risk,
            "loan_amount_risk_assessment": loan_amount_risk,
            "anomaly_detection": anomalies,
            "overall_financial_risk": {
                "risk_score": overall_risk_score,
                "risk_classification": self.classify_overall_risk(overall_risk_score),
                "confidence_level": round(self.calculate_confidence(data), 1)
            },
            "reasoning": self.generate_reasoning(dti_ratio, credit_score, loan_amount_risk, anomalies),
            "recommendations": self.generate_recommendations(overall_risk_score, credit_risk, loan_amount_risk, anomalies)
        }

        return risk_output

    def calculate_overall_risk_score(self, dti: float, credit_score: int,
                                     loan_risk: Dict, anomalies: Dict) -> int:
        """Calculate overall financial risk score (0-100)"""
        score = 50  # Base score

        # DTI adjustment
        if dti < 0.15:
            score -= 15
        elif dti < 0.30:
            score -= 10
        elif dti < 0.50:
            score -= 5
        elif dti < 0.70:
            score += 10
        else:
            score += 20

        # Credit score adjustment
        if credit_score >= 750:
            score -= 15
        elif credit_score >= 700:
            score -= 10
        elif credit_score >= 650:
            score -= 5
        elif credit_score >= 600:
            score += 5
        else:
            score += 15

        # Loan amount risk adjustment
        score += loan_risk.get('risk_score', 0) - 50

        # Anomaly adjustment
        anomaly_count = anomalies.get('total_anomalies', 0)
        score += anomaly_count * 5

        return max(0, min(100, score))

    def interpret_dti(self, dti: float) -> str:
        """Interpret DTI ratio"""
        if dti < 0.15:
            return "Excellent - Very healthy debt-to-income ratio"
        elif dti < 0.30:
            return "Good - Acceptable debt-to-income ratio"
        elif dti < 0.50:
            return "Acceptable - Moderate debt-to-income ratio"
        elif dti < 0.70:
            return "High - Elevated debt-to-income ratio"
        else:
            return "Very High - Excessive debt-to-income ratio, high default risk"

    def classify_overall_risk(self, score: int) -> str:
        """Classify overall risk level"""
        if score <= 25:
            return "Low Risk"
        elif score <= 50:
            return "Low-Medium Risk"
        elif score <= 75:
            return "High Risk"
        else:
            return "Very High Risk"

    def calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence level based on data completeness"""
        confidence = 100
        if not data.get('applicant'):
            confidence -= 30
        if not data.get('application'):
            confidence -= 20
        if not data.get('risk_assessment'):
            confidence -= 10
        return max(0, confidence)

    def generate_reasoning(self, dti: float, credit_score: int,
                         loan_risk: Dict, anomalies: Dict) -> str:
        """Generate reasoning for the financial risk assessment"""
        reasons = []

        reasons.append(f"DTI ratio: {dti:.1%} - {'healthy' if dti < 0.50 else 'concerning'}")
        reasons.append(f"Credit score: {credit_score} - {'strong' if credit_score >= 700 else 'fair' if credit_score >= 650 else 'weak'}")
        reasons.append(f"Loan amount risk: {loan_risk.get('risk_level', 'Unknown')}")

        if anomalies.get('total_anomalies', 0) > 0:
            reasons.append(f"Detected {anomalies['total_anomalies']} financial anomalies")

        return " | ".join(reasons)

    def generate_recommendations(self, risk_score: int, credit_risk: Dict,
                                loan_risk: Dict, anomalies: Dict) -> list:
        """Generate recommendations"""
        recommendations = []

        if risk_score <= 25:
            recommendations.append("Recommend approval with standard terms")
        elif risk_score <= 50:
            recommendations.append("Recommend approval with possible rate adjustment")
        elif risk_score <= 75:
            recommendations.append("Recommend conditional approval - require additional documentation")
        else:
            recommendations.append("Recommend rejection or require significant collateral")

        if credit_risk.get('score', 0) < 650:
            recommendations.append("Require credit improvement plan or co-signer")

        if loan_risk.get('risk_level') == 'High Risk':
            recommendations.append("Consider reducing loan amount")

        if anomalies.get('total_anomalies', 0) > 2:
            recommendations.append("Conduct detailed income and employment verification")

        return recommendations

    def print_report(self, analysis: Dict[str, Any]):
        """Print formatted financial risk report"""
        print("\n" + "="*80)
        print("FINANCIAL RISK ANALYSIS REPORT")
        print("="*80)

        print(f"\n📋 APPLICANT ID: {analysis.get('applicant_id')}")
        print(f"⏰ ANALYSIS TIME: {analysis.get('timestamp')}")

        overview = analysis.get('financial_overview', {})
        print(f"\n💼 FINANCIAL OVERVIEW:")
        print(f"   Annual Income: ${overview.get('annual_income'):,.2f}")
        print(f"   Monthly Income: ${overview.get('monthly_income'):,.2f}")
        print(f"   Total Liabilities: ${overview.get('total_liabilities'):,.2f}")
        print(f"   Loan Amount Requested: ${overview.get('requested_loan_amount'):,.2f}")

        dti = analysis.get('debt_to_income_analysis', {})
        print(f"\n📊 DEBT-TO-INCOME RATIO:")
        print(f"   Current DTI: {dti.get('current_dti_ratio', 0):.1%}")
        print(f"   Status: {dti.get('current_dti_status')}")
        print(f"   Interpretation: {dti.get('interpretation')}")

        credit = analysis.get('credit_score_risk_level', {})
        print(f"\n💳 CREDIT SCORE RISK:")
        print(f"   Credit Score: {credit.get('score')}")
        print(f"   Risk Level: {credit.get('risk_level')}")
        print(f"   Recommendation: {credit.get('recommendation')}")

        loan = analysis.get('loan_amount_risk_assessment', {})
        print(f"\n💰 LOAN AMOUNT RISK:")
        print(f"   LTI Ratio: {loan.get('loan_to_income_ratio')}")
        print(f"   Risk Level: {loan.get('risk_level')}")
        print(f"   Risk Score: {loan.get('risk_score')}")

        anomalies = analysis.get('anomaly_detection', {})
        print(f"\n⚠️  ANOMALY DETECTION:")
        print(f"   Total Anomalies: {anomalies.get('total_anomalies')}")
        for anomaly in anomalies.get('anomalies', []):
            print(f"   - {anomaly.get('type')} (Severity: {anomaly.get('severity')})")

        overall = analysis.get('overall_financial_risk', {})
        print(f"\n🎯 OVERALL RISK ASSESSMENT:")
        print(f"   Risk Score: {overall.get('risk_score')}/100")
        print(f"   Risk Classification: {overall.get('risk_classification')}")
        print(f"   Confidence Level: {overall.get('confidence_level')}%")

        print(f"\n💡 REASONING: {analysis.get('reasoning')}")

        print(f"\n✅ RECOMMENDATIONS:")
        for rec in analysis.get('recommendations', []):
            print(f"   • {rec}")

        print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',
        'database': 'loan_approval_system'
    }

    agent = FinancialRiskAgent(db_config)

    if not agent.connect_database():
        sys.exit(1)

    try:
        # Example: Analyze first applicant
        applicant_id = 'APP-2026-000001'

        print(f"\n🔍 Analyzing financial risk for {applicant_id}...")
        analysis = agent.analyze_financial_risk(applicant_id)

        if 'error' not in analysis:
            agent.print_report(analysis)

            # Output as JSON
            print(json.dumps(analysis, indent=2, default=str))
        else:
            print(f"❌ {analysis['error']}")

    finally:
        agent.disconnect_database()


if __name__ == "__main__":
    main()
