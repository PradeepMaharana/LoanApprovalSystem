# Advanced Risk Assessment Guide

## Overview

This guide documents the advanced risk assessment features added to the `risk_assessments` table:
- Income Stability Score
- Employment Risk Score
- Credit History Summary
- Application Completeness Flags

---

## 1. Income Stability Score (0-100)

### Purpose
Measures how stable an applicant's income is based on employment type, age, income level, and existing liabilities.

### Calculation Factors

#### A. Employment Type (Base: ±30 points)
- **Salaried:** +28.5 (95% stability factor × 30)
- **Business Owner:** +21 (70% stability factor × 30)
- **Self-Employed:** +19.5 (65% stability factor × 30)
- **Freelancer:** +15 (50% stability factor × 30)

#### B. Age/Experience (±20 points)
- **< 25 years:** -15 (younger, limited experience)
- **25-35 years:** -5 (early career)
- **35-55 years:** +15 (peak earning, stable career)
- **55-65 years:** +5 (mid-career)
- **> 65 years:** -10 (near retirement risk)

#### C. Income Level (±15 points)
- **< $40,000:** -10 (lower income = less stable)
- **$40-80K:** 0
- **$80-150K:** +10
- **> $150K:** +15 (higher income = more stable)

#### D. Liabilities Ratio (±15 points)
- **Liabilities/Income > 0.5:** -15 (high liabilities)
- **0.3-0.5:** -8
- **0.15-0.3:** -2
- **< 0.15:** +5 (low liabilities = stable)

### Score Interpretation
- **90-100:** Very Stable Income (excellent score)
- **75-89:** Stable Income (good score)
- **60-74:** Moderate Stability (acceptable)
- **45-59:** Low Stability (concerning)
- **< 45:** Unstable Income (high risk)

### Example Query
```sql
SELECT 
    applicant_id,
    income_stability_score,
    employment_type_factor,
    age_factor_stability,
    income_factor,
    liability_factor
FROM risk_assessments
ORDER BY income_stability_score DESC
LIMIT 10;
```

---

## 2. Employment Risk Score (0-100)

### Purpose
Measures the employment-related risk of an applicant. Higher score = higher risk.

### Calculation Factors

#### A. Employment Type Risk (Base: 15-50 points)
- **Salaried:** 15 (lowest risk)
- **Business Owner:** 35 (higher risk)
- **Self-Employed:** 40 (higher risk)
- **Freelancer:** 50 (highest risk)

#### B. Age/Career Stage Risk (±20 points)
- **< 22 years:** +20 (very new to workforce)
- **22-30 years:** +10 (early career, may change jobs)
- **30-45 years:** +5 (stable career)
- **45-60 years:** +8 (mid-career)
- **> 60 years:** +25 (near retirement risk)

#### C. Income Level Risk (±15 points)
- **< $30,000:** +20 (very low = unstable)
- **$30-60K:** +10
- **$60-150K:** +2 (stable middle income)
- **> $150K:** -5 (higher income = lower risk)

#### D. Credit Management Risk (±15 points)
- **Credit < 600:** +20 (poor credit management)
- **600-650:** +12
- **650-700:** +5
- **700-750:** 0
- **> 750:** -8 (excellent credit = lower employment risk)

### Score Interpretation
- **0-20:** Very Low Employment Risk
- **21-40:** Low Employment Risk
- **41-60:** Moderate Employment Risk
- **61-80:** High Employment Risk
- **81-100:** Very High Employment Risk

### Example Query
```sql
SELECT 
    applicant_id,
    employment_risk_score,
    employment_type_risk,
    age_stage_risk,
    income_level_risk,
    credit_management_risk
FROM risk_assessments
WHERE employment_risk_score > 70
ORDER BY employment_risk_score DESC;
```

---

## 3. Credit History Summary

### Purpose
Provides categorized credit information and recommendations based on credit score.

### Credit Categories

#### A. Poor (300-579)
- **Risk Level:** Very High
- **Description:** Significant credit management issues
- **Recommendation:** Consider requiring co-signer or secured loan
- **Rebuild Target:** 580
- **Months to Rebuild:** 24

#### B. Fair (580-669)
- **Risk Level:** High
- **Description:** Several missed payments or high debt levels
- **Recommendation:** Require higher interest rate or down payment
- **Rebuild Target:** 670
- **Months to Rebuild:** 18

#### C. Good (670-739)
- **Risk Level:** Moderate
- **Description:** Decent credit management with some issues
- **Recommendation:** Standard approval with market rate
- **Rebuild Target:** 740
- **Months to Rebuild:** 12

#### D. Very Good (740-799)
- **Risk Level:** Low
- **Description:** Strong credit management and payment history
- **Recommendation:** Favorable terms and lower interest rate
- **Rebuild Target:** 800
- **Months to Rebuild:** 6

#### E. Excellent (800-850)
- **Risk Level:** Very Low
- **Description:** Excellent credit management and payment history
- **Recommendation:** Best available terms and rates
- **Rebuild Target:** 850
- **Months to Rebuild:** 0

