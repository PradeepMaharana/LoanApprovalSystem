# Sample Data for Loan Approval System

## Overview

1,000 rows of realistic loan applicant sample data generated for testing and development of the Loan Approval System.

---

## Files Generated

### 1. **Loan_Applicants_Sample_Data.xlsx** (Primary - Recommended)
- Professional Excel format with formatting
- Multiple sheets (Data + Statistics)
- Frozen header row
- Formatted columns with currency symbols
- Data validation and statistics sheet

**Best for:** Analysis in Excel, presentations, data review

### 2. **Loan_Applicants_Sample_Data.csv**
- Comma-separated values format
- Compatible with all tools
- Easy to import into databases

**Best for:** Database import, API testing, data processing

### 3. **Loan_Applicants_Sample_Data.json**
- JSON format with ISO date strings
- Structured data format

**Best for:** API integration, JavaScript/web applications

### 4. **generate_sample_data.py**
- Python script to regenerate data with different parameters
- Customizable record count, date ranges, and distributions

**Best for:** Regenerating data with custom parameters

---

## Data Columns

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| **Applicant ID** | String | APP-2026-000001 to APP-2026-001000 | Unique identifier for each applicant |
| **Age** | Integer | 18 - 75 years | Applicant age (normally distributed around 45) |
| **Income** | Currency | $30,000 - $486,248 | Annual income in USD (log-normal distribution) |
| **Employment Type** | String | Salaried, Self-Employed, Freelancer, Business Owner | Type of employment |
| **Credit Score** | Integer | 401 - 850 | FICO credit score (normally distributed around 679) |
| **Loan Amount** | Currency | $50,000 - $2,000,000 | Requested loan amount (multiples of $5,000) |
| **Tenure (Months)** | Integer | 12 - 360 | Loan duration in months (multiples of 12) |
| **Existing Liabilities** | Currency | $0 - $133,000 | Current debts and obligations |
| **Location** | String | 30 US cities | Geographic location |
| **Application Timestamp** | DateTime | 2026-01-02 to 2026-07-01 | Date and time of application |

---

## Data Statistics

### Population Metrics

| Metric | Value |
|--------|-------|
| Total Records | 1,000 |
| Date Range | 6 months (Jan - Jul 2026) |
| Unique Locations | 30 US cities |
| Records with Liabilities | 709 (70.9%) |

### Age Statistics
- **Range:** 18 - 75 years
- **Mean:** 45.0 years
- **Distribution:** Normal (μ=45, σ=12)

### Income Statistics
- **Range:** $30,000 - $486,248
- **Mean:** $56,034
- **Median:** $36,956
- **Distribution:** Log-normal (skewed towards lower values)

### Credit Score Statistics
- **Range:** 401 - 850
- **Mean:** 678.6
- **Median:** 679
- **Distribution:** Normal (μ=680, σ=80)

### Loan Amount Statistics
- **Range:** $50,000 - $2,000,000
- **Mean:** $192,195
- **Median:** $135,000
- **Typical Range:** 1.5x - 5.5x annual income

### Tenure Statistics
- **Range:** 12 - 360 months
- **Mean:** 185.2 months (~15 years)
- **Common Terms:** 12, 24, 36, 48, 60, 120, 180, 240, 360 months

### Liabilities Statistics
- **Range:** $0 - $133,000
- **Mean:** $10,276
- **With Liabilities:** 70.9%
- **Without Liabilities:** 29.1%

### Employment Type Distribution
| Employment Type | Count | Percentage |
|-----------------|-------|-----------|
| Salaried | 535 | 53.5% |
| Self-Employed | 235 | 23.5% |
| Freelancer | 130 | 13.0% |
| Business Owner | 100 | 10.0% |

### Top 10 Locations
| Location | Count |
|----------|-------|
| Boston, MA | 48 |
| Charlotte, NC | 43 |
| Seattle, WA | 43 |
| Dallas, TX | 41 |
| Nashville, TN | 40 |
| Chicago, IL | 39 |
| Denver, CO | 39 |
| Houston, TX | 38 |
| Atlanta, GA | 37 |
| San Francisco, CA | 37 |

