"""
FastAPI Server
REST API and webhook endpoints
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application"""

    app = FastAPI(
        title="WBS BPKH API",
        description="Whistleblowing System BPKH - REST API",
        version="2.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==================== Health Check ====================

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        from database import get_database

        db = get_database()
        db_status = db.health_check()

        return {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "version": "2.0.0"
        }

    # ==================== Webhook Endpoints ====================

    @app.post("/webhook/waha")
    async def waha_webhook(request: Request, background_tasks: BackgroundTasks):
        """WAHA WhatsApp webhook endpoint"""
        try:
            payload = await request.json()
            logger.info(f"WAHA webhook received: {payload.get('event')}")

            # Process in background
            from integrations import WAHAWebhookHandler
            handler = WAHAWebhookHandler()

            background_tasks.add_task(handler.handle_message, payload)

            return {"status": "received"}

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ==================== Report Endpoints ====================

    class ReportSubmission(BaseModel):
        what: str
        where: str
        when: str
        who: str
        how: str
        evidence_description: Optional[str] = None
        source_channel: str = "api"

    @app.post("/api/reports")
    async def submit_report(data: ReportSubmission):
        """Submit a new report via API"""
        from services import ReportService
        from models import ReportCreate

        service = ReportService()

        report_data = ReportCreate(
            what=data.what,
            where=data.where,
            when=data.when,
            who=data.who,
            how=data.how,
            evidence_description=data.evidence_description,
            source_channel=data.source_channel
        )

        result = service.submit_report(report_data)

        if result.success:
            return {
                "status": "success",
                "report_id": result.report_id,
                "pin": result.pin
            }
        else:
            raise HTTPException(status_code=400, detail=result.error)

    @app.get("/api/reports/{report_id}")
    async def get_report(report_id: str, pin: str):
        """Get report by ID (requires PIN)"""
        from services import ReportService, AuthService

        auth = AuthService()
        success, error = auth.verify_reporter_access(report_id, pin)

        if not success:
            raise HTTPException(status_code=401, detail=error)

        service = ReportService()
        report = service.get_report(report_id)

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return {
            "report_id": report.report_id,
            "status": report.status,
            "category": report.category,
            "severity": report.severity,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "summary": report.summary
        }

    # ==================== Statistics Endpoint ====================

    @app.get("/api/statistics")
    async def get_statistics():
        """Get dashboard statistics (public summary)"""
        from services import ReportService

        service = ReportService()
        stats = service.get_statistics()

        return {
            "total_reports": stats.get('total', 0),
            "this_month": stats.get('this_month', 0),
            "open_reports": stats.get('open', 0),
            "resolved_reports": stats.get('resolved', 0)
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