### Additional Fields
- **score_to_next_level:** Points needed to reach next category
- **months_to_rebuild:** Estimated months to reach next level
- **credit_percentile:** Percentile ranking (0-100) based on 300-850 range

### Example Query
```sql
SELECT 
    applicant_id,
    credit_category,
    credit_risk_level,
    credit_description,
    credit_recommendation,
    score_to_next_level,
    months_to_rebuild
FROM risk_assessments
WHERE credit_category IN ('Poor', 'Fair')
ORDER BY score_to_next_level DESC;
```

---

## 4. Application Completeness Flags

### Purpose
Identifies data quality issues, missing information, and warning flags.

### Components

#### A. all_required_fields_present
**Boolean flag** - TRUE if all required fields are populated

Required Fields:
- applicant_id
- age
- income
- employment_type
- location
- credit_score
- loan_amount
- tenure_months
- existing_liabilities

#### B. missing_fields
**JSON Array** - List of fields that are missing or empty

Example:
```json
["employment_type", "location"]
```

#### C. data_consistency_issues
**JSON Array** - Lists data inconsistencies detected

Common Issues:
- "Loan amount unusually high relative to income"
- "Business owner status unlikely at young age"
- "Liabilities extremely high relative to income"
- "Age and employment type mismatch"

Example:
```json
[
  "Loan amount unusually high relative to income",
  "Liabilities extremely high relative to income"
]
```

#### D. warning_flags
**JSON Array** - Alerts about potential concerns

Common Warnings:
- "Applicant age below 25 - may indicate limited credit history"
- "Applicant age above 65 - near retirement"
- "Low income level - may impact repayment ability"
- "No existing liabilities - limited credit history"
- "Credit score below 650 - high risk"

Example:
```json
[
  "Applicant age below 25 - may indicate limited credit history",
  "Credit score below 650 - high risk"
]
```

#### E. completeness_percentage
**Decimal (0-100)** - Percentage of required fields completed

Calculation: `(Present Fields / Total Required Fields) × 100`

### Example Query
```sql
-- Find applications with data issues
SELECT 
    applicant_id,
    all_required_fields_present,
    data_consistency_issues,
    missing_fields,
    warning_flags,
    completeness_percentage
FROM risk_assessments
WHERE 
    NOT all_required_fields_present 
    OR completeness_percentage < 100
    OR warning_flags != '[]'
ORDER BY completeness_percentage ASC;
```

---

## Database Schema

### Risk Assessments Table (Enhanced)

| Column | Type | Purpose |
|--------|------|---------|
| **applicant_id** | VARCHAR(50) | Foreign key to applicants |
| **income_stability_score** | DECIMAL(5,2) | Income stability 0-100 |
| **employment_type_factor** | DECIMAL(5,2) | Employment type contribution |
| **age_factor_stability** | DECIMAL(5,2) | Age factor for stability |
| **income_factor** | DECIMAL(5,2) | Income level factor |
| **liability_factor** | DECIMAL(5,2) | Liabilities factor |
| **employment_risk_score** | DECIMAL(5,2) | Employment risk 0-100 |
| **employment_type_risk** | DECIMAL(5,2) | Employment type risk |
| **age_stage_risk** | DECIMAL(5,2) | Age/career stage risk |
| **income_level_risk** | DECIMAL(5,2) | Income level risk |
| **credit_management_risk** | DECIMAL(5,2) | Credit management risk |
| **credit_category** | VARCHAR(50) | Poor/Fair/Good/Very Good/Excellent |
| **credit_risk_level** | VARCHAR(50) | Very High/High/Moderate/Low/Very Low |
| **credit_description** | TEXT | Detailed credit summary |
| **credit_recommendation** | TEXT | Action recommendation |
| **score_to_next_level** | INT | Points to next credit level |
| **months_to_rebuild** | INT | Months to reach next level |
| **credit_percentile** | DECIMAL(5,1) | Credit percentile (0-100) |
| **all_required_fields_present** | BOOLEAN | All required data present |
| **data_consistency_issues** | JSON | Array of issues found |
| **missing_fields** | JSON | Array of missing fields |
| **warning_flags** | JSON | Array of warning flags |
| **completeness_percentage** | DECIMAL(5,2) | % of required fields (0-100) |

---

## Useful Queries

### 1. Get Overall Risk Profile
```sql
SELECT 
    a.applicant_id,
    a.employment_type,
    a.age,
    a.income,
    l.credit_score,
    l.loan_amount,
    r.income_stability_score,
    r.employment_risk_score,
    r.credit_category,
    r.completeness_percentage
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
JOIN risk_assessments r ON a.applicant_id = r.applicant_id
LIMIT 20;
```

### 2. Find High-Risk Applicants
```sql
SELECT 
    applicant_id,
    income_stability_score,
    employment_risk_score,
    credit_category,
    warning_flags
FROM risk_assessments
WHERE 
    income_stability_score < 50
    OR employment_risk_score > 70
    OR credit_category IN ('Poor', 'Fair')
ORDER BY income_stability_score ASC;
```