---

## Data Characteristics

### Realistic Features

✅ **Age Distribution**
- Concentrated around working age (25-60)
- Realistic minimum (18) and maximum (75)
- Normal distribution matches population patterns

✅ **Income Distribution**
- Log-normal distribution (realistic for population)
- Higher concentration at lower incomes
- Tail extends to higher earners
- Aligned with US income patterns

✅ **Credit Scores**
- Normally distributed around 680 (US median)
- Realistic range (401-850)
- Includes some poor credit applicants (< 600)
- Realistic proportion of good credit scores (750+)

✅ **Loan Amounts**
- Correlates with income (1.5x - 5.5x annual)
- Varies by employment type
- Includes full range (small to large loans)

✅ **Liabilities**
- 70% of applicants have existing debts
- Positively correlated with income
- Realistically distributed

✅ **Locations**
- Covers 30 major US cities
- Realistic geographic distribution
- Matches population centers

✅ **Timestamps**
- Spread over 6-month period
- Realistic business hours (8-20)
- Random minute and second precision

---

## Usage Examples

### Excel Analysis

1. Open **Loan_Applicants_Sample_Data.xlsx** in Excel
2. View statistics in "Info" sheet
3. Analyze data in "Applicants" sheet
4. Use pivot tables for custom analysis
5. Create charts and visualizations

### Import to Database

```sql
-- SQL Server / PostgreSQL
LOAD DATA INFILE 'Loan_Applicants_Sample_Data.csv'
INTO TABLE loan_applications
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

### Python Data Processing

```python
import pandas as pd

# Load data
df = pd.read_csv('Loan_Applicants_Sample_Data.csv')

# Convert timestamp
df['Application Timestamp'] = pd.to_datetime(df['Application Timestamp'])

# Basic analysis
print(df.describe())
print(df.groupby('Employment Type').size())
```

### API Testing with Sample Data

```python
import requests
import pandas as pd

df = pd.read_csv('Loan_Applicants_Sample_Data.csv')

for idx, row in df.iterrows():
    app_data = {
        "applicant": {
            "applicant_id": row['Applicant ID'],
            "age": row['Age'],
            "income": row['Income'],
            "employment_type": row['Employment Type'],
            "location": row['Location']
        },
        "loan_details": {
            "credit_score": row['Credit Score'],
            "loan_amount": row['Loan Amount'],
            "tenure": row['Tenure (Months)'],
            "liabilities": row['Existing Liabilities']
        }
    }
    
    response = requests.post(
        'http://localhost:8000/api/v1/applications',
        json=app_data
    )
    print(f"Application {row['Applicant ID']}: {response.status_code}")
```

### Load into Streamlit Session

```python
import pandas as pd
import streamlit as st

@st.cache_data
def load_sample_data():
    return pd.read_csv('Loan_Applicants_Sample_Data.csv')

df = load_sample_data()
st.dataframe(df)
```

---

## Regenerating Data

### Generate Custom Data

```bash
# Edit generate_sample_data.py to customize:
# - num_rows: Number of records
# - Date range
# - Income distribution
# - Credit score distribution
# - Locations list

python generate_sample_data.py
```

### Script Parameters

```python
# In generate_sample_data.py

# Number of records to generate
num_rows = 1000

# Age distribution
age_mean = 45
age_std = 12

# Income distribution
income_log_mean = 10.5
income_log_std = 0.8

# Credit score distribution
credit_mean = 680
credit_std = 80

# Loan amount multiplier
loan_multiplier_min = 1.5
loan_multiplier_max = 5.5

