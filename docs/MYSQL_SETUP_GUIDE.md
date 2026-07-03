# MySQL Database Setup Guide

## Overview

Complete guide to set up MySQL database and load 1000 loan applicant records into your system.

---

## Prerequisites

### 1. MySQL Server Installation

#### Ubuntu/Debian
```bash
# Update package manager
sudo apt update

# Install MySQL Server
sudo apt install mysql-server

# Verify installation
mysql --version
```

#### macOS (Homebrew)
```bash
# Install MySQL
brew install mysql

# Start MySQL service
brew services start mysql

# Verify installation
mysql --version
```

#### Windows
1. Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
2. Run installer
3. Choose setup type (Developer Default recommended)
4. Follow installation wizard
5. Configure MySQL Server (port 3306 default)
6. Start MySQL Service

#### Docker (Alternative)
```bash
# Run MySQL in Docker container
docker run --name mysql_loan_db \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -p 3306:3306 \
  -d mysql:8.0

# Verify running
docker ps
```

### 2. Python Packages
```bash
source venv/bin/activate
pip install mysql-connector-python pandas
```

---

## Database Setup Steps

### Step 1: Start MySQL Server

#### Ubuntu/Linux
```bash
# Start MySQL service
sudo systemctl start mysql

# Verify service is running
sudo systemctl status mysql

# Enable on boot (optional)
sudo systemctl enable mysql
```

#### macOS
```bash
# Start MySQL service
brew services start mysql
```

#### Windows
```bash
# MySQL service starts automatically
# Or manually start via Services
net start MySQL80
```

#### Docker
```bash
# Already running if container started
docker exec mysql_loan_db mysqld_version
```

### Step 2: Verify MySQL Connection

```bash
# Connect to MySQL (will prompt for password)
mysql -u root -p

# Or if no password set
mysql -u root

# Inside MySQL, verify:
mysql> SELECT VERSION();
mysql> SHOW DATABASES;
mysql> EXIT;
```

### Step 3: Update Connection Parameters (if needed)

Edit `mysql_setup.py` line with `db_config`:

```python
db_config = {
    'host': 'localhost',        # MySQL server address
    'user': 'root',             # MySQL username
    'password': '',             # MySQL password (empty if not set)
    'port': 3306                # MySQL port (default 3306)
}
```

### Step 4: Run Database Setup Script

```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
source venv/bin/activate

# Run the setup script
python mysql_setup.py
```

**Expected Output:**
```
════════════════════════════════════════════════════════════════════════════════
🗄️  LOAN APPLICANTS SAMPLE DATA - MySQL DATABASE LOADER
════════════════════════════════════════════════════════════════════════════════

🔗 Connecting to MySQL Server...
✅ Successfully connected to MySQL Server version 8.0.35

📦 Creating database...
🗑️  Dropped existing database 'loan_approval_system' (if any)
✅ Created database 'loan_approval_system'
✅ Using database 'loan_approval_system'

📋 Creating tables...
✅ Created table 'applicants'
✅ Created table 'loan_applications'
✅ Created table 'risk_assessments'
✅ Created table 'chat_messages'

📥 Loading sample data...
📖 Loaded 1000 records from /path/to/Loan_Applicants_Sample_Data.csv
📊 Processing data and calculating risk scores...
   Processing record 100/1000
   Processing record 200/1000
   ...
✅ Successfully loaded 1000 records into database

[VERIFICATION REPORT]
...
✅ VERIFICATION COMPLETE - All data loaded successfully!
```

---

## Database Schema

### Table: applicants
Stores applicant profile information

```sql
CREATE TABLE applicants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) UNIQUE NOT NULL,
    age INT NOT NULL,
    income DECIMAL(15, 2) NOT NULL,
    employment_type ENUM('Salaried', 'Self-Employed', 'Freelancer', 'Business Owner'),
    location VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_employment_type (employment_type),
    INDEX idx_location (location)
);
```

