#!/usr/bin/env python3

"""
FastAPI Microservice for LoanOrchestrator
Exposes LangGraph orchestration engine as REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio
import logging

from langgraph_orchestrator import LoanOrchestrator, format_workflow_result

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Loan Approval Orchestrator API",
    description="Multi-agent AI orchestration engine for loan processing",
    version="1.0.0"
)

# Initialize orchestrator
orchestrator = LoanOrchestrator(use_local_agents=True)

# Store processing status
processing_status = {}

# ============================================================================
# Request/Response Models
# ============================================================================

class LoanApplicationRequest(BaseModel):
    """Loan application request"""
    applicant_id: str = Field(..., description="Applicant ID")
    full_name: Optional[str] = Field(None, description="Full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    loan_amount: Optional[float] = Field(None, description="Requested loan amount")
    annual_income: Optional[float] = Field(None, description="Annual income")


class ProcessingStage(BaseModel):
    """Processing stage information"""
    stage: str
    timestamp: str
    status: str


class OrchestrationResponse(BaseModel):
    """Orchestration response"""
    applicant_id: str
    processing_stages: List[ProcessingStage]
    decision: str
    risk_score: float
    confidence: float
    case_id: Optional[str] = None
    llm_analysis: Dict[str, Any]
    errors: List[str]
    timestamp: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/status/{applicant_id}")
async def get_processing_status(applicant_id: str):
    """Get processing status for an applicant"""
    if applicant_id not in processing_status:
        raise HTTPException(status_code=404, detail="Application not found")

    return processing_status[applicant_id]


# ============================================================================
# Loan Processing Endpoints
# ============================================================================

@app.post("/process", response_model=OrchestrationResponse)
async def process_loan_application(request: LoanApplicationRequest):
    """
    Process loan application through orchestration engine

    Steps:
    1. Receive loan application data
    2. Invoke orchestrator with applicant_id
    3. Orchestrator invokes agents via MCP
    4. LLM synthesizes results
    5. Return final decision
    """
    logger.info(f"Processing loan application for {request.applicant_id}")

    try:
        # Process application
        result = orchestrator.process_application_sync(request.applicant_id)

        # Format result
        formatted_result = format_workflow_result(result)

        # Store status
        processing_status[request.applicant_id] = {
            "status": "COMPLETED",
            "result": formatted_result,
            "timestamp": datetime.now().isoformat()
        }

        return formatted_result

    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-async")
async def process_loan_application_async(request: LoanApplicationRequest, background_tasks: BackgroundTasks):
    """
    Process loan application asynchronously

    Returns immediately with processing ID
    """
    applicant_id = request.applicant_id

    # Store initial status
    processing_status[applicant_id] = {
        "status": "PROCESSING",
        "started_at": datetime.now().isoformat()
    }

    logger.info(f"Starting async processing for {applicant_id}")

    # Add background task
    def process_in_background():
        try:
            result = orchestrator.process_application_sync(applicant_id)
            formatted_result = format_workflow_result(result)

            processing_status[applicant_id] = {
                "status": "COMPLETED",
                "result": formatted_result,
                "completed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Background processing error: {str(e)}")
            processing_status[applicant_id] = {
                "status": "FAILED",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

    background_tasks.add_task(process_in_background)

    return {
        "applicant_id": applicant_id,
        "status": "PROCESSING",
        "message": "Application submitted for processing",
        "check_status_url": f"/status/{applicant_id}",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/process/{applicant_id}")
async def get_processing_result(applicant_id: str):
    """Get processing result for an applicant"""
    if applicant_id not in processing_status:
        raise HTTPException(status_code=404, detail="Application not found")

    status_data = processing_status[applicant_id]

    if status_data["status"] == "PROCESSING":
        return {
            "status": "PROCESSING",
            "applicant_id": applicant_id,
            "message": "Still processing...",
            "started_at": status_data.get("started_at")
        }
    elif status_data["status"] == "COMPLETED":
        return status_data["result"]
    else:
        return {
            "status": "FAILED",
            "applicant_id": applicant_id,
            "error": status_data.get("error")
        }


# ============================================================================
# Batch Processing Endpoints
# ============================================================================

@app.post("/batch-process")
async def batch_process_applications(applications: List[LoanApplicationRequest]):
    """Process multiple loan applications"""
    logger.info(f"Starting batch processing for {len(applications)} applications")

    results = []

    for app in applications:
        try:
            result = orchestrator.process_application_sync(app.applicant_id)
            formatted_result = format_workflow_result(result)
            results.append(formatted_result)
        except Exception as e:
            logger.error(f"Error processing {app.applicant_id}: {str(e)}")
            results.append({
                "applicant_id": app.applicant_id,
                "error": str(e)
            })

    # Summary
    approved_count = sum(1 for r in results if r.get("decision") == "APPROVE")
    rejected_count = sum(1 for r in results if r.get("decision") == "REJECT")
    review_count = sum(1 for r in results if r.get("decision") == "REVIEW")

    return {
        "total_processed": len(results),
        "approved": approved_count,
        "rejected": rejected_count,
        "under_review": review_count,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# WebSocket Streaming Endpoint
# ============================================================================

@app.websocket("/ws/process/{applicant_id}")
async def websocket_process(websocket: WebSocket, applicant_id: str):
    """
    WebSocket endpoint for real-time processing updates

    Sends processing stages as they complete
    """
    await websocket.accept()

    try:
        # Send start message
        await websocket.send_json({
            "type": "START",
            "applicant_id": applicant_id,
            "timestamp": datetime.now().isoformat()
        })

        # Process application with stage updates
        result = orchestrator.process_application_sync(applicant_id)

        # Send stage updates
        for stage in result.get("processing_stages", []):
            await websocket.send_json({
                "type": "STAGE_UPDATE",
                "stage": stage["stage"],
                "status": stage["status"],
                "timestamp": stage["timestamp"]
            })

        # Send final result
        formatted_result = format_workflow_result(result)
        await websocket.send_json({
            "type": "COMPLETED",
            "data": formatted_result,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    finally:
        await websocket.close()


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get summary analytics of processed applications"""
    completed = [s for s in processing_status.values() if s.get("status") == "COMPLETED"]

    if not completed:
        return {
            "total_processed": 0,
            "message": "No completed applications yet"
        }

    results = [s["result"] for s in completed]

    approved = sum(1 for r in results if r.get("decision") == "APPROVE")
    rejected = sum(1 for r in results if r.get("decision") == "REJECT")
    review = sum(1 for r in results if r.get("decision") == "REVIEW")

    avg_risk_score = sum(r.get("risk_score", 0) for r in results) / len(results)
    avg_confidence = sum(r.get("confidence", 0) for r in results) / len(results)

    return {
        "total_processed": len(completed),
        "approved": approved,
        "rejected": rejected,
        "under_review": review,
        "approval_rate": f"{(approved/len(completed)*100):.1f}%",
        "average_risk_score": round(avg_risk_score, 2),
        "average_confidence": round(avg_confidence, 2),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/analytics/decisions")
async def get_decision_analytics():
    """Get detailed decision analytics"""
    completed = [s for s in processing_status.values() if s.get("status") == "COMPLETED"]

    decisions = {}
    for status in completed:
        result = status["result"]
        decision = result.get("decision", "UNKNOWN")
        if decision not in decisions:
            decisions[decision] = {
                "count": 0,
                "avg_risk_score": 0,
                "avg_confidence": 0
            }
        decisions[decision]["count"] += 1
        decisions[decision]["avg_risk_score"] += result.get("risk_score", 0)
        decisions[decision]["avg_confidence"] += result.get("confidence", 0)

    # Calculate averages
    for decision in decisions:
        count = decisions[decision]["count"]
        decisions[decision]["avg_risk_score"] = round(decisions[decision]["avg_risk_score"] / count, 2)
        decisions[decision]["avg_confidence"] = round(decisions[decision]["avg_confidence"] / count, 2)

    return {
        "decision_breakdown": decisions,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 Loan Orchestrator API starting up")
    logger.info("✅ LangGraph orchestration engine initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 Loan Orchestrator API shutting down")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
