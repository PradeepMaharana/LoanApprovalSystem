from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Loan Approval System API",
    description="Professional REST API for loan application processing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class EmploymentType(str, Enum):
    SALARIED = "Salaried"
    SELF_EMPLOYED = "Self-Employed"
    FREELANCER = "Freelancer"
    BUSINESS_OWNER = "Business Owner"


class ApplicationStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING_DOCUMENTS = "PENDING_DOCUMENTS"


# Pydantic Models
class ApplicantProfile(BaseModel):
    applicant_id: str = Field(..., min_length=3, max_length=50, description="Unique applicant identifier")
    age: int = Field(..., ge=18, le=100, description="Applicant age")
    income: float = Field(..., gt=0, description="Annual income in USD")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    location: str = Field(..., min_length=2, max_length=100, description="Applicant location")

    @validator('applicant_id')
    def validate_applicant_id(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Applicant ID must be alphanumeric')
        return v


class CreditLoanDetails(BaseModel):
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    loan_amount: float = Field(..., gt=0, le=10000000, description="Loan amount in USD")
    tenure: int = Field(..., ge=3, le=360, description="Loan tenure in months")
    liabilities: float = Field(default=0, ge=0, description="Existing liabilities in USD")

    @validator('tenure')
    def validate_tenure(cls, v):
        if v % 3 != 0:
            raise ValueError('Tenure must be in multiples of 3 months')
        return v


class LoanApplicationRequest(BaseModel):
    applicant: ApplicantProfile
    loan_details: CreditLoanDetails
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "applicant": {
                    "applicant_id": "APP-2024-001",
                    "age": 35,
                    "income": 120000,
                    "employment_type": "Salaried",
                    "location": "New York, NY"
                },
                "loan_details": {
                    "credit_score": 750,
                    "loan_amount": 300000,
                    "tenure": 360,
                    "liabilities": 50000
                }
            }
        }


class RiskAssessment(BaseModel):
    risk_score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_level: str = Field(..., description="Risk level classification")
    dti_ratio: float = Field(..., ge=0, description="Debt-to-Income ratio")
    lti_ratio: float = Field(..., ge=0, description="Loan-to-Income ratio")
    factors: dict = Field(default_factory=dict, description="Risk factors breakdown")


class LoanApplicationResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    applicant_id: str
    loan_amount: float
    risk_assessment: RiskAssessment
    created_at: datetime
    updated_at: datetime
    message: str


class ApplicationListResponse(BaseModel):
    total_count: int
    applications: List[LoanApplicationResponse]
    page: int
    page_size: int


class ChatMessage(BaseModel):
    user_id: str = Field(..., min_length=1, description="User or applicant ID")
    message: str = Field(..., min_length=1, max_length=1000, description="Chat message")
    application_id: Optional[str] = Field(None, description="Associated application ID")


class ChatResponse(BaseModel):
    message_id: str
    user_id: str
    user_message: str
    bot_response: str
    timestamp: datetime
    application_context: Optional[dict] = None


# Risk Calculation Functions
def calculate_risk_score(
    credit_score: int,
    liabilities: float,
    income: float,
    loan_amount: float,
    age: int
) -> dict:
    """Calculate comprehensive risk assessment"""
    score = 100
    factors = {}

    # Credit score factor (max -40)
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
    factors['credit_score'] = {
        'impact': credit_factor,
        'value': credit_score,
        'description': 'Credit Score Factor'
    }

    # Debt-to-Income ratio (max -30)
    dti = (liabilities + loan_amount) / income if income > 0 else 1.0
    dti_factor = 0
    if dti > 0.6:
        dti_factor = -30
    elif dti > 0.5:
        dti_factor = -20
    elif dti > 0.4:
        dti_factor = -10

    score += dti_factor
    factors['dti_ratio'] = {
        'impact': dti_factor,
        'value': dti,
        'description': 'Debt-to-Income Ratio'
    }

    # Age factor (max -15)
    age_factor = 0
    if age < 25 or age > 65:
        age_factor = -15
    elif age > 60:
        age_factor = -5

    score += age_factor
    factors['age'] = {
        'impact': age_factor,
        'value': age,
        'description': 'Age Factor'
    }

    # Loan-to-Income ratio (max -20)
    lti = loan_amount / income if income > 0 else 10.0
    lti_factor = 0
    if lti > 5:
        lti_factor = -20
    elif lti > 3:
        lti_factor = -10

    score += lti_factor
    factors['lti_ratio'] = {
        'impact': lti_factor,
        'value': lti,
        'description': 'Loan-to-Income Ratio'
    }

    final_score = max(0, min(100, score))
    return {
        'risk_score': final_score,
        'dti_ratio': dti,
        'lti_ratio': lti,
        'factors': factors
    }


def get_risk_level(risk_score: float) -> str:
    """Determine risk level classification"""
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


# In-memory storage (replace with database in production)
applications_db = {}
application_counter = 0


# API Routes
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Loan Approval System API"
    }