**Fields:**
- `id`: Auto-incremented primary key
- `applicant_id`: Unique applicant identifier (APP-2026-XXXXXX)
- `age`: Applicant age (18-100)
- `income`: Annual income in USD
- `employment_type`: Type of employment
- `location`: Geographic location
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

### Table: loan_applications
Stores loan application and risk assessment details

```sql
CREATE TABLE loan_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) NOT NULL UNIQUE,
    credit_score INT NOT NULL,
    loan_amount DECIMAL(15, 2) NOT NULL,
    tenure_months INT NOT NULL,
    existing_liabilities DECIMAL(15, 2) DEFAULT 0,
    application_status ENUM('SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'PENDING_DOCUMENTS'),
    risk_score DECIMAL(5, 2),
    risk_level VARCHAR(50),
    application_timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id),
    INDEX idx_status (application_status),
    INDEX idx_risk_level (risk_level)
);
```

**Fields:**
- `applicant_id`: Reference to applicants table
- `credit_score`: FICO credit score (300-850)
- `loan_amount`: Requested loan amount
- `tenure_months`: Loan duration in months
- `existing_liabilities`: Current debts
- `application_status`: Current status
- `risk_score`: Calculated risk score (0-100)
- `risk_level`: Risk classification
- `application_timestamp`: Application submission time

### Table: risk_assessments
Detailed risk assessment breakdown

```sql
CREATE TABLE risk_assessments (
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
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
```

**Fields:**
- `credit_score_impact`: Credit score factor impact
- `dti_ratio`: Debt-to-Income ratio
- `dti_impact`: DTI factor impact
- `age_impact`: Age factor impact
- `lti_ratio`: Loan-to-Income ratio
- `lti_impact`: LTI factor impact
- `final_score`: Final risk score

### Table: chat_messages
Stores chat interactions

```sql
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    message_timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);
```

---

## Useful MySQL Queries

### View All Applicants
```sql
SELECT applicant_id, age, income, employment_type, location
FROM applicants
LIMIT 10;
```

### View Loan Applications with Risk Assessment
```sql
SELECT 
    a.applicant_id,
    a.age,
    a.income,
    l.credit_score,
    l.loan_amount,
    l.risk_score,
    l.risk_level,
    l.application_status
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
LIMIT 10;
```

### Get Statistics by Status
```sql
SELECT 
    application_status,
    COUNT(*) as count,
    AVG(risk_score) as avg_risk,
    AVG(loan_amount) as avg_loan
FROM loan_applications
GROUP BY application_status;
```

### Get High-Risk Applicants
```sql
SELECT 
    a.applicant_id,
    a.age,
    a.income,
    l.credit_score,
    l.risk_score,
    l.risk_level
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
WHERE l.risk_score < 40
ORDER BY l.risk_score ASC;
```

### Get Approved Applicants
```sql
SELECT 
    a.applicant_id,
    a.age,
    a.income,
    l.loan_amount,
    l.tenure_months,
    l.risk_score
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
WHERE l.application_status = 'APPROVED'
ORDER BY l.risk_score DESC;
```

### Get Employment Type Distribution
```sql
SELECT 
    employment_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM applicants), 1) as percentage
FROM applicants
GROUP BY employment_type
ORDER BY count DESC;
```

### Get Geographic Distribution
```sql
SELECT 
    location,
    COUNT(*) as count
FROM applicants
GROUP BY location
ORDER BY count DESC;
```

### Get Income Statistics by Employment Type
```sql
SELECT 
    employment_type,
    MIN(income) as min_income,
    MAX(income) as max_income,
    AVG(income) as avg_income,
    STDDEV(income) as std_income
FROM applicants
GROUP BY employment_type;
```

### Get Recent Applications
```sql
SELECT 
    a.applicant_id,
    l.application_timestamp,
    l.application_status,
    l.risk_score
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
ORDER BY l.application_timestamp DESC
LIMIT 20;
```

---

## Troubleshooting

