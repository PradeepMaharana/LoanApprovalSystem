"""
MySQL Database Setup and Data Loading Script
Load 1000 loan applicant sample records into MySQL database
"""

import mysql.connector
from mysql.connector import Error, errorcode
import pandas as pd
from datetime import datetime
import os
import sys


class MySQLLoanDatabase:
    """MySQL database handler for loan applications"""

    def __init__(self, host='localhost', user='root', password='Tek@12345', port=3306):
        """Initialize database connection parameters"""
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = 'loan_approval_system'
        self.connection = None
        self.cursor = None

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
                print(f"   Details: {err}")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("❌ Database does not exist")
            else:
                print(f"❌ Error: {err}")
                print(f"   Error Code: {err.errno if hasattr(err, 'errno') else 'N/A'}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"   Error type: {type(e).__name__}")
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
        """Create required tables for loan application system"""
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
                INDEX idx_location (location),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """

            # Loan details table
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
                INDEX idx_risk_level (risk_level),
                INDEX idx_application_timestamp (application_timestamp),
                INDEX idx_credit_score (credit_score)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """

            # Risk assessment table
            create_risk_table = """
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id VARCHAR(50) NOT NULL UNIQUE,
                credit_score_impact DECIMAL(5, 2),
                dti_ratio DECIMAL(5, 4),
                dti_impact DECIMAL(5, 2),
                age_impact DECIMAL(5, 2),
                lti_ratio DECIMAL(5, 4),
                lti_impact DECIMAL(5, 2),
                final_score DECIMAL(5, 2),
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE,
                INDEX idx_final_score (final_score),
                INDEX idx_assessment_date (assessment_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """

            # Execute table creation
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
                    print(f"✅ Created table '{table_name}'")
                except Error as err:
                    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        print(f"⚠️  Table '{table_name}' already exists")
                    else:
                        print(f"❌ Error creating table '{table_name}': {err}")
                        return False

            return True

        except Error as err:
            print(f"❌ Error creating tables: {err}")
            return False

    def load_sample_data(self, csv_file):
        """Load sample data from CSV file into database"""
        try:
            # Read CSV file
            if not os.path.exists(csv_file):
                print(f"❌ CSV file not found: {csv_file}")
                return False

            df = pd.read_csv(csv_file)
            print(f"📖 Loaded {len(df)} records from {csv_file}")

            # Calculate risk scores
            print("\n📊 Processing data and calculating risk scores...")
            risk_data = []

            for idx, row in df.iterrows():
                if (idx + 1) % 100 == 0:
                    print(f"   Processing record {idx + 1}/{len(df)}")

                # Insert into applicants table
                insert_applicant = """
                INSERT INTO applicants (applicant_id, age, income, employment_type, location)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    age=VALUES(age),
                    income=VALUES(income),
                    employment_type=VALUES(employment_type),
                    location=VALUES(location)
                """

                applicant_data = (
                    row['Applicant ID'],
                    int(row['Age']),
                    float(row['Income']),
                    row['Employment Type'],
                    row['Location']
                )

                self.cursor.execute(insert_applicant, applicant_data)

                # Calculate risk score
                risk_score = self._calculate_risk_score(
                    credit_score=int(row['Credit Score']),
                    liabilities=float(row['Existing Liabilities']),
                    income=float(row['Income']),
                    loan_amount=float(row['Loan Amount']),
                    age=int(row['Age'])
                )

                risk_level = self._get_risk_level(risk_score['risk_score'])

                # Insert into loan_applications table
                insert_loan = """
                INSERT INTO loan_applications
                (applicant_id, credit_score, loan_amount, tenure_months,
                 existing_liabilities, risk_score, risk_level, application_timestamp, application_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    credit_score=VALUES(credit_score),
                    loan_amount=VALUES(loan_amount),
                    tenure_months=VALUES(tenure_months),
                    existing_liabilities=VALUES(existing_liabilities),
                    risk_score=VALUES(risk_score),
                    risk_level=VALUES(risk_level),
                    application_timestamp=VALUES(application_timestamp)
                """

                # Determine application status based on risk score
                if risk_score['risk_score'] >= 75:
                    app_status = 'APPROVED'
                elif risk_score['risk_score'] < 20:
                    app_status = 'REJECTED'
                else:
                    app_status = 'UNDER_REVIEW'

                loan_data = (
                    row['Applicant ID'],
                    int(row['Credit Score']),
                    float(row['Loan Amount']),
                    int(row['Tenure (Months)']),
                    float(row['Existing Liabilities']),
                    risk_score['risk_score'],
                    risk_level,
                    row['Application Timestamp'],
                    app_status
                )

                self.cursor.execute(insert_loan, loan_data)

                # Store risk data for later insertion
                risk_data.append({
                    'applicant_id': row['Applicant ID'],
                    'credit_score_impact': risk_score['factors']['credit_score']['impact'],
                    'dti_ratio': risk_score['dti_ratio'],
                    'dti_impact': risk_score['factors']['dti_ratio']['impact'],
                    'age_impact': risk_score['factors']['age']['impact'],
                    'lti_ratio': risk_score['lti_ratio'],
                    'lti_impact': risk_score['factors']['lti_ratio']['impact'],
                    'final_score': risk_score['risk_score']
                })

            # Insert risk assessments
            print("\n💾 Inserting risk assessments...")
            insert_risk = """
            INSERT INTO risk_assessments
            (applicant_id, credit_score_impact, dti_ratio, dti_impact,
             age_impact, lti_ratio, lti_impact, final_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            for risk in risk_data:
                self.cursor.execute(insert_risk, (
                    risk['applicant_id'],
                    risk['credit_score_impact'],
                    risk['dti_ratio'],
                    risk['dti_impact'],
                    risk['age_impact'],
                    risk['lti_ratio'],
                    risk['lti_impact'],
                    risk['final_score']
                ))

            self.connection.commit()
            print(f"✅ Successfully loaded {len(df)} records into database")
            return True

        except Error as err:
            print(f"❌ Error loading data: {err}")
            self.connection.rollback()
            return False
        except Exception as err:
            print(f"❌ Unexpected error: {err}")
            return False

    def _calculate_risk_score(self, credit_score, liabilities, income, loan_amount, age):
        """Calculate risk score (same as API)"""
        score = 100
        factors = {}

        # Credit score factor
        credit_factor = 0
        if credit_score < 600:
            credit_factor = -40
        elif credit_score < 650:
            credit_factor = -30
        elif credit_score < 700:
            credit_factor = -15
        elif credit_score >= 750:
            credit_factor = 5

        score += credit_factor
        factors['credit_score'] = {'impact': credit_factor, 'value': credit_score}

        # DTI ratio
        dti = (liabilities + loan_amount) / income if income > 0 else 1.0
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
        if age < 25 or age > 65:
            age_factor = -15
        elif age > 60:
            age_factor = -5

        score += age_factor
        factors['age'] = {'impact': age_factor, 'value': age}

        # LTI ratio
        lti = loan_amount / income if income > 0 else 10.0
        lti_factor = 0
        if lti > 5:
            lti_factor = -20
        elif lti > 3:
            lti_factor = -10

        score += lti_factor
        factors['lti_ratio'] = {'impact': lti_factor, 'value': lti}

        final_score = max(0, min(100, score))
        return {
            'risk_score': final_score,
            'dti_ratio': dti,
            'lti_ratio': lti,
            'factors': factors
        }

    def _get_risk_level(self, risk_score):
        """Get risk level classification"""
        if risk_score >= 75:
            return "Very Low Risk"
        elif risk_score >= 60:
            return "Low Risk"
        elif risk_score >= 40:
            return "Moderate Risk"
        elif risk_score >= 20:
            return "High Risk"
        else:
            return "Very High Risk"

    def verify_data(self):
        """Verify data was loaded correctly"""
        try:
            print("\n" + "="*80)
            print("📊 DATABASE VERIFICATION REPORT")
            print("="*80)

            # Check applicants count
            self.cursor.execute("SELECT COUNT(*) FROM applicants")
            applicant_count = self.cursor.fetchone()[0]
            print(f"\n✅ Total Applicants: {applicant_count:,}")

            # Check loan applications count
            self.cursor.execute("SELECT COUNT(*) FROM loan_applications")
            loan_count = self.cursor.fetchone()[0]
            print(f"✅ Total Loan Applications: {loan_count:,}")

            # Check application status distribution
            self.cursor.execute("""
                SELECT application_status, COUNT(*) as count
                FROM loan_applications
                GROUP BY application_status
                ORDER BY count DESC
            """)
            print(f"\n📈 Application Status Distribution:")
            for status, count in self.cursor.fetchall():
                percentage = (count / loan_count) * 100
                print(f"   {status}: {count:,} ({percentage:.1f}%)")

            # Check risk level distribution
            self.cursor.execute("""
                SELECT risk_level, COUNT(*) as count
                FROM loan_applications
                GROUP BY risk_level
                ORDER BY COUNT(*) DESC
            """)
            print(f"\n📊 Risk Level Distribution:")
            for level, count in self.cursor.fetchall():
                percentage = (count / loan_count) * 100
                print(f"   {level}: {count:,} ({percentage:.1f}%)")

            # Check employment type distribution
            self.cursor.execute("""
                SELECT employment_type, COUNT(*) as count
                FROM applicants
                GROUP BY employment_type
                ORDER BY count DESC
            """)
            print(f"\n💼 Employment Type Distribution:")
            for emp_type, count in self.cursor.fetchall():
                percentage = (count / applicant_count) * 100
                print(f"   {emp_type}: {count:,} ({percentage:.1f}%)")

            # Check age statistics
            self.cursor.execute("""
                SELECT MIN(age), MAX(age), AVG(age), STDDEV(age)
                FROM applicants
            """)
            min_age, max_age, avg_age, std_age = self.cursor.fetchone()
            print(f"\n👥 Age Statistics:")
            print(f"   Min: {min_age} | Max: {max_age} | Avg: {avg_age:.1f} | Std Dev: {std_age:.2f}")

            # Check income statistics
            self.cursor.execute("""
                SELECT MIN(income), MAX(income), AVG(income), STDDEV(income)
                FROM applicants
            """)
            min_income, max_income, avg_income, std_income = self.cursor.fetchone()
            print(f"\n💰 Income Statistics:")
            print(f"   Min: ${min_income:,.0f} | Max: ${max_income:,.0f}")
            print(f"   Avg: ${avg_income:,.0f} | Std Dev: ${std_income:,.0f}")

            # Check credit score statistics
            self.cursor.execute("""
                SELECT MIN(credit_score), MAX(credit_score), AVG(credit_score), STDDEV(credit_score)
                FROM loan_applications
            """)
            min_credit, max_credit, avg_credit, std_credit = self.cursor.fetchone()
            print(f"\n📊 Credit Score Statistics:")
            print(f"   Min: {min_credit} | Max: {max_credit} | Avg: {avg_credit:.0f} | Std Dev: {std_credit:.2f}")

            # Check loan amount statistics
            self.cursor.execute("""
                SELECT MIN(loan_amount), MAX(loan_amount), AVG(loan_amount), STDDEV(loan_amount)
                FROM loan_applications
            """)
            min_loan, max_loan, avg_loan, std_loan = self.cursor.fetchone()
            print(f"\n💵 Loan Amount Statistics:")
            print(f"   Min: ${min_loan:,.0f} | Max: ${max_loan:,.0f}")
            print(f"   Avg: ${avg_loan:,.0f} | Std Dev: ${std_loan:,.0f}")

            # Check top locations
            self.cursor.execute("""
                SELECT location, COUNT(*) as count
                FROM applicants
                GROUP BY location
                ORDER BY count DESC
                LIMIT 5
            """)
            print(f"\n🗺️  Top 5 Locations:")
            for location, count in self.cursor.fetchall():
                print(f"   {location}: {count}")

            # Check data date range
            self.cursor.execute("""
                SELECT MIN(application_timestamp), MAX(application_timestamp)
                FROM loan_applications
            """)
            min_date, max_date = self.cursor.fetchone()
            print(f"\n📅 Application Timestamp Range:")
            print(f"   From: {min_date}")
            print(f"   To: {max_date}")

            print("\n" + "="*80)
            print("✅ VERIFICATION COMPLETE - All data loaded successfully!")
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
    print("🗄️  LOAN APPLICANTS SAMPLE DATA - MySQL DATABASE LOADER")
    print("="*80 + "\n")

    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Tek@12345',  # MySQL root password
        'port': 3306
    }

    csv_file = '/home/ubuntu/Desktop/LoanApprovalSystem/Loan_Applicants_Sample_Data.csv'

    # Create database instance
    db = MySQLLoanDatabase(**db_config)

    try:
        # Connect to MySQL
        print("🔗 Connecting to MySQL Server...")
        if not db.connect():
            print("❌ Failed to connect to MySQL Server")
            print("\n⚠️  TROUBLESHOOTING:")
            print("   1. Ensure MySQL Server is running")
            print("   2. Check connection parameters (host, user, password)")
            print("   3. Update db_config in this script if needed")
            return False

        # Create database
        print("\n📦 Creating database...")
        if not db.create_database():
            print("❌ Failed to create database")
            return False

        # Create tables
        print("\n📋 Creating tables...")
        if not db.create_tables():
            print("❌ Failed to create tables")
            return False

        # Load sample data
        print("\n📥 Loading sample data...")
        if not db.load_sample_data(csv_file):
            print("❌ Failed to load sample data")
            return False

        # Verify data
        if not db.verify_data():
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