# Liabilities probability
liabilities_probability = 0.7
```

---

## Data Quality

### Validation Checks

✅ **ID Uniqueness**
- All Applicant IDs are unique (1000 unique IDs)

✅ **Range Validation**
- Age: 18-75 (legal lending age range)
- Income: Positive, realistic values
- Credit Score: 300-850 (standard FICO range)
- Loan Amount: $50K-$2M (reasonable range)
- Tenure: 12-360 months (standard loan terms)
- Liabilities: Non-negative values

✅ **Data Consistency**
- Loan amounts correlate with income
- Liabilities reasonable relative to income
- Employment types valid and realistic
- Locations are real US cities
- Timestamps are sequential and realistic

✅ **No Missing Values**
- All 1000 rows complete
- No NULL or empty fields
- All required fields populated

---

## Use Cases

### 1. System Testing
```
Use entire dataset to test API endpoints
Test data validation with diverse inputs
Verify risk assessment algorithms
Test pagination and filtering
```

### 2. Performance Testing
```
Load test API with 1000 applications
Measure response times
Test database indexing strategies
Benchmark search queries
```

### 3. Data Analysis
```
Analyze applicant demographics
Calculate approval rates by segment
Identify risk patterns
Geographic distribution analysis
```

### 4. Training & Documentation
```
Example datasets for tutorials
Sample data for presentations
Demo data for stakeholders
Realistic scenarios for QA testing
```

### 5. Machine Learning
```
Train risk assessment models
Feature engineering and selection
Predictive analytics development
Model validation with real patterns
```

---

## Column Relationships

### Income-Based Calculations

```
Loan Amount ≈ Income × 1.5 to 5.5 multiplier
Monthly Payment = Loan Amount / Tenure (months)
Debt-to-Income Ratio = (Liabilities + Loan Amount) / Income
Loan-to-Income Ratio = Loan Amount / Income
```

### Risk Factors

```
Credit Score influence: Lower credit → Higher risk
DTI Ratio influence: Higher DTI → Higher risk
Age influence: Very young/old → Higher risk
Employment Type: Salaried more stable than others
```

---

## Best Practices for Using This Data

1. **Anonymization**
   - This is sample data (not real individuals)
   - Safe to use in development and testing
   - No actual personal information

2. **Backup**
   - Keep original files before modifications
   - Use version control for tracked changes
   - Regular backups of analysis

3. **Data Integrity**
   - Don't manually edit in Excel (maintain consistency)
   - Regenerate if modifications needed
   - Document any custom transformations

4. **Statistical Validity**
   - Sample size (1000) reasonable for analysis
   - Distributions representative of real data
   - Suitable for model training

5. **Performance Testing**
   - Scale up data as needed
   - Use for database query optimization
   - API load testing scenarios

---

## Troubleshooting

### Excel File Won't Open
- Ensure Excel 2016 or later
- Try opening with LibreOffice Calc
- Convert to CSV format

### CSV Import Issues
- Verify delimiter (comma-separated)
- Check character encoding (UTF-8)
- Ensure quotes around text fields

### JSON Parsing Error
- Validate JSON format
- Check date format (ISO 8601)
- Use Python's `json.loads()` for validation

### Data Mismatch in Different Formats
- All three formats (Excel, CSV, JSON) contain identical data
- Small differences in date formatting are normal
- Re-generate if consistency is critical

---

## Support

For questions about the sample data:
1. Review this README file
2. Check IMPLEMENTATION_SUMMARY.md
3. Review API_DOCUMENTATION.md for expected formats
4. Run generate_sample_data.py to regenerate

---

## License & Usage

✅ **Free to use** for any purpose within the Loan Approval System
✅ **Modify** as needed for your use case
✅ **Distribute** as part of project deliverables
✅ **Scale** to larger datasets by modifying script

---

## Summary

- **1000 realistic loan applicant records**
- **3 file formats** (Excel, CSV, JSON)
- **10 data columns** with realistic distributions
- **Comprehensive statistics** and analysis
- **Production-ready** data for testing and development

**Status:** ✅ Ready to Use  
**Quality:** Professional Grade  
**Generated:** 2024-07-01