### 3. Credit Category Distribution with Stability
```sql
SELECT 
    credit_category,
    COUNT(*) as count,
    ROUND(AVG(income_stability_score), 2) as avg_stability,
    ROUND(AVG(employment_risk_score), 2) as avg_employment_risk
FROM risk_assessments
GROUP BY credit_category
ORDER BY count DESC;
```

### 4. Identify Data Quality Issues
```sql
SELECT 
    applicant_id,
    completeness_percentage,
    missing_fields,
    data_consistency_issues,
    warning_flags
FROM risk_assessments
WHERE 
    completeness_percentage < 100
    OR data_consistency_issues != '[]'
ORDER BY completeness_percentage ASC;
```

### 5. Employment Risk by Type
```sql
SELECT 
    a.employment_type,
    COUNT(*) as count,
    ROUND(AVG(r.employment_risk_score), 2) as avg_risk,
    ROUND(AVG(r.income_stability_score), 2) as avg_stability
FROM applicants a
JOIN risk_assessments r ON a.applicant_id = r.applicant_id
GROUP BY a.employment_type
ORDER BY avg_risk DESC;
```

### 6. Age Group Analysis
```sql
SELECT 
    CASE 
        WHEN age < 25 THEN '18-24'
        WHEN age < 35 THEN '25-34'
        WHEN age < 45 THEN '35-44'
        WHEN age < 55 THEN '45-54'
        WHEN age < 65 THEN '55-64'
        ELSE '65+'
    END as age_group,
    COUNT(*) as count,
    ROUND(AVG(r.income_stability_score), 2) as avg_stability,
    ROUND(AVG(r.employment_risk_score), 2) as avg_employment_risk
FROM applicants a
JOIN risk_assessments r ON a.applicant_id = r.applicant_id
GROUP BY age_group
ORDER BY age_group ASC;
```

---

## Integration with Loan Decisions

### 1. Recommendation Engine
```sql
-- Get comprehensive recommendation for each applicant
SELECT 
    a.applicant_id,
    a.age,
    a.income,
    a.employment_type,
    l.credit_score,
    l.loan_amount,
    r.income_stability_score,
    r.employment_risk_score,
    r.credit_category,
    r.credit_recommendation,
    CASE 
        WHEN r.income_stability_score >= 75 AND r.employment_risk_score <= 30 
             AND r.credit_category IN ('Very Good', 'Excellent')
        THEN 'STRONG APPROVAL - Best terms'
        WHEN r.income_stability_score >= 60 AND r.employment_risk_score <= 50
             AND r.credit_category IN ('Good', 'Very Good')
        THEN 'APPROVAL - Standard terms'
        WHEN r.income_stability_score >= 50 AND r.employment_risk_score <= 65
        THEN 'CONDITIONAL APPROVAL - Higher rate'
        ELSE 'REVIEW REQUIRED - Manual assessment'
    END as recommendation
FROM applicants a
JOIN loan_applications l ON a.applicant_id = l.applicant_id
JOIN risk_assessments r ON a.applicant_id = r.applicant_id;
```

---

## Statistics Summary

### Current Database Status
- **Total Applicants:** 1,000
- **Income Stability Scores:** Min 36.50, Max 100, Avg 78.04
- **Employment Risk Scores:** Min 11, Max 100, Avg 50.14
- **Credit Category Distribution:**
  - Fair: 355 (35.5%)
  - Good: 318 (31.8%)
  - Very Good: 159 (15.9%)
  - Poor: 98 (9.8%)
  - Excellent: 70 (7.0%)
- **Application Completeness:** 100% (all fields present)

---

## Implementation Notes

### Python Classes
- **AdvancedRiskAssessment:** Main class handling all calculations
- **EnhancedMySQLLoanDatabase:** Database handler with enhanced loading

### Key Methods
1. `calculate_income_stability_score()` - Income stability calculation
2. `calculate_employment_risk()` - Employment risk calculation
3. `calculate_credit_history_summary()` - Credit summarization
4. `calculate_application_completeness_flags()` - Data quality assessment
5. `generate_comprehensive_risk_summary()` - Combine all assessments

### Data Flow
```
CSV Sample Data
    ↓
Advanced Risk Assessment
    ├─ Income Stability Score
    ├─ Employment Risk Score
    ├─ Credit History Summary
    └─ Application Completeness Flags
    ↓
MySQL Database (risk_assessments table)
    ↓
Queries and Analysis
```

---

## Future Enhancements

1. **Machine Learning Integration:** Train models using historical data
2. **Real-time Scoring:** Update scores as new data arrives
3. **Fraud Detection:** Flag suspicious patterns
4. **Portfolio Analysis:** Aggregate insights across all applicants
5. **Dashboarding:** Visualize risk profiles and trends

---

## Support & Documentation

- **Main Script:** `mysql_enhanced_setup.py`
- **Assessment Logic:** `advanced_risk_assessment.py`
- **Database Schema:** MySQL `loan_approval_system.risk_assessments`
- **Sample Queries:** See section above

Generated: 2024-07-01  
Status: Production Ready
