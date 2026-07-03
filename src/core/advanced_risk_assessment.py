"""
Advanced Risk Assessment Logic
Income Stability Score, Employment Risk, Credit History Summary, Application Completeness
"""

import pandas as pd
from datetime import datetime


class AdvancedRiskAssessment:
    """Calculate advanced risk factors for loan applications"""

    def __init__(self):
        self.income_stability_factors = {
            'Salaried': 0.95,           # Most stable
            'Self-Employed': 0.65,      # Moderate stability
            'Freelancer': 0.50,         # Lower stability
            'Business Owner': 0.70      # Mixed stability
        }

    def calculate_income_stability_score(self, employment_type: str, age: int,
                                        income: float, liabilities: float) -> dict:
        """
        Calculate income stability score (0-100)

        Factors:
        - Employment type stability (base)
        - Age/Experience (younger = lower)
        - Income level (higher income = more stability)
        - Liabilities (high liabilities = less stable)
        """
        score = 50  # Base score

        # 1. Employment type factor (±30 points)
        employment_factor = self.income_stability_factors.get(employment_type, 0.65)
        score += (employment_factor * 30)

        # 2. Age factor (±20 points) - Experience
        if age < 25:
            age_factor = -15  # Younger, less experience
        elif age < 35:
            age_factor = -5
        elif age < 55:
            age_factor = 15   # Peak earning years
        elif age < 65:
            age_factor = 5
        else:
            age_factor = -10  # Nearing retirement
        score += age_factor

        # 3. Income level factor (±15 points)
        if income < 40000:
            income_factor = -10  # Lower income = less stable
        elif income < 80000:
            income_factor = 0
        elif income < 150000:
            income_factor = 10
        else:
            income_factor = 15   # Higher income = more stable
        score += income_factor

        # 4. Liabilities factor (±15 points)
        liability_ratio = liabilities / max(income, 1)
        if liability_ratio > 0.5:
            liability_factor = -15  # High liabilities = unstable
        elif liability_ratio > 0.3:
            liability_factor = -8
        elif liability_ratio > 0.15:
            liability_factor = -2
        else:
            liability_factor = 5     # Low liabilities = stable
        score += liability_factor

        final_score = max(0, min(100, score))

        return {
            'income_stability_score': round(final_score, 2),
            'employment_type_factor': employment_factor,
            'age_factor': age_factor,
            'income_factor': income_factor,
            'liability_factor': liability_factor
        }

    def calculate_employment_risk(self, employment_type: str, age: int,
                                  income: float, credit_score: int) -> dict:
        """
        Calculate employment risk score (0-100, higher = more risk)

        Factors:
        - Employment type stability
        - Age/Career stage
        - Income consistency indicators
        - Credit history management
        """
        risk = 50  # Base risk

        # 1. Employment type risk (±25 points)
        employment_risks = {
            'Salaried': 15,          # Lower risk
            'Self-Employed': 40,     # Higher risk
            'Freelancer': 50,        # Highest risk
            'Business Owner': 35     # High risk
        }
        employment_risk = employment_risks.get(employment_type, 40)
        risk = risk - 25 + employment_risk

        # 2. Age/Career stage risk (±20 points)
        if age < 22:
            age_risk = 20  # Very new to workforce
        elif age < 30:
            age_risk = 10  # Early career, may change jobs
        elif age < 45:
            age_risk = 5   # Stable career
        elif age < 60:
            age_risk = 8   # Mid-career
        else:
            age_risk = 25  # Near retirement risk
        risk = risk - 10 + age_risk

        # 3. Income level risk (±15 points)
        if income < 30000:
            income_risk = 20  # Very low income = unstable
        elif income < 60000:
            income_risk = 10
        elif income < 150000:
            income_risk = 2   # Stable middle income
        else:
            income_risk = -5  # Higher income = lower risk
        risk = risk - 7 + income_risk

        # 4. Credit management risk (±15 points)
        if credit_score < 600:
            credit_risk = 20  # Poor credit management
        elif credit_score < 650:
            credit_risk = 12
        elif credit_score < 700:
            credit_risk = 5
        elif credit_score < 750:
            credit_risk = 0
        else:
            credit_risk = -8  # Excellent credit = lower employment risk
        risk = risk - 7 + credit_risk

        final_risk = max(0, min(100, risk))

        return {
            'employment_risk_score': round(final_risk, 2),
            'employment_type_risk': employment_risk,
            'age_stage_risk': age_risk,
            'income_level_risk': income_risk,
            'credit_management_risk': credit_risk
        }

    def calculate_credit_history_summary(self, credit_score: int) -> dict:
        """
        Summarize credit history based on credit score

        Credit categories:
        - Poor (300-579): High risk
        - Fair (580-669): Moderate risk
        - Good (670-739): Good standing
        - Very Good (740-799): Strong standing
        - Excellent (800-850): Excellent standing
        """
        if credit_score < 580:
            category = 'Poor'
            risk_level = 'Very High'
            description = 'Significant credit management issues'
            recommendation = 'Consider requiring co-signer or secured loan'
            rebuild_score = 580
            months_to_rebuild = 24
        elif credit_score < 670:
            category = 'Fair'
            risk_level = 'High'
            description = 'Several missed payments or high debt levels'
            recommendation = 'Require higher interest rate or down payment'
            rebuild_score = 670
            months_to_rebuild = 18
        elif credit_score < 740:
            category = 'Good'
            risk_level = 'Moderate'
            description = 'Decent credit management with some issues'
            recommendation = 'Standard approval with market rate'
            rebuild_score = 740
            months_to_rebuild = 12
        elif credit_score < 800:
            category = 'Very Good'
            risk_level = 'Low'
            description = 'Strong credit management and payment history'
            recommendation = 'Favorable terms and lower interest rate'
            rebuild_score = 800
            months_to_rebuild = 6
        else:
            category = 'Excellent'
            risk_level = 'Very Low'
            description = 'Excellent credit management and payment history'
            recommendation = 'Best available terms and rates'
            rebuild_score = 850
            months_to_rebuild = 0

        score_to_next = rebuild_score - credit_score
        score_pct_of_range = ((credit_score - 300) / 550) * 100

        return {
            'credit_category': category,
            'credit_risk_level': risk_level,
            'credit_description': description,
            'credit_recommendation': recommendation,
            'score_to_next_level': max(0, score_to_next),
            'months_to_rebuild': months_to_rebuild,
            'percentile': round(score_pct_of_range, 1)
        }

    def calculate_application_completeness_flags(self, applicant_data: dict) -> dict:
        """
        Calculate application completeness flags
        Identifies missing or incomplete information
        """
        flags = {
            'all_required_fields_present': True,
            'data_consistency_issues': [],
            'missing_fields': [],
            'warning_flags': [],
            'completeness_percentage': 100.0
        }

        required_fields = [
            'applicant_id', 'age', 'income', 'employment_type', 'location',
            'credit_score', 'loan_amount', 'tenure_months', 'existing_liabilities'
        ]

        # Check for missing fields
        missing = []
        for field in required_fields:
            if field not in applicant_data or applicant_data[field] is None or applicant_data[field] == '':
                missing.append(field)
                flags['all_required_fields_present'] = False

        flags['missing_fields'] = missing

        # Check data consistency
        consistency_issues = []

        # Income vs Loan amount consistency
        if 'income' in applicant_data and 'loan_amount' in applicant_data:
            income = applicant_data.get('income', 0)
            loan = applicant_data.get('loan_amount', 0)
            if loan > income * 10:
                consistency_issues.append('Loan amount unusually high relative to income')

        # Age vs Employment
        if 'age' in applicant_data and 'employment_type' in applicant_data:
            age = applicant_data.get('age', 0)
            emp_type = applicant_data.get('employment_type', '')
            if age < 22 and emp_type == 'Business Owner':
                consistency_issues.append('Business owner status unlikely at young age')

        # Liabilities vs Income
        if 'income' in applicant_data and 'existing_liabilities' in applicant_data:
            income = applicant_data.get('income', 0)
            liabilities = applicant_data.get('existing_liabilities', 0)
            if liabilities > income * 2:
                consistency_issues.append('Liabilities extremely high relative to income')

        flags['data_consistency_issues'] = consistency_issues

        # Set warning flags
        warning_flags = []
        if 'age' in applicant_data:
            age = applicant_data.get('age', 0)
            if age < 25:
                warning_flags.append('Applicant age below 25 - may indicate limited credit history')
            if age > 65:
                warning_flags.append('Applicant age above 65 - near retirement')

        if 'income' in applicant_data:
            income = applicant_data.get('income', 0)
            if income < 30000:
                warning_flags.append('Low income level - may impact repayment ability')

        if 'existing_liabilities' in applicant_data:
            liabilities = applicant_data.get('existing_liabilities', 0)
            if liabilities == 0:
                warning_flags.append('No existing liabilities - limited credit history')

        if 'credit_score' in applicant_data:
            credit = applicant_data.get('credit_score', 0)
            if credit < 650:
                warning_flags.append('Credit score below 650 - high risk')

        flags['warning_flags'] = warning_flags

        # Calculate completeness percentage
        if missing:
            flags['completeness_percentage'] = round(
                ((len(required_fields) - len(missing)) / len(required_fields)) * 100, 2
            )

        return flags

    def generate_comprehensive_risk_summary(self, applicant_data: dict) -> dict:
        """
        Generate comprehensive risk summary combining all factors
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'applicant_id': applicant_data.get('applicant_id', 'N/A')
        }

        # Income Stability
        income_stability = self.calculate_income_stability_score(
            employment_type=applicant_data.get('employment_type', 'Salaried'),
            age=applicant_data.get('age', 45),
            income=applicant_data.get('income', 50000),
            liabilities=applicant_data.get('existing_liabilities', 0)
        )
        summary['income_stability'] = income_stability

        # Employment Risk
        employment_risk = self.calculate_employment_risk(
            employment_type=applicant_data.get('employment_type', 'Salaried'),
            age=applicant_data.get('age', 45),
            income=applicant_data.get('income', 50000),
            credit_score=applicant_data.get('credit_score', 680)
        )
        summary['employment_risk'] = employment_risk

        # Credit History
        credit_summary = self.calculate_credit_history_summary(
            credit_score=applicant_data.get('credit_score', 680)
        )
        summary['credit_history'] = credit_summary

        # Application Completeness
        completeness = self.calculate_application_completeness_flags(applicant_data)
        summary['application_completeness'] = completeness

        return summary


# Example usage
if __name__ == "__main__":
    # Test the assessment
    assessor = AdvancedRiskAssessment()

    test_applicant = {
        'applicant_id': 'APP-2026-000001',
        'age': 35,
        'income': 120000,
        'employment_type': 'Salaried',
        'location': 'New York, NY',
        'credit_score': 750,
        'loan_amount': 300000,
        'tenure_months': 360,
        'existing_liabilities': 50000
    }

    result = assessor.generate_comprehensive_risk_summary(test_applicant)
    print("Comprehensive Risk Assessment:")
    print("=" * 80)
    import json
    print(json.dumps(result, indent=2))