@app.post(
    "/api/v1/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Applications"],
    summary="Submit New Loan Application"
)
async def submit_application(request: LoanApplicationRequest):
    """
    Submit a new loan application with comprehensive validation.

    - **applicant**: Applicant profile information
    - **loan_details**: Credit and loan details
    """
    try:
        global application_counter
        application_counter += 1

        # Calculate risk assessment
        risk_data = calculate_risk_score(
            credit_score=request.loan_details.credit_score,
            liabilities=request.loan_details.liabilities,
            income=request.applicant.income,
            loan_amount=request.loan_details.loan_amount,
            age=request.applicant.age
        )

        risk_level = get_risk_level(risk_data['risk_score'])

        # Determine initial status based on risk score
        if risk_data['risk_score'] >= 75:
            status_val = ApplicationStatus.APPROVED
            message = "Application approved! Congratulations on your pre-approval."
        elif risk_data['risk_score'] < 20:
            status_val = ApplicationStatus.REJECTED
            message = "Application requires further review. We'll contact you shortly."
        else:
            status_val = ApplicationStatus.UNDER_REVIEW
            message = "Application received and under review. You'll receive updates within 2-3 business days."

        application_id = f"LOAN-{datetime.now().strftime('%Y%m%d')}-{application_counter:06d}"

        # Create response
        risk_assessment = RiskAssessment(
            risk_score=risk_data['risk_score'],
            risk_level=risk_level,
            dti_ratio=risk_data['dti_ratio'],
            lti_ratio=risk_data['lti_ratio'],
            factors=risk_data['factors']
        )

        response = LoanApplicationResponse(
            application_id=application_id,
            status=status_val,
            applicant_id=request.applicant.applicant_id,
            loan_amount=request.loan_details.loan_amount,
            risk_assessment=risk_assessment,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            message=message
        )

        # Store application
        applications_db[application_id] = response

        logger.info(f"Application {application_id} submitted for {request.applicant.applicant_id}")

        return response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing application. Please try again."
        )


@app.get(
    "/api/v1/applications/{application_id}",
    response_model=LoanApplicationResponse,
    tags=["Applications"],
    summary="Get Application Details"
)
async def get_application(application_id: str):
    """Retrieve application details by ID"""
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found"
        )

    return applications_db[application_id]


@app.get(
    "/api/v1/applications",
    response_model=ApplicationListResponse,
    tags=["Applications"],
    summary="List All Applications"
)
async def list_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ApplicationStatus] = Query(None)
):
    """
    List all applications with pagination and filtering.

    - **page**: Page number (starting from 1)
    - **page_size**: Number of applications per page
    - **status_filter**: Filter by application status
    """
    apps = list(applications_db.values())

    # Filter by status if provided
    if status_filter:
        apps = [app for app in apps if app.status == status_filter]

    total_count = len(apps)

    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_apps = apps[start_idx:end_idx]

    return ApplicationListResponse(
        total_count=total_count,
        applications=paginated_apps,
        page=page,
        page_size=page_size
    )


@app.post(
    "/api/v1/validate-application",
    response_model=RiskAssessment,
    tags=["Validation"],
    summary="Validate Application Data"
)
async def validate_application(request: LoanApplicationRequest):
    """
    Validate application data and return risk assessment without submitting.
    Useful for real-time validation in UI.
    """
    try:
        risk_data = calculate_risk_score(
            credit_score=request.loan_details.credit_score,
            liabilities=request.loan_details.liabilities,
            income=request.applicant.income,
            loan_amount=request.loan_details.loan_amount,
            age=request.applicant.age
        )

        risk_level = get_risk_level(risk_data['risk_score'])

        return RiskAssessment(
            risk_score=risk_data['risk_score'],
            risk_level=risk_level,
            dti_ratio=risk_data['dti_ratio'],
            lti_ratio=risk_data['lti_ratio'],
            factors=risk_data['factors']
        )

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Send Chat Message"
)
async def send_chat_message(chat_msg: ChatMessage):
    """
    Process chat messages and provide intelligent responses.
    Optionally associate with an application for context.
    """
    try:
        # Get application context if provided
        app_context = None
        if chat_msg.application_id and chat_msg.application_id in applications_db:
            app_context = applications_db[chat_msg.application_id].dict()

        # Generate bot response based on message
        bot_response = generate_chat_response(
            user_message=chat_msg.message,
            app_context=app_context
        )

        message_id = f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(chat_msg.message) % 10000:04d}"

        logger.info(f"Chat message from {chat_msg.user_id}: {chat_msg.message[:50]}...")

        return ChatResponse(
            message_id=message_id,
            user_id=chat_msg.user_id,
            user_message=chat_msg.message,
            bot_response=bot_response,
            timestamp=datetime.now(),
            application_context=app_context
        )

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing chat message"
        )


def generate_chat_response(user_message: str, app_context: Optional[dict] = None) -> str:
    """Generate contextual chat responses"""
    message_lower = user_message.lower()

    responses = {
        'approval': "Based on your profile and credit information, our team is reviewing your application. You'll receive a decision within 2-3 business days.",
        'timeline': "Standard loan applications are typically processed within 2-3 business days. You can check your application status anytime.",
        'documents': "You may need to provide: recent pay stubs, tax returns, bank statements, and employment verification. We'll request any additional documents if needed.",
        'interest': "Interest rates are determined based on your credit score and loan profile. You'll receive a formal offer after initial review.",
        'decline': "Each application is reviewed individually. If you have concerns, we can discuss your options or ways to strengthen your application.",
        'contact': "You can reach our support team at support@loanapproval.com or call 1-800-LOAN-HELP (1-800-562-6435).",
        'status': "Your application status is available in the dashboard. You can also check it by providing your application ID.",
    }

    for keyword, response in responses.items():
        if keyword in message_lower:
            return response

    context_str = ""
    if app_context:
        context_str = f" I see you've applied for ${app_context['loan_amount']:,.0f} with a credit score of {app_context['risk_assessment']['risk_score']:.0f}/100."

    return f"Thank you for your inquiry!{context_str} How else can I help you with your loan application today?"


# Error Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