### Issue: "Connection refused" or "Can't connect to MySQL"

**Solution:**
```bash
# Check MySQL service status
sudo systemctl status mysql

# Start MySQL if not running
sudo systemctl start mysql

# Verify MySQL is listening on port 3306
sudo netstat -tlnp | grep 3306

# Or using ss command
sudo ss -tlnp | grep 3306
```

### Issue: "Access denied for user 'root'@'localhost'"

**Solution:**
```bash
# Try connecting with no password
mysql -u root

# If that doesn't work, reset password
sudo mysql -u root

# In MySQL shell:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
EXIT;
```

### Issue: "database 'loan_approval_system' already exists"

**Solution:**
```bash
# The script automatically drops the existing database
# This is expected behavior - all data is reloaded fresh

# Or manually drop it:
mysql -u root -p
DROP DATABASE loan_approval_system;
EXIT;
```

### Issue: "mysql-connector-python" not installed

**Solution:**
```bash
source venv/bin/activate
pip install mysql-connector-python
```

### Issue: CSV file not found

**Solution:**
```bash
# Verify file location
ls -la /home/ubuntu/Desktop/LoanApprovalSystem/Loan_Applicants_Sample_Data.csv

# Update path in mysql_setup.py if needed
```

---

## Verification Queries

After setup, run these to verify data:

```bash
mysql -u root -p loan_approval_system

# Count records
mysql> SELECT COUNT(*) FROM applicants;
mysql> SELECT COUNT(*) FROM loan_applications;

# Check status distribution
mysql> SELECT application_status, COUNT(*) FROM loan_applications GROUP BY application_status;

# Check risk levels
mysql> SELECT risk_level, COUNT(*) FROM loan_applications GROUP BY risk_level;

# View sample record
mysql> SELECT * FROM loan_applications LIMIT 1\G

# Get statistics
mysql> SELECT 
    AVG(age) as avg_age,
    AVG(income) as avg_income,
    AVG(credit_score) as avg_credit,
    AVG(loan_amount) as avg_loan
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id;
```

---

## Performance Optimization

### Create Additional Indexes (Optional)
```sql
-- If queries are slow, add these indexes:
CREATE INDEX idx_app_risk ON loan_applications(applicant_id, risk_level);
CREATE INDEX idx_app_status_timestamp ON loan_applications(application_status, application_timestamp);
CREATE INDEX idx_location_employment ON applicants(location, employment_type);
```

### Analyze Table Performance
```sql
ANALYZE TABLE applicants;
ANALYZE TABLE loan_applications;
ANALYZE TABLE risk_assessments;
```

---

## Backup and Restore

### Backup Database
```bash
# Backup entire database
mysqldump -u root -p loan_approval_system > loan_backup.sql

# Backup with timestamp
mysqldump -u root -p loan_approval_system > loan_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database
```bash
# Restore from backup
mysql -u root -p loan_approval_system < loan_backup.sql

# Or restore entire server
mysql -u root -p < loan_backup.sql
```

---

## Integration with Python FastAPI

### Example: Query database in FastAPI

```python
import mysql.connector
from mysql.connector import Error

def get_application(applicant_id: str):
    """Fetch application from database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='loan_approval_system'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            a.applicant_id,
            a.age,
            a.income,
            l.credit_score,
            l.loan_amount,
            l.risk_score,
            l.risk_level,
            l.application_status
        FROM applicants a
        JOIN loan_applications l ON a.applicant_id = l.applicant_id
        WHERE a.applicant_id = %s
        """
        
        cursor.execute(query, (applicant_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return result
        
    except Error as err:
        print(f"Error: {err}")
        return None
```

---

## Summary

✅ MySQL database created and configured  
✅ 4 tables with proper relationships and indexes  
✅ 1000 loan applicant records loaded  
✅ Risk scores calculated for all applicants  
✅ Application status automatically determined  
✅ Ready for production use  

**Status:** Database setup complete and verified

For questions or issues, refer to troubleshooting section above.
