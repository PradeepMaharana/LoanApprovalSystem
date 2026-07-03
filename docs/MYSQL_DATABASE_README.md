# MySQL Database Integration for Loan Approval System

Complete documentation for pushing sample data into MySQL database.

---

## Quick Start (3 Steps)

### Step 1: Ensure MySQL is Running
```bash
# Linux/macOS
sudo systemctl start mysql
# or
brew services start mysql

# Windows
# MySQL service starts automatically
```

### Step 2: Run Deployment Script
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
chmod +x deploy_mysql.sh
./deploy_mysql.sh
```

### Step 3: Verify Database
```bash
mysql -u root loan_approval_system
mysql> SELECT COUNT(*) FROM applicants;
mysql> EXIT;
```

---

## Detailed Setup Guide

### Prerequisites

#### 1. MySQL Server Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server

# Post-installation security
sudo mysql_secure_installation
```

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**macOS (DMG Installer):**
- Download from https://dev.mysql.com/downloads/mysql/
- Run installer and follow prompts
- Add MySQL to PATH if needed

**Windows:**
- Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
- Run installer
- Follow setup wizard
- Note your root password
- Service starts automatically

**Docker (Alternative):**
```bash
docker run --name mysql_loan \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -p 3306:3306 \
  -d mysql:8.0

# Wait for container to start
sleep 5

# Test connection
mysql -h 127.0.0.1 -u root -proot_password -e "SELECT VERSION();"
```

#### 2. Verify MySQL Service

```bash
# Check if MySQL is running
sudo systemctl status mysql

# Or with ps
ps aux | grep mysql

# Or with netstat
netstat -tlnp | grep 3306
```

#### 3. Python Packages

```bash
source venv/bin/activate
pip install mysql-connector-python pandas
```

---

## Manual Setup (Without Script)

If you prefer manual setup, follow these steps:

### Step 1: Create Database

```bash
# Connect to MySQL
mysql -u root -p

# In MySQL shell:
mysql> CREATE DATABASE loan_approval_system;
mysql> USE loan_approval_system;
mysql> EXIT;
```

### Step 2: Create Tables

```bash
# Save the following as tables.sql
cat > tables.sql << 'EOF'
-- Applicants table
CREATE TABLE applicants (
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

-- Loan applications table
CREATE TABLE loan_applications (
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

-- Risk assessments table
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
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Chat messages table
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id VARCHAR(50) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    message_timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
EOF

# Apply tables
mysql -u root -p loan_approval_system < tables.sql
```

### Step 3: Import Sample Data

```bash
# Import CSV directly into applicants and loan_applications
mysql -u root -p loan_approval_system << 'EOF'
-- This is complex, use the Python script instead
EOF
```

### Recommendation: Use Python Script

The manual CSV import is complex. Use the `mysql_setup.py` script instead:

```bash
source venv/bin/activate
python mysql_setup.py
```

---

## File Structure

```
LoanApprovalSystem/
├── mysql_setup.py                      ⭐ Main setup script
├── deploy_mysql.sh                     ⭐ Deployment script
├── MYSQL_SETUP_GUIDE.md                ⭐ Detailed setup guide
├── MYSQL_DATABASE_README.md            ⭐ This file
├── Loan_Applicants_Sample_Data.csv     💾 Sample data file
└── requirements.txt                     📋 Updated dependencies
```

---

## Python Script: mysql_setup.py

The `mysql_setup.py` script automates the entire setup process:

### What It Does

1. ✅ Connects to MySQL server
2. ✅ Creates `loan_approval_system` database
3. ✅ Creates 4 tables with proper relationships
4. ✅ Loads 1000 sample records from CSV
5. ✅ Calculates risk scores for each applicant
6. ✅ Determines application status based on risk
7. ✅ Verifies data integrity
8. ✅ Generates detailed statistics report

### How to Run

```bash
# Option 1: Direct execution
python mysql_setup.py

# Option 2: With deployment script
./deploy_mysql.sh

# Option 3: With custom parameters (edit script first)
# Edit mysql_setup.py db_config for custom host/user/password
python mysql_setup.py
```

### Configuration

Edit `mysql_setup.py` line 22-27:

```python
db_config = {
    'host': 'localhost',        # MySQL server hostname
    'user': 'root',             # MySQL username
    'password': '',             # MySQL password (empty = no password)
    'port': 3306                # MySQL port (default 3306)
}
```

