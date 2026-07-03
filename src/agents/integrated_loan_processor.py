#!/usr/bin/env python3

"""
Integrated Loan Processor
Orchestrates all four agents for end-to-end loan processing:
1. Applicant Profile Agent
2. Financial Risk Analysis Agent
3. Loan Decision Agent
4. Compliance & Action Orchestrator Agent
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any

from applicant_profile_agent import ApplicantProfileAgent
from financial_risk_agent import FinancialRiskAgent
from loan_decision_agent import LoanDecisionAgent
from compliance_action_agent import ComplianceActionOrchestrator

class IntegratedLoanProcessor:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.applicant_profile_agent = ApplicantProfileAgent(db_config)
        self.financial_risk_agent = FinancialRiskAgent(db_config)
        self.loan_decision_agent = LoanDecisionAgent(db_config)
        self.compliance_agent = ComplianceActionOrchestrator(db_config)

        self.profile_data = None
        self.risk_data = None
        self.decision_data = None
        self.orchestration_data = None

    def connect_all_agents(self) -> bool:
        """Connect all agents to database"""
        if not self.applicant_profile_agent.connect_database():
            return False
        print("✅ Applicant Profile Agent connected")

        if not self.financial_risk_agent.connect_database():
            return False
        print("✅ Financial Risk Agent connected")

        if not self.loan_decision_agent.connect_database():
            return False
        print("✅ Loan Decision Agent connected")

        if not self.compliance_agent.connect_database():
            return False
        print("✅ Compliance Agent connected")

        return True

    def disconnect_all_agents(self):
        """Disconnect all agents"""
        self.applicant_profile_agent.disconnect_database()
        self.financial_risk_agent.disconnect_database()
        self.loan_decision_agent.disconnect_database()
        self.compliance_agent.disconnect_database()

    def process_loan_application(self, applicant_id: str) -> Dict[str, Any]:
        """Process complete loan application through all agents"""
        print(f"\n{'='*80}")
        print(f"INTEGRATED LOAN PROCESSING - APPLICANT {applicant_id}")
        print(f"{'='*80}")

        start_time = datetime.now()

        # Step 1: Applicant Profile Analysis
        print(f"\n🔍 STEP 1: APPLICANT PROFILE ANALYSIS")
        print("-" * 80)
        self.profile_data = self.applicant_profile_agent.analyze_applicant_profile(applicant_id)

        if 'error' in self.profile_data:
            print(f"❌ {self.profile_data['error']}")
            return {"error": self.profile_data['error']}

        print(f"✅ Profile analysis completed")
        print(f"   Income Stability Score: {self.profile_data['income_stability_score']['score']}")
        print(f"   Employment Risk: {self.profile_data['employment_risk']['risk_level']}")
        print(f"   Credit Category: {self.profile_data['credit_history_summary']['category']}")
        print(f"   Application Completeness: {self.profile_data['application_completeness']['completion_percentage']}%")

        # Step 2: Financial Risk Analysis
        print(f"\n📊 STEP 2: FINANCIAL RISK ANALYSIS")
        print("-" * 80)
        self.risk_data = self.financial_risk_agent.analyze_financial_risk(applicant_id)

        print(f"✅ Risk analysis completed")
        print(f"   DTI Ratio: {self.risk_data['debt_to_income_analysis']['current_dti_ratio']:.1%}")
        print(f"   Credit Risk Level: {self.risk_data['credit_score_risk_level']['risk_level']}")
        print(f"   Loan Amount Risk: {self.risk_data['loan_amount_risk_assessment']['risk_level']}")
        print(f"   Anomalies Detected: {self.risk_data['anomaly_detection']['total_anomalies']}")
        print(f"   Overall Risk Score: {self.risk_data['overall_financial_risk']['risk_score']}/100")

        # Step 3: Loan Decision Synthesis
        print(f"\n🎯 STEP 3: LOAN DECISION SYNTHESIS")
        print("-" * 80)
        self.decision_data = self.loan_decision_agent.synthesize_loan_decision(applicant_id)

        print(f"✅ Decision synthesis completed")
        print(f"   Classification: {self.decision_data['decision']['classification']}")
        print(f"   Risk Score: {self.decision_data['decision']['risk_score']}/100")
        print(f"   Confidence Level: {self.decision_data['decision']['confidence_level']}%")
        print(f"   Recommended Interest Rate: {self.decision_data['financial_breakdown']['recommended_interest_rate']}%")
        print(f"   Estimated Monthly Payment: ${self.decision_data['financial_breakdown']['estimated_monthly_payment']:,.2f}")

        # Step 4: Compliance & Action Orchestration
        print(f"\n⚙️  STEP 4: COMPLIANCE & ACTION ORCHESTRATION")
        print("-" * 80)
        self.orchestration_data = self.compliance_agent.orchestrate_action(applicant_id, self.decision_data)

        print(f"✅ Action orchestration completed")
        print(f"   Case ID: {self.orchestration_data['case_id']}")
        print(f"   Action Type: {self.orchestration_data['action_type']}")
        print(f"   Actions Taken: {len(self.orchestration_data['actions_taken'])}")
        print(f"   Notifications Sent: {len(self.orchestration_data['notifications_sent'])}")

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Generate comprehensive report
        comprehensive_report = {
            "processing_summary": {
                "applicant_id": applicant_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "processing_time_seconds": processing_time,
                "status": "COMPLETED"
            },
            "stage_1_applicant_profile": self.profile_data,
            "stage_2_financial_risk": self.risk_data,
            "stage_3_loan_decision": self.decision_data,
            "stage_4_compliance_action": self.orchestration_data,
            "final_recommendation": self.generate_final_recommendation()
        }

        return comprehensive_report

    def generate_final_recommendation(self) -> Dict[str, Any]:
        """Generate final recommendation summary"""
        if not all([self.profile_data, self.risk_data, self.decision_data]):
            return {"error": "Incomplete processing data"}

        return {
            "final_decision": self.decision_data['decision']['classification'],
            "overall_assessment": {
                "applicant_creditworthiness": self.profile_data['credit_history_summary']['category'],
                "financial_health": self.risk_data['overall_financial_risk']['risk_classification'],
                "decision_confidence": self.decision_data['decision']['confidence_level'],
                "processing_confidence": self.risk_data['overall_financial_risk']['confidence_level']
            },
            "key_strengths": self.extract_strengths(),
            "key_concerns": self.extract_concerns(),
            "recommended_action": self.decision_data['recommendation_for_processor'],
            "next_processing_steps": self.orchestration_data['next_steps']
        }

    def extract_strengths(self) -> list:
        """Extract key strengths from analysis"""
        strengths = []

        if isinstance(self.profile_data['income_stability_score']['score'], (int, float)):
            if self.profile_data['income_stability_score']['score'] >= 70:
                strengths.append("Strong income stability")

        if self.risk_data['credit_score_risk_level']['score'] >= 700:
            strengths.append("Good credit score")

        if self.risk_data['debt_to_income_analysis']['current_dti_ratio'] < 0.50:
            strengths.append("Healthy debt-to-income ratio")

        if self.decision_data['decision']['risk_score'] >= 70:
            strengths.append("Strong overall risk profile")

        return strengths or ["Profile meets basic requirements"]

    def extract_concerns(self) -> list:
        """Extract key concerns from analysis"""
        concerns = []

        if isinstance(self.profile_data['income_stability_score']['score'], (int, float)):
            if self.profile_data['income_stability_score']['score'] < 50:
                concerns.append("Income stability concerns")

        if self.risk_data['credit_score_risk_level']['score'] < 650:
            concerns.append("Credit score below standard threshold")

        if self.risk_data['debt_to_income_analysis']['current_dti_ratio'] > 0.50:
            concerns.append("Elevated debt-to-income ratio")

        if self.risk_data['anomaly_detection']['total_anomalies'] > 0:
            concerns.append(f"{self.risk_data['anomaly_detection']['total_anomalies']} financial anomalies detected")

        return concerns or ["No major concerns identified"]

    def print_comprehensive_report(self, report: Dict[str, Any]):
        """Print comprehensive end-to-end report"""
        print(f"\n\n{'='*80}")
        print("INTEGRATED LOAN PROCESSING - COMPREHENSIVE REPORT")
        print(f"{'='*80}")

        summary = report.get('processing_summary', {})
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"   Applicant ID: {summary.get('applicant_id')}")
        print(f"   Status: {summary.get('status')}")
        print(f"   Processing Time: {summary.get('processing_time_seconds'):.1f} seconds")

        print(f"\n🏁 FINAL DECISION: {report['final_recommendation'].get('final_decision')}")
        print(f"   Confidence: {report['final_recommendation'].get('overall_assessment', {}).get('decision_confidence')}%")

        print(f"\n✅ KEY STRENGTHS:")
        for strength in report['final_recommendation'].get('key_strengths', []):
            print(f"   • {strength}")

        print(f"\n⚠️  KEY CONCERNS:")
        for concern in report['final_recommendation'].get('key_concerns', []):
            print(f"   • {concern}")

        print(f"\n👤 APPLICANT PROFILE INSIGHTS:")
        profile = report.get('stage_1_applicant_profile', {})
        print(f"   Name: {profile.get('applicant_info', {}).get('name')}")
        print(f"   Age: {profile.get('applicant_info', {}).get('age')}")
        print(f"   Income: ${profile.get('applicant_info', {}).get('annual_income'):,.2f}")
        print(f"   Application Completeness: {profile.get('application_completeness', {}).get('completion_percentage')}%")

        print(f"\n📈 FINANCIAL HEALTH:")
        risk = report.get('stage_2_financial_risk', {})
        print(f"   DTI Ratio: {risk.get('debt_to_income_analysis', {}).get('current_dti_ratio', 'N/A'):.1%}")
        print(f"   Overall Risk: {risk.get('overall_financial_risk', {}).get('risk_classification')}")
        print(f"   Anomalies: {risk.get('anomaly_detection', {}).get('total_anomalies')} detected")

        print(f"\n💰 LOAN TERMS:")
        decision = report.get('stage_3_loan_decision', {})
        financial = decision.get('financial_breakdown', {})
        print(f"   Loan Amount: ${financial.get('requested_loan_amount', 0):,.2f}")
        print(f"   Interest Rate: {financial.get('recommended_interest_rate')}%")
        print(f"   Term: {financial.get('recommended_term')}")
        print(f"   Monthly Payment: ${financial.get('estimated_monthly_payment', 0):,.2f}")

        print(f"\n🎯 ACTION TAKEN:")
        orchestration = report.get('stage_4_compliance_action', {})
        print(f"   Case ID: {orchestration.get('case_id')}")
        print(f"   Actions Executed: {len(orchestration.get('actions_taken', []))}")
        print(f"   Notifications Sent: {len(orchestration.get('notifications_sent', []))}")

        print(f"\n🔄 NEXT STEPS:")
        for i, step in enumerate(report['final_recommendation'].get('next_processing_steps', []), 1):
            print(f"   {i}. {step}")

        print(f"\n{'='*80}\n")


def main():
    """Main execution"""
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',
        'database': 'loan_approval_system'
    }

    processor = IntegratedLoanProcessor(db_config)

    if not processor.connect_all_agents():
        print("❌ Failed to connect to database")
        sys.exit(1)

    try:
        # Process multiple applicants
        applicant_ids = [
            'APP-2026-000001',
            'APP-2026-000002',
            'APP-2026-000003'
        ]

        all_reports = {}

        for applicant_id in applicant_ids:
            print(f"\n\n{'*'*80}")
            print(f"PROCESSING APPLICANT: {applicant_id}")
            print(f"{'*'*80}")

            report = processor.process_loan_application(applicant_id)

            if 'error' not in report:
                processor.print_comprehensive_report(report)
                all_reports[applicant_id] = report

                # Save individual report as JSON
                with open(f"report_{applicant_id}.json", 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"✅ Report saved to report_{applicant_id}.json")
            else:
                print(f"❌ Processing failed: {report['error']}")

        # Print summary of all processed applications
        print(f"\n\n{'='*80}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Total Applicants Processed: {len(all_reports)}")

        approved_count = sum(1 for r in all_reports.values()
                           if r.get('final_recommendation', {}).get('final_decision') == 'APPROVE')
        rejected_count = sum(1 for r in all_reports.values()
                           if r.get('final_recommendation', {}).get('final_decision') == 'REJECT')
        review_count = sum(1 for r in all_reports.values()
                         if r.get('final_recommendation', {}).get('final_decision') == 'REVIEW')

        print(f"\nDecision Breakdown:")
        print(f"   ✅ Approved: {approved_count}")
        print(f"   ❌ Rejected: {rejected_count}")
        print(f"   ⏳ Under Review: {review_count}")

        # Save comprehensive summary
        with open("batch_processing_summary.json", 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_processed": len(all_reports),
                "approved": approved_count,
                "rejected": rejected_count,
                "under_review": review_count,
                "reports": all_reports
            }, f, indent=2, default=str)
        print(f"\n✅ Batch summary saved to batch_processing_summary.json")

    finally:
        processor.disconnect_all_agents()


if __name__ == "__main__":
    main()
