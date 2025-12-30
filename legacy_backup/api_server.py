"""
API Server for WBS BPKH
FastAPI server for WAHA webhooks and external integrations
"""

import os
from datetime import datetime
from typing import Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import WAHAConfig, AppConfig
from database import WBSDatabase
from waha_integration import WAHAWebhookHandler, create_waha_webhook_response
from chatbot_agent import ChatbotAgent


# Pydantic models for request/response
class WAHAWebhookPayload(BaseModel):
    event: str
    payload: Dict = {}
    session: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class StatusCheckRequest(BaseModel):
    report_id: str
    pin: str


class StatusCheckResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_unit: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    error: Optional[str] = None


# Global instances
db: WBSDatabase = None
webhook_handler: WAHAWebhookHandler = None
config: AppConfig = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global db, webhook_handler, config

    # Startup
    print("[OK] Starting WBS API Server...")

    config = AppConfig()
    db = WBSDatabase()

    # Initialize webhook handler with API key
    api_key = os.getenv("GROQ_API_KEY", "")
    webhook_handler = WAHAWebhookHandler(db, api_key)

    print("[OK] WBS API Server ready")

    yield

    # Shutdown
    print("[OK] Shutting down WBS API Server...")
    if db:
        db.close()


# Create FastAPI app
app = FastAPI(
    title="WBS BPKH API",
    description="API server for WBS BPKH - WhatsApp webhooks and external integrations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Key verification
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for protected endpoints"""
    waha_config = WAHAConfig()
    if waha_config.api_key and x_api_key != waha_config.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


# WAHA Webhook endpoint
@app.post("/webhook/waha")
async def waha_webhook(request: Request):
    """
    Handle incoming WAHA webhooks

    Events:
    - message: New incoming message
    - message.ack: Message delivery acknowledgment
    - session.status: Session status change
    """
    try:
        payload = await request.json()

        # Log incoming webhook
        event = payload.get("event", "unknown")
        print(f"[INFO] WAHA webhook received: {event}")

        # Process with handler
        if webhook_handler:
            result = webhook_handler.handle_webhook(payload)
            return create_waha_webhook_response(True, result.get("status", "processed"))
        else:
            return create_waha_webhook_response(False, "Handler not initialized")

    except Exception as e:
        print(f"[ERROR] Webhook processing error: {e}")
        return create_waha_webhook_response(False, str(e))


# Status check API (for external integrations)
@app.post("/api/status", response_model=StatusCheckResponse)
async def check_status(request: StatusCheckRequest):
    """
    Check report status via API
    Requires Report ID and PIN
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        # Validate access
        if not db.validate_report_access(request.report_id, request.pin):
            return StatusCheckResponse(
                success=False,
                error="Invalid Report ID or PIN"
            )

        # Get report
        report = db.get_report_for_reporter(request.report_id)
        if not report:
            return StatusCheckResponse(
                success=False,
                error="Report not found"
            )

        return StatusCheckResponse(
            success=True,
            report_id=request.report_id,
            status=report.get("status"),
            severity=report.get("severity"),
            assigned_unit=report.get("assigned_unit"),
            created_at=report.get("created_at"),
            updated_at=report.get("updated_at")
        )

    except Exception as e:
        print(f"[ERROR] Status check error: {e}")
        return StatusCheckResponse(
            success=False,
            error="Internal server error"
        )


# WAHA status check
@app.get("/api/waha/status")
async def waha_status(verified: bool = Depends(verify_api_key)):
    """Check WAHA connection status"""
    from waha_integration import WAHAClient

    client = WAHAClient()
    health = client.check_health()
    sessions = client.get_sessions()

    return {
        "waha_health": health,
        "sessions": sessions,
        "timestamp": datetime.now().isoformat()
    }


# Send notification endpoint (protected)
@app.post("/api/notify")
async def send_notification(
    request: Request,
    verified: bool = Depends(verify_api_key)
):
    """
    Send notification to reporter

    Body:
    - report_id: Report ID
    - type: notification type (status_update, new_message)
    - message: custom message (optional)
    """
    try:
        data = await request.json()
        report_id = data.get("report_id")
        notif_type = data.get("type")

        if not report_id:
            raise HTTPException(status_code=400, detail="report_id required")

        # Get contact info
        access = db.get_report_access(report_id) if db else None
        if not access:
            return {"success": False, "error": "Report access not found"}

        from notifications import NotificationService
        notifier = NotificationService(db)

        email = access.get("email")
        phone = access.get("phone")

        if notif_type == "status_update":
            old_status = data.get("old_status", "N/A")
            new_status = data.get("new_status", "Updated")
            result = notifier.notify_status_update(report_id, old_status, new_status, email, phone)
        elif notif_type == "new_message":
            sender = data.get("sender", "Pengelola WBS")
            result = notifier.notify_new_message(report_id, sender, email, phone)
        else:
            return {"success": False, "error": f"Unknown notification type: {notif_type}"}

        return {"success": True, "result": result}

    except Exception as e:
        print(f"[ERROR] Notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Chatbot API endpoint
@app.post("/api/chatbot")
async def chatbot_message(request: Request):
    """
    Send message to chatbot

    Body:
    - session_id: Session ID (optional, will create new if not provided)
    - message: User message
    - channel: Channel (web, whatsapp, api)
    """
    try:
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")
        channel = data.get("channel", "web")
        # Ensure channel is valid
        if channel not in ['web', 'whatsapp']:
            channel = 'web'

        if not message:
            raise HTTPException(status_code=400, detail="message required")

        api_key = os.getenv("GROQ_API_KEY", "")
        chatbot = ChatbotAgent(api_key, db)

        # Create session if needed
        if not session_id:
            session_id = chatbot.create_session(channel)

        # Process message
        result = chatbot.process_message(session_id, message)

        return {
            "success": True,
            "session_id": session_id,
            "response": result.get("response"),
            "state": result.get("state"),
            "report_id": result.get("report_id"),
            "pin": result.get("pin")
        }

    except Exception as e:
        print(f"[ERROR] Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"[ERROR] Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