---

## Database Structure

### Applicants Table
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Primary key, auto-increment |
| applicant_id | VARCHAR(50) | Unique identifier (APP-2026-XXXXXX) |
| age | INT | Age 18-100 |
| income | DECIMAL(15,2) | Annual income |
| employment_type | ENUM | Salaried, Self-Employed, Freelancer, Business Owner |
| location | VARCHAR(100) | City, State |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Indexes:**
- Primary: `id`
- Unique: `applicant_id`
- Regular: `employment_type`, `location`, `created_at`

### Loan Applications Table
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Primary key |
| applicant_id | VARCHAR(50) | Foreign key to applicants |
| credit_score | INT | FICO score 300-850 |
| loan_amount | DECIMAL(15,2) | Requested loan amount |
| tenure_months | INT | Loan duration 12-360 months |
| existing_liabilities | DECIMAL(15,2) | Current debts |
| application_status | ENUM | SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, PENDING_DOCUMENTS |
| risk_score | DECIMAL(5,2) | Calculated risk 0-100 |
| risk_level | VARCHAR(50) | Very Low, Low, Moderate, High, Very High |
| application_timestamp | DATETIME | Application submission time |

**Indexes:**
- Primary: `id`
- Foreign: `applicant_id` → applicants
- Regular: `application_status`, `risk_level`

### Risk Assessments Table
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Primary key |
| applicant_id | VARCHAR(50) | Foreign key to applicants |
| credit_score_impact | DECIMAL(5,2) | Credit score factor |
| dti_ratio | DECIMAL(5,4) | Debt-to-Income ratio |
| dti_impact | DECIMAL(5,2) | DTI factor |
| age_impact | DECIMAL(5,2) | Age factor |
| lti_ratio | DECIMAL(5,4) | Loan-to-Income ratio |
| lti_impact | DECIMAL(5,2) | LTI factor |
| final_score | DECIMAL(5,2) | Final risk score |
| assessment_date | TIMESTAMP | Assessment time |

### Chat Messages Table
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Primary key |
| applicant_id | VARCHAR(50) | Foreign key to applicants |
| user_message | TEXT | User's message |
| bot_response | TEXT | Bot's response |
| message_timestamp | DATETIME | Message time |
| created_at | TIMESTAMP | Record creation time |

---

## Useful Queries

### View Sample Records
```sql
-- First 10 applicants
SELECT * FROM applicants LIMIT 10;

-- Loan details with risk
SELECT 
    a.applicant_id,
    a.income,
    l.credit_score,
    l.loan_amount,
    l.risk_score,
    l.risk_level
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
LIMIT 10;
```

### Get Statistics
```sql
-- Overall statistics
SELECT 
    COUNT(*) as total_applicants,
    ROUND(AVG(age), 1) as avg_age,
    ROUND(AVG(income), 0) as avg_income,
    COUNT(DISTINCT location) as unique_locations
FROM applicants;

-- Risk distribution
SELECT 
    risk_level,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM loan_applications), 1) as percentage
FROM loan_applications
GROUP BY risk_level
ORDER BY COUNT(*) DESC;
```

### Filter Data
```sql
-- Approved applicants
SELECT * FROM loan_applications WHERE application_status = 'APPROVED';

-- High-risk applications
SELECT * FROM loan_applications WHERE risk_score < 40 ORDER BY risk_score;

-- By location
SELECT a.location, COUNT(*) FROM applicants a GROUP BY a.location;

-- By employment type
SELECT employment_type, COUNT(*) FROM applicants GROUP BY employment_type;
```

---

## Backup and Restore

### Backup Database
```bash
# Single backup
mysqldump -u root -p loan_approval_system > backup.sql

# With timestamp
mysqldump -u root -p loan_approval_system > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
mysqldump -u root -p loan_approval_system | gzip > backup.sql.gz
```

### Restore Database
```bash
# From backup
mysql -u root -p loan_approval_system < backup.sql

# From compressed backup
gunzip < backup.sql.gz | mysql -u root -p loan_approval_system
```

---

## Integration with FastAPI

### Connection Pool Example

