"""
Enhanced MySQL Database Setup with Advanced Risk Assessment
Includes Income Stability, Employment Risk, Credit History, and Completeness Flags
"""

import mysql.connector
from mysql.connector import Error, errorcode
import pandas as pd
from datetime import datetime
import os
import sys
from advanced_risk_assessment import AdvancedRiskAssessment


class EnhancedMySQLLoanDatabase:
    """Enhanced MySQL database handler with advanced risk assessments"""

    def __init__(self, host='localhost', user='root', password='Tek@12345', port=3306):
        """Initialize database connection parameters"""
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = 'loan_approval_system'
        self.connection = None
        self.cursor = None
        self.assessor = AdvancedRiskAssessment()

    def connect(self):
        """Establish connection to MySQL server"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                auth_plugin='mysql_native_password'
            )

            if self.connection.is_connected():
                db_info = self.connection.server_info
                print(f"✅ Successfully connected to MySQL Server version {db_info}")
                self.cursor = self.connection.cursor()
                return True
            else:
                print("❌ Failed to connect to MySQL Server")
                return False

        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("❌ Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("❌ Database does not exist")
            else:
                print(f"❌ Error: {err}")
            return False

    def create_database(self):
        """Create loan_approval_system database"""
        try:
            self.cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
            print(f"🗑️  Dropped existing database '{self.database}' (if any)")

            self.cursor.execute(f"CREATE DATABASE {self.database}")
            print(f"✅ Created database '{self.database}'")

            self.cursor.execute(f"USE {self.database}")
            print(f"✅ Using database '{self.database}'")
            self.connection.commit()
            return True

        except Error as err:
            print(f"❌ Error creating database: {err}")
            return False

    def create_tables(self):
        """Create required tables with enhanced risk_assessments"""
        try:
            # Main applicants table
            create_applicants_table = """
            CREATE TABLE IF NOT EXISTS applicants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id VARCHAR(50) UNIQUE NOT NULL,
                age INT NOT NULL CHECK (age >= 18 AND age <= 100),
                income DECIMAL(15, 2) NOT NULL,
                employment_type ENUM('Salaried', 'Self-Employed', 'Freelancer', 'Business Owner') NOT NULL,
                location VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_applicant_id (applicant_id),
                INDEX idx_employment_type (employment_type),
                INDEX idx_location (location)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """

            # Loan applications table
            create_loans_table = """
            CREATE TABLE IF NOT EXISTS loan_applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id VARCHAR(50) NOT NULL UNIQUE,
                credit_score INT NOT NULL CHECK (credit_score >= 300 AND credit_score <= 850),
                loan_amount DECIMAL(15, 2) NOT NULL,
                tenure_months INT NOT NULL CHECK (tenure_months >= 12 AND tenure_months <= 360),
                existing_liabilities DECIMAL(15, 2) DEFAULT 0,
                application_status ENUM('SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'PENDING_DOCUMENTS') DEFAULT 'SUBMITTED',
                risk_score DECIMAL(5, 2),
                risk_level VARCHAR(50),
                application_timestamp DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE,
                INDEX idx_status (application_status),
                INDEX idx_risk_level (risk_level)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """

            # Enhanced risk assessments table
            create_risk_table = """
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id VARCHAR(50) NOT NULL UNIQUE,

                -- Basic Risk Factors
                credit_score_impact DECIMAL(5, 2),
                dti_ratio DECIMAL(5, 4),
                dti_impact DECIMAL(5, 2),
                age_impact DECIMAL(5, 2),
                lti_ratio DECIMAL(5, 4),
                lti_impact DECIMAL(5, 2),
                final_score DECIMAL(5, 2),

                -- Income Stability Score
                income_stability_score DECIMAL(5, 2),
                employment_type_factor DECIMAL(5, 2),
                age_factor_stability DECIMAL(5, 2),
                income_factor DECIMAL(5, 2),
                liability_factor DECIMAL(5, 2),

                -- Employment Risk
                employment_risk_score DECIMAL(5, 2),
                employment_type_risk DECIMAL(5, 2),
                age_stage_risk DECIMAL(5, 2),
                income_level_risk DECIMAL(5, 2),
                credit_management_risk DECIMAL(5, 2),

                -- Credit History Summary
                credit_category VARCHAR(50),
                credit_risk_level VARCHAR(50),
                credit_description TEXT,
                credit_recommendation TEXT,
                score_to_next_level INT,
                months_to_rebuild INT,
                credit_percentile DECIMAL(5, 1),

                -- Application Completeness Flags
                all_required_fields_present BOOLEAN DEFAULT TRUE,
                data_consistency_issues JSON,
                missing_fields JSON,
                warning_flags JSON,
                completeness_percentage DECIMAL(5, 2),

                -- Metadata
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assessment_notes TEXT,

                FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE,
                INDEX idx_final_score (final_score),
                INDEX idx_income_stability (income_stability_score),
                INDEX idx_employment_risk (employment_risk_score),
                INDEX idx_completeness (completeness_percentage),
                INDEX idx_assessment_date (assessment_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """

            # Chat messages table
            create_chat_table = """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id VARCHAR(50) NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                message_timestamp DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_applicant_id (applicant_id),
                INDEX idx_message_timestamp (message_timestamp),
                FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """

            tables = {
                'applicants': create_applicants_table,
                'loan_applications': create_loans_table,
                'risk_assessments': create_risk_table,
                'chat_messages': create_chat_table
            }

            for table_name, create_statement in tables.items():
                try:
                    self.cursor.execute(create_statement)
                    self.connection.commit()
                    print(f"✅ Created/Updated table '{table_name}'")
                except Error as err:
                    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        print(f"⚠️  Table '{table_name}' already exists, updating schema...")
                    else:
                        print(f"❌ Error with table '{table_name}': {err}")

            return True

        except Error as err:
            print(f"❌ Error creating tables: {err}")
            return False

    def load_enhanced_data(self, csv_file):
        """Load sample data with enhanced risk assessments"""
        try:
            if not os.path.exists(csv_file):
                print(f"❌ CSV file not found: {csv_file}")
                return False

            df = pd.read_csv(csv_file)
            print(f"📖 Loaded {len(df)} records from {csv_file}")

            print("\n📊 Processing data with enhanced risk assessments...")

            for idx, row in df.iterrows():
                if (idx + 1) % 100 == 0:
                    print(f"   Processing record {idx + 1}/{len(df)}")

                # Prepare applicant data
                applicant_data = {
                    'applicant_id': row['Applicant ID'],
                    'age': int(row['Age']),
                    'income': float(row['Income']),
                    'employment_type': row['Employment Type'],
                    'location': row['Location'],
                    'credit_score': int(row['Credit Score']),
                    'loan_amount': float(row['Loan Amount']),
                    'tenure_months': int(row['Tenure (Months)']),
                    'existing_liabilities': float(row['Existing Liabilities'])
                }

                # Insert into applicants
                insert_applicant = """
                INSERT INTO applicants (applicant_id, age, income, employment_type, location)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    age=VALUES(age), income=VALUES(income),
                    employment_type=VALUES(employment_type), location=VALUES(location)
                """
                self.cursor.execute(insert_applicant, (
                    applicant_data['applicant_id'],
                    applicant_data['age'],
                    applicant_data['income'],
                    applicant_data['employment_type'],
                    applicant_data['location']
                ))

                # Calculate basic risk score
                basic_risk = self._calculate_basic_risk_score(applicant_data)

                # Insert into loan_applications
                app_status = self._determine_app_status(basic_risk['risk_score'])
                insert_loan = """
                INSERT INTO loan_applications
                (applicant_id, credit_score, loan_amount, tenure_months,
                 existing_liabilities, risk_score, risk_level, application_timestamp, application_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    credit_score=VALUES(credit_score), loan_amount=VALUES(loan_amount),
                    tenure_months=VALUES(tenure_months), existing_liabilities=VALUES(existing_liabilities),
                    risk_score=VALUES(risk_score), risk_level=VALUES(risk_level)
                """
                self.cursor.execute(insert_loan, (
                    applicant_data['applicant_id'],
                    applicant_data['credit_score'],
                    applicant_data['loan_amount'],
                    applicant_data['tenure_months'],
                    applicant_data['existing_liabilities'],
                    basic_risk['risk_score'],
                    basic_risk['risk_level'],
                    row['Application Timestamp'],
                    app_status
                ))

                # Generate comprehensive risk assessment
                comprehensive_assessment = self.assessor.generate_comprehensive_risk_summary(applicant_data)

                # Insert into enhanced risk_assessments
                insert_risk = """
                INSERT INTO risk_assessments (
                    applicant_id,
                    credit_score_impact, dti_ratio, dti_impact, age_impact, lti_ratio, lti_impact, final_score,
                    income_stability_score, employment_type_factor, age_factor_stability, income_factor, liability_factor,
                    employment_risk_score, employment_type_risk, age_stage_risk, income_level_risk, credit_management_risk,
                    credit_category, credit_risk_level, credit_description, credit_recommendation,
                    score_to_next_level, months_to_rebuild, credit_percentile,
                    all_required_fields_present, data_consistency_issues, missing_fields, warning_flags, completeness_percentage
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    income_stability_score=VALUES(income_stability_score),
                    employment_risk_score=VALUES(employment_risk_score),
                    completeness_percentage=VALUES(completeness_percentage)
                """

                import json
                self.cursor.execute(insert_risk, (
                    applicant_data['applicant_id'],
                    basic_risk['factors']['credit_score']['impact'],
                    basic_risk['dti_ratio'],
                    basic_risk['factors']['dti_ratio']['impact'],
                    basic_risk['factors']['age']['impact'],
                    basic_risk['lti_ratio'],
                    basic_risk['factors']['lti_ratio']['impact'],
                    basic_risk['risk_score'],
                    comprehensive_assessment['income_stability']['income_stability_score'],
                    comprehensive_assessment['income_stability']['employment_type_factor'],
                    comprehensive_assessment['income_stability']['age_factor'],
                    comprehensive_assessment['income_stability']['income_factor'],
                    comprehensive_assessment['income_stability']['liability_factor'],
                    comprehensive_assessment['employment_risk']['employment_risk_score'],
                    comprehensive_assessment['employment_risk']['employment_type_risk'],
                    comprehensive_assessment['employment_risk']['age_stage_risk'],
                    comprehensive_assessment['employment_risk']['income_level_risk'],
                    comprehensive_assessment['employment_risk']['credit_management_risk'],
                    comprehensive_assessment['credit_history']['credit_category'],
                    comprehensive_assessment['credit_history']['credit_risk_level'],
                    comprehensive_assessment['credit_history']['credit_description'],
                    comprehensive_assessment['credit_history']['credit_recommendation'],
                    comprehensive_assessment['credit_history']['score_to_next_level'],
                    comprehensive_assessment['credit_history']['months_to_rebuild'],
                    comprehensive_assessment['credit_history']['percentile'],
                    comprehensive_assessment['application_completeness']['all_required_fields_present'],
                    json.dumps(comprehensive_assessment['application_completeness']['data_consistency_issues']),
                    json.dumps(comprehensive_assessment['application_completeness']['missing_fields']),
                    json.dumps(comprehensive_assessment['application_completeness']['warning_flags']),
                    comprehensive_assessment['application_completeness']['completeness_percentage']
                ))

            self.connection.commit()
            print(f"✅ Successfully loaded and enhanced {len(df)} records")
            return True

        except Error as err:
            print(f"❌ Error loading data: {err}")
            self.connection.rollback()
            return False
        except Exception as err:
            print(f"❌ Unexpected error: {err}")
            return False

    def _calculate_basic_risk_score(self, data: dict) -> dict:
        """Calculate basic risk score"""
        score = 100
        factors = {}

        # Credit score factor
        credit_factor = 0
        if data['credit_score'] < 600:
            credit_factor = -40
        elif data['credit_score'] < 650:
            credit_factor = -30
        elif data['credit_score'] < 700:
            credit_factor = -15
        elif data['credit_score'] >= 750:
            credit_factor = 5

        score += credit_factor
        factors['credit_score'] = {'impact': credit_factor, 'value': data['credit_score']}

        # DTI ratio
        dti = (data['existing_liabilities'] + data['loan_amount']) / data['income']
        dti_factor = 0
        if dti > 0.6:
            dti_factor = -30
        elif dti > 0.5:
            dti_factor = -20
        elif dti > 0.4:
            dti_factor = -10

        score += dti_factor
        factors['dti_ratio'] = {'impact': dti_factor, 'value': dti}

        # Age factor
        age_factor = 0
        if data['age'] < 25 or data['age'] > 65:
            age_factor = -15
        elif data['age'] > 60:
            age_factor = -5

        score += age_factor
        factors['age'] = {'impact': age_factor, 'value': data['age']}

        # LTI ratio
        lti = data['loan_amount'] / data['income']
        lti_factor = 0
        if lti > 5:
            lti_factor = -20
        elif lti > 3:
            lti_factor = -10

        score += lti_factor
        factors['lti_ratio'] = {'impact': lti_factor, 'value': lti}

        final_score = max(0, min(100, score))

        if final_score >= 75:
            risk_level = "Very Low Risk"
        elif final_score >= 60:
            risk_level = "Low Risk"
        elif final_score >= 40:
            risk_level = "Moderate Risk"
        elif final_score >= 20:
            risk_level = "High Risk"
        else:
            risk_level = "Very High Risk"

        return {
            'risk_score': final_score,
            'risk_level': risk_level,
            'dti_ratio': dti,
            'lti_ratio': lti,
            'factors': factors
        }

    def _determine_app_status(self, risk_score: float) -> str:
        """Determine application status based on risk score"""
        if risk_score >= 75:
            return 'APPROVED'
        elif risk_score < 20:
            return 'REJECTED'
        else:
            return 'UNDER_REVIEW'

    def verify_enhanced_data(self):
        """Verify enhanced data was loaded correctly"""
        try:
            print("\n" + "="*80)
            print("📊 ENHANCED DATABASE VERIFICATION REPORT")
            print("="*80)

            # Check record counts
            self.cursor.execute("SELECT COUNT(*) FROM applicants")
            app_count = self.cursor.fetchone()[0]
            print(f"\n✅ Total Applicants: {app_count:,}")

            self.cursor.execute("SELECT COUNT(*) FROM loan_applications")
            loan_count = self.cursor.fetchone()[0]
            print(f"✅ Total Loan Applications: {loan_count:,}")

            self.cursor.execute("SELECT COUNT(*) FROM risk_assessments")
            risk_count = self.cursor.fetchone()[0]
            print(f"✅ Total Risk Assessments: {risk_count:,}")

            # Income Stability Statistics
            self.cursor.execute("""
                SELECT MIN(income_stability_score), MAX(income_stability_score), AVG(income_stability_score)
                FROM risk_assessments
            """)
            min_is, max_is, avg_is = self.cursor.fetchone()
            print(f"\n💰 Income Stability Scores:")
            print(f"   Min: {min_is:.2f} | Max: {max_is:.2f} | Avg: {avg_is:.2f}")

            # Employment Risk Statistics
            self.cursor.execute("""
                SELECT MIN(employment_risk_score), MAX(employment_risk_score), AVG(employment_risk_score)
                FROM risk_assessments
            """)
            min_er, max_er, avg_er = self.cursor.fetchone()
            print(f"\n🏢 Employment Risk Scores:")
            print(f"   Min: {min_er:.2f} | Max: {max_er:.2f} | Avg: {avg_er:.2f}")

            # Credit Category Distribution
            self.cursor.execute("""
                SELECT credit_category, COUNT(*) as count
                FROM risk_assessments
                GROUP BY credit_category
                ORDER BY count DESC
            """)
            print(f"\n📊 Credit Category Distribution:")
            for category, count in self.cursor.fetchall():
                pct = (count / risk_count) * 100
                print(f"   {category}: {count:,} ({pct:.1f}%)")

            # Application Completeness
            self.cursor.execute("""
                SELECT
                    MIN(completeness_percentage),
                    MAX(completeness_percentage),
                    AVG(completeness_percentage)
                FROM risk_assessments
            """)
            min_comp, max_comp, avg_comp = self.cursor.fetchone()
            print(f"\n✅ Application Completeness:")
            print(f"   Min: {min_comp:.2f}% | Max: {max_comp:.2f}% | Avg: {avg_comp:.2f}%")

            # Records with data consistency issues
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM risk_assessments
                WHERE data_consistency_issues != '[]'
            """)
            consistency_issues = self.cursor.fetchone()[0]
            print(f"\n⚠️  Records with Data Consistency Issues: {consistency_issues:,}")

            # Records with warnings
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM risk_assessments
                WHERE warning_flags != '[]'
            """)
            warnings = self.cursor.fetchone()[0]
            print(f"⚠️  Records with Warning Flags: {warnings:,}")

            print("\n" + "="*80)
            print("✅ VERIFICATION COMPLETE - All enhanced data loaded successfully!")
            print("="*80 + "\n")
            return True

        except Error as err:
            print(f"❌ Error verifying data: {err}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("✅ MySQL connection closed")


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("🗄️  ENHANCED LOAN APPLICANTS - MySQL DATABASE LOADER")
    print("   (Income Stability, Employment Risk, Credit History, Completeness)")
    print("="*80 + "\n")

    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',
        'port': 3306
    }

    csv_file = '/home/ubuntu/Desktop/LoanApprovalSystem/Loan_Applicants_Sample_Data.csv'

    db = EnhancedMySQLLoanDatabase(**db_config)

    try:
        print("🔗 Connecting to MySQL Server...")
        if not db.connect():
            print("❌ Failed to connect to MySQL Server")
            return False

        print("\n📦 Creating enhanced database and tables...")
        if not db.create_database():
            print("❌ Failed to create database")
            return False

        if not db.create_tables():
            print("❌ Failed to create tables")
            return False

        print("\n📥 Loading sample data with enhanced risk assessments...")
        if not db.load_enhanced_data(csv_file):
            print("❌ Failed to load data")
            return False

        if not db.verify_enhanced_data():
            print("❌ Failed to verify data")
            return False

        print("✨ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        return True

    except Exception as err:
        print(f"❌ Unexpected error: {err}")
        return False

    finally:
        db.disconnect()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
