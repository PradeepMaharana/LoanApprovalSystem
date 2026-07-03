#!/bin/bash

# MySQL Database Deployment Script
# Automates MySQL setup and data loading

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║              MySQL DATABASE DEPLOYMENT SCRIPT FOR LOAN APPROVAL SYSTEM         ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if MySQL is installed
echo -e "${BLUE}📋 Checking MySQL installation...${NC}"
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}❌ MySQL is not installed${NC}"
    echo ""
    echo "Install MySQL using:"
    echo "  Ubuntu/Debian: sudo apt install mysql-server"
    echo "  macOS: brew install mysql"
    echo "  Windows: Download from https://dev.mysql.com/downloads/mysql/"
    echo ""
    exit 1
fi

MYSQL_VERSION=$(mysql --version)
echo -e "${GREEN}✅ MySQL found: ${MYSQL_VERSION}${NC}"

# Check if MySQL service is running
echo ""
echo -e "${BLUE}🔍 Checking MySQL service status...${NC}"
if ! pgrep -x "mysqld" > /dev/null; then
    echo -e "${YELLOW}⚠️  MySQL service is not running${NC}"
    echo ""
    echo "Starting MySQL service..."

    # Try to start MySQL (may require sudo on some systems)
    if command -v systemctl &> /dev/null; then
        sudo systemctl start mysql || sudo systemctl start mysqld || true
    elif command -v brew &> /dev/null; then
        brew services start mysql || true
    fi

    sleep 2

    if pgrep -x "mysqld" > /dev/null; then
        echo -e "${GREEN}✅ MySQL service started${NC}"
    else
        echo -e "${RED}❌ Failed to start MySQL service${NC}"
        echo "Please start MySQL manually and run this script again"
        exit 1
    fi
else
    echo -e "${GREEN}✅ MySQL service is running${NC}"
fi

# Check Python virtual environment
echo ""
echo -e "${BLUE}🐍 Checking Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found, creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Install required packages
echo ""
echo -e "${BLUE}📦 Installing required Python packages...${NC}"
pip install -q mysql-connector-python pandas
echo -e "${GREEN}✅ Packages installed${NC}"

# Verify MySQL connection
echo ""
echo -e "${BLUE}🔗 Testing MySQL connection...${NC}"
if mysql -u root -e "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✅ MySQL connection successful (no password)${NC}"
    MYSQL_PASSWORD=""
elif mysql -u root -p"${MYSQL_PASSWORD}" -e "SELECT 1" &> /dev/null 2>&1; then
    echo -e "${GREEN}✅ MySQL connection successful${NC}"
else
    echo -e "${YELLOW}⚠️  MySQL connection test failed${NC}"
    echo ""
    echo "Enter MySQL root password (press Enter if no password):"
    read -s MYSQL_PASSWORD
fi

# Run the setup script
echo ""
echo -e "${BLUE}🚀 Running database setup script...${NC}"
echo ""

python mysql_setup.py

# Check if setup was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "📊 Database Information:"
    echo "   Database: loan_approval_system"
    echo "   Tables: applicants, loan_applications, risk_assessments, chat_messages"
    echo "   Records: 1000 loan applicants"
    echo ""
    echo "🔍 Verify database:"
    echo "   mysql -u root loan_approval_system"
    echo "   SELECT COUNT(*) FROM applicants;"
    echo ""
    echo "📚 Documentation:"
    echo "   - MYSQL_SETUP_GUIDE.md - Complete setup guide"
    echo "   - SAMPLE_DATA_README.md - Data documentation"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Check the error messages above for details"
    exit 1
fi
