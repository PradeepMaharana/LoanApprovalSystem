# Loan Approval Chatbot - Streamlit UI

A professional, interactive Streamlit-based chatbot UI for loan application processing with advanced risk assessment and real-time analytics.

## Features

### 📋 Application Form
- **Applicant Information**: ID and Location tracking
- **Applicant Profile**: Age, Annual Income, Employment Type (Salaried, Self-Employed, Freelancer, Business Owner)
- **Credit Details**: Credit Score (300-850), Loan Amount, and Tenure (months)
- **Financial Obligations**: Existing Liabilities tracking
- **Application Timestamp**: Automatic timestamp recording

### 📊 Real-time Metrics
- **Debt-to-Income Ratio**: Quick assessment of financial burden
- **Monthly Payment Calculation**: Automatic computation
- **Loan-to-Income Ratio**: Income relative to loan size
- **Risk Assessment**: Dynamic risk scoring (0-100 scale)

### ⚠️ Risk Assessment System
- **Very Low Risk** (75+): Green indicator
- **Low Risk** (60-74): Light green indicator
- **Moderate Risk** (40-59): Orange indicator
- **High Risk** (20-39): Red indicator
- **Very High Risk** (0-19): Dark red indicator

Risk factors considered:
- Credit score analysis
- Debt-to-income ratio
- Applicant age
- Loan-to-income ratio

### 💬 Chat Assistant
- Real-time conversation with loan assistant
- Context-aware responses about:
  - Approval likelihood
  - Processing timeline
  - Required documents
  - Interest rates
  - Application modifications
- Chat history tracking with timestamps

### 📈 Application Dashboard
- View all submitted applications
- Application history with key metrics
- CSV export functionality
- Quick access to application summaries

## Installation

1. **Clone or navigate to the project directory:**
```bash
cd /home/ubuntu/Desktop/LoanApprovalSystem
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

1. **Run the Streamlit app:**
```bash
streamlit run app.py
```

2. **Access the application:**
- The app will open in your default browser (typically at `http://localhost:8501`)
- If not, manually navigate to the URL shown in the terminal

3. **Fill out the Application Form:**
   - Enter all required information (marked as required)
   - System calculates metrics in real-time
   - Risk assessment updates automatically

4. **Submit Application:**
   - Click "Submit Application" button
   - Application is recorded and appears in chat history
   - Receive immediate feedback

5. **Chat with Assistant:**
   - Ask questions about your application status
   - Get contextual responses based on your profile
   - Common queries: "What are my chances?", "Timeline?", "What documents do I need?"

6. **View Application History:**
   - Click "View Applications" to see all submitted applications
   - Export data as CSV for record-keeping

## Project Structure

```
LoanApprovalSystem/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Form Fields Explained

### Applicant Information
- **Applicant ID**: Unique identifier (e.g., APP-2024-001)
- **Location**: Applicant's residential location (e.g., New York, NY)

### Applicant Profile
- **Age**: Applicant's current age (18-100)
- **Income**: Annual income in USD
- **Employment Type**: Current employment status

### Credit & Loan Details
- **Credit Score**: FICO score (300-850)
- **Loan Amount**: Requested loan amount in USD
- **Tenure**: Loan repayment period in months

### Financial Obligations
- **Existing Liabilities**: Current debts/obligations in USD

## Risk Scoring Algorithm

The risk score is calculated using:
```
Base Score: 100

Credit Score Impact: -0 to -40 points
- <600: -40 points
- 600-650: -30 points
- 650-700: -15 points
- 700-750: 0 points
- 750+: +5 points

DTI Ratio Impact: -0 to -30 points
- >60%: -30 points
- 50-60%: -20 points
- 40-50%: -10 points

Age Impact: -0 to -15 points
- <25 or >65: -15 points
- 60-65: -5 points

LTI Ratio Impact: -0 to -20 points
- >5.0: -20 points
- 3.0-5.0: -10 points

Final Score: 0-100 (0=Highest Risk, 100=Lowest Risk)
```

## Chat Assistant Capabilities

The AI assistant can answer questions about:
- **Approval Chances**: "What are my chances of approval?"
- **Timeline**: "How long does processing take?"
- **Documents**: "What documents do I need?"
- **Interest Rates**: "What interest rates apply?"
- **Application Status**: "Can I decline my application?"
- **Modifications**: "Can I modify my application?"

## Customization

### Modify Risk Assessment
Edit the `calculate_risk_score()` function in `app.py` to adjust weighting factors.

### Change Employment Types
Update the employment type selectbox in the Applicant Profile section to add/remove options.

### Customize Chat Responses
Edit the `responses` dictionary in `generate_bot_response()` function to personalize bot replies.

### Adjust Styling
Modify the CSS in the `st.markdown()` call at the top of the app to change colors, fonts, and layouts.

## Performance Notes

- All data is stored in Streamlit session state (in-memory)
- For production use, integrate with a backend database
- Chat history is cleared on app restart (session-based)
- Applications persist during the session but are lost on app restart

## Future Enhancements

1. **Database Integration**: Persist applications to PostgreSQL/MongoDB
2. **Authentication**: Add user login and profile management
3. **Real ML Model**: Integrate actual loan approval ML models
4. **Document Upload**: File upload for supporting documents
5. **Email Notifications**: Send updates via email
6. **Advanced Analytics**: Dashboard with approval statistics
7. **Multi-language Support**: Internationalization
8. **Mobile Optimization**: Responsive design for mobile devices

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Module Not Found
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Data Not Persisting
Session data is temporary. For production, connect to a database.

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions about this chatbot, refer to the Streamlit documentation at https://docs.streamlit.io/
