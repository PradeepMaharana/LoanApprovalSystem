"""
Database Service Layer
Handles all CRUD operations for loan approval system
"""

import mysql.connector
from mysql.connector import Error, errorcode
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for database operations"""

    def __init__(self, host='localhost', user='root', password='Tek@12345',
                 database='loan_approval_system', port=3306):
        """Initialize database connection parameters"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self) -> bool:
        """Establish connection to MySQL server"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                auth_plugin='mysql_native_password'
            )
            if self.connection.is_connected():
                logger.info(f"✅ Database connected: {self.database}")
                return True
            return False
        except Error as err:
            logger.error(f"❌ Connection error: {err}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("✅ Database connection closed")

    def insert_applicant(self, applicant_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert new applicant into database

        Args:
            applicant_data: Dict with keys: applicant_id, age, income, employment_type, location

        Returns:
            applicant_id if successful, None otherwise
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return None

        try:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO applicants
            (applicant_id, age, income, employment_type, location, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            now = datetime.now()
            values = (
                applicant_data['applicant_id'],
                applicant_data['age'],
                applicant_data['income'],
                applicant_data['employment_type'],
                applicant_data['location'],
                now,
                now
            )

            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()

            logger.info(f"✅ Applicant inserted: {applicant_data['applicant_id']}")
            return applicant_data['applicant_id']

        except Error as err:
            self.connection.rollback()
            if err.errno == errorcode.ER_DUP_ENTRY:
                logger.warning(f"⚠️  Applicant already exists: {applicant_data.get('applicant_id')}")
            else:
                logger.error(f"❌ Insert error: {err}")
            return None

    def insert_loan_application(self, app_data: Dict[str, Any]) -> bool:
        """
        Insert new loan application into database

        Args:
            app_data: Dict with keys: applicant_id, credit_score, loan_amount,
                      tenure_months, existing_liabilities, risk_score, risk_level

        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return False

        try:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO loan_applications
            (applicant_id, credit_score, loan_amount, tenure_months, existing_liabilities,
             risk_score, risk_level, application_status, application_timestamp, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                credit_score = VALUES(credit_score),
                loan_amount = VALUES(loan_amount),
                tenure_months = VALUES(tenure_months),
                existing_liabilities = VALUES(existing_liabilities),
                risk_score = VALUES(risk_score),
                risk_level = VALUES(risk_level),
                updated_at = VALUES(updated_at)
            """

            now = datetime.now()
            values = (
                app_data['applicant_id'],
                app_data['credit_score'],
                app_data['loan_amount'],
                app_data['tenure_months'],
                app_data.get('existing_liabilities', 0),
                app_data.get('risk_score'),
                app_data.get('risk_level'),
                'SUBMITTED',
                now,
                now,
                now
            )

            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()

            logger.info(f"✅ Loan application inserted: {app_data['applicant_id']}")
            return True

        except Error as err:
            self.connection.rollback()
            logger.error(f"❌ Insert loan application error: {err}")
            return False

    def update_loan_application(self, applicant_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update existing loan application

        Args:
            applicant_id: ID of applicant
            update_data: Dict with fields to update

        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return False

        try:
            cursor = self.connection.cursor()

            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            set_clause += ", updated_at = %s"

            query = f"UPDATE loan_applications SET {set_clause} WHERE applicant_id = %s"

            values = list(update_data.values())
            values.append(datetime.now())
            values.append(applicant_id)

            cursor.execute(query, values)
            self.connection.commit()

            affected = cursor.rowcount
            cursor.close()

            if affected > 0:
                logger.info(f"✅ Loan application updated: {applicant_id}")
                return True
            else:
                logger.warning(f"⚠️  No records updated for: {applicant_id}")
                return False

        except Error as err:
            self.connection.rollback()
            logger.error(f"❌ Update error: {err}")
            return False

    def update_applicant(self, applicant_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update existing applicant

        Args:
            applicant_id: ID of applicant
            update_data: Dict with fields to update (age, income, employment_type, location)

        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return False

        try:
            cursor = self.connection.cursor()

            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            set_clause += ", updated_at = %s"

            query = f"UPDATE applicants SET {set_clause} WHERE applicant_id = %s"

            values = list(update_data.values())
            values.append(datetime.now())
            values.append(applicant_id)

            cursor.execute(query, values)
            self.connection.commit()

            affected = cursor.rowcount
            cursor.close()

            if affected > 0:
                logger.info(f"✅ Applicant updated: {applicant_id}")
                return True
            else:
                logger.warning(f"⚠️  No records updated for: {applicant_id}")
                return False

        except Error as err:
            self.connection.rollback()
            logger.error(f"❌ Update error: {err}")
            return False

    def search_applicants(self, criteria: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search applicants by multiple criteria

        Args:
            criteria: Dict with optional keys: applicant_id, location, age_min, age_max,
                     employment_type, credit_score_min, credit_score_max
            limit: Max results to return

        Returns:
            List of applicant records
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)

            query = """
            SELECT a.*,
                   l.credit_score, l.loan_amount, l.application_status, l.risk_score, l.risk_level
            FROM applicants a
            LEFT JOIN loan_applications l ON a.applicant_id = l.applicant_id
            WHERE 1=1
            """

            params = []

            if 'applicant_id' in criteria and criteria['applicant_id']:
                query += " AND a.applicant_id = %s"
                params.append(criteria['applicant_id'])

            if 'location' in criteria and criteria['location']:
                query += " AND a.location LIKE %s"
                params.append(f"%{criteria['location']}%")

            if 'age_min' in criteria and criteria['age_min'] is not None:
                query += " AND a.age >= %s"
                params.append(criteria['age_min'])

            if 'age_max' in criteria and criteria['age_max'] is not None:
                query += " AND a.age <= %s"
                params.append(criteria['age_max'])

            if 'employment_type' in criteria and criteria['employment_type']:
                query += " AND a.employment_type = %s"
                params.append(criteria['employment_type'])

            if 'credit_score_min' in criteria and criteria['credit_score_min'] is not None:
                query += " AND l.credit_score >= %s"
                params.append(criteria['credit_score_min'])

            if 'credit_score_max' in criteria and criteria['credit_score_max'] is not None:
                query += " AND l.credit_score <= %s"
                params.append(criteria['credit_score_max'])

            if 'application_status' in criteria and criteria['application_status']:
                query += " AND l.application_status = %s"
                params.append(criteria['application_status'])

            query += f" ORDER BY a.created_at DESC LIMIT {limit}"

            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()

            logger.info(f"✅ Search completed: {len(results)} results")
            return results if results else []

        except Error as err:
            logger.error(f"❌ Search error: {err}")
            return []

    def get_applicant_with_application(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete applicant profile with loan application and risk assessment

        Args:
            applicant_id: ID of applicant

        Returns:
            Dict with applicant, application, and risk data, or None
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)

            query = """
            SELECT
                a.*,
                l.credit_score, l.loan_amount, l.tenure_months, l.existing_liabilities,
                l.application_status, l.risk_score, l.risk_level,
                r.income_stability_score, r.employment_risk_score, r.credit_category,
                r.dti_ratio, r.lti_ratio
            FROM applicants a
            LEFT JOIN loan_applications l ON a.applicant_id = l.applicant_id
            LEFT JOIN risk_assessments r ON a.applicant_id = r.applicant_id
            WHERE a.applicant_id = %s
            """

            cursor.execute(query, (applicant_id,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                logger.info(f"✅ Applicant profile retrieved: {applicant_id}")
                return result
            else:
                logger.warning(f"⚠️  Applicant not found: {applicant_id}")
                return None

        except Error as err:
            logger.error(f"❌ Retrieval error: {err}")
            return None

    def search_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search applications by status

        Args:
            status: Application status (SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, etc.)
            limit: Max results

        Returns:
            List of application records
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)

            query = """
            SELECT a.applicant_id, a.age, a.income, a.employment_type, a.location,
                   l.credit_score, l.loan_amount, l.application_status, l.risk_level, l.created_at
            FROM applicants a
            JOIN loan_applications l ON a.applicant_id = l.applicant_id
            WHERE l.application_status = %s
            ORDER BY l.created_at DESC
            LIMIT %s
            """

            cursor.execute(query, (status, limit))
            results = cursor.fetchall()
            cursor.close()

            logger.info(f"✅ Status search completed: {len(results)} results for {status}")
            return results if results else []

        except Error as err:
            logger.error(f"❌ Status search error: {err}")
            return []

    def list_all_applicants(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """
        List all applicants with pagination

        Args:
            page: Page number (1-indexed)
            limit: Records per page

        Returns:
            Dict with page info and applicant list
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return {"page": page, "limit": limit, "total": 0, "data": []}

        try:
            cursor = self.connection.cursor(dictionary=True)

            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM applicants")
            total = cursor.fetchone()['total']

            # Get paginated results
            offset = (page - 1) * limit
            query = """
            SELECT a.*,
                   l.credit_score, l.loan_amount, l.application_status, l.risk_level
            FROM applicants a
            LEFT JOIN loan_applications l ON a.applicant_id = l.applicant_id
            ORDER BY a.created_at DESC
            LIMIT %s OFFSET %s
            """

            cursor.execute(query, (limit, offset))
            results = cursor.fetchall()
            cursor.close()

            return {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit,
                "data": results if results else []
            }

        except Error as err:
            logger.error(f"❌ List error: {err}")
            return {"page": page, "limit": limit, "total": 0, "data": []}

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dict with database statistics
        """
        if not self.connection:
            logger.error("❌ No database connection")
            return {}

        try:
            cursor = self.connection.cursor(dictionary=True)

            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM applicants")
            stats['total_applicants'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM loan_applications")
            stats['total_applications'] = cursor.fetchone()['count']

            cursor.execute("""
                SELECT application_status, COUNT(*) as count
                FROM loan_applications
                GROUP BY application_status
            """)
            stats['applications_by_status'] = {row['application_status']: row['count']
                                               for row in cursor.fetchall()}

            cursor.execute("""
                SELECT employment_type, COUNT(*) as count
                FROM applicants
                GROUP BY employment_type
            """)
            stats['applicants_by_employment'] = {row['employment_type']: row['count']
                                                 for row in cursor.fetchall()}

            cursor.close()
            logger.info("✅ Statistics retrieved")
            return stats

        except Error as err:
            logger.error(f"❌ Statistics error: {err}")
            return {}


# Singleton instance
_db_service = None


def get_db_service() -> DatabaseService:
    """Get or create database service singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
        _db_service.connect()
    return _db_service