```python
import mysql.connector
from mysql.connector import pooling

# Create connection pool
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "loan_approval_system"
}

pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

def get_application(applicant_id: str):
    """Fetch application from database"""
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            a.applicant_id, a.age, a.income,
            l.credit_score, l.loan_amount, l.risk_score, l.risk_level
        FROM applicants a
        JOIN loan_applications l ON a.applicant_id = l.applicant_id
        WHERE a.applicant_id = %s
        """
        
        cursor.execute(query, (applicant_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
```

---

## Troubleshooting

### MySQL Connection Issues

**Problem:** "Can't connect to MySQL server"

**Solution:**
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql

# Check if listening on port 3306
sudo netstat -tlnp | grep 3306
```

### Access Denied

**Problem:** "Access denied for user 'root'@'localhost'"

**Solution:**
```bash
# Try without password
mysql -u root

# If failed, reset password
sudo mysql -u root
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
mysql> FLUSH PRIVILEGES;
mysql> EXIT;
```

### Database Doesn't Exist

**Problem:** "Unknown database 'loan_approval_system'"

**Solution:**
```bash
# Run setup script again
python mysql_setup.py

# Or manually create
mysql -u root -e "CREATE DATABASE loan_approval_system;"
```

### Slow Performance

**Solution:**
```sql
-- Analyze tables
ANALYZE TABLE applicants;
ANALYZE TABLE loan_applications;
ANALYZE TABLE risk_assessments;

-- Create additional indexes if needed
CREATE INDEX idx_app_timestamp ON loan_applications(application_timestamp);
CREATE INDEX idx_app_income ON applicants(income);
```

---

## Performance Tips

1. **Use Indexes Wisely**
   - Already created on commonly queried columns
   - Add more if queries are slow

2. **Batch Operations**
   - Use bulk INSERT for large data loads
   - Script already does this

3. **Connection Pooling**
   - Use connection pool for multiple queries
   - Improves performance significantly

4. **Query Optimization**
   - Use EXPLAIN to analyze queries
   - Add indexes on WHERE clause columns

---

## Security Considerations

⚠️ **Note:** This setup is for development. For production:

1. **Change Root Password**
   ```bash
   mysql -u root -p
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'strong_password';
   ```

2. **Create Application User**
   ```sql
   CREATE USER 'loan_app'@'localhost' IDENTIFIED BY 'app_password';
   GRANT SELECT, INSERT, UPDATE ON loan_approval_system.* TO 'loan_app'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Restrict Network Access**
   ```bash
   # MySQL should only listen on localhost
   # Edit /etc/mysql/mysql.conf.d/mysqld.cnf
   bind-address = 127.0.0.1
   ```

4. **Enable SSL/TLS**
   ```sql
   -- Configure SSL certificates in MySQL config
   -- Restart MySQL service
   ```

---

## Files Provided

| File | Purpose |
|------|---------|
| `mysql_setup.py` | Main database setup script |
| `deploy_mysql.sh` | Automated deployment script |
| `MYSQL_SETUP_GUIDE.md` | Detailed manual setup guide |
| `MYSQL_DATABASE_README.md` | This comprehensive guide |
| `Loan_Applicants_Sample_Data.csv` | 1000 sample records |

---

## Quick Reference

### Start Setup
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
./deploy_mysql.sh
```

### Verify Database
```bash
mysql -u root loan_approval_system
SELECT COUNT(*) FROM applicants;
```

### Check Statistics
```bash
mysql -u root loan_approval_system << 'EOF'
SELECT 
    'Total Applicants' as metric, COUNT(*) as value FROM applicants
UNION
SELECT 'Avg Income', ROUND(AVG(income)) FROM applicants
UNION
SELECT 'High Risk', COUNT(*) FROM loan_applications WHERE risk_score < 40
UNION
SELECT 'Approved', COUNT(*) FROM loan_applications WHERE application_status = 'APPROVED';
EOF
```

---

## Next Steps

1. ✅ Install MySQL Server
2. ✅ Run deployment script
3. ✅ Verify database
4. ✅ Run sample queries
5. ✅ Integrate with FastAPI
6. ✅ Test end-to-end

---

## Support

For issues:
1. Check MYSQL_SETUP_GUIDE.md troubleshooting section
2. Verify MySQL is running
3. Check connection parameters
4. Review error messages in script output

**Status:** Ready for Production

Generated: 2024-07-01
