"""
Report Service
Business logic for report operations
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from ..database import get_database, ReportRepository, MessageRepository
from ..models import Report, ReportCreate, ReportUpdate, Message, MessageCreate
from ..config import ReportStatus, SLA_CONFIG


@dataclass
class SubmitResult:
    """Report submission result"""
    success: bool
    report_id: Optional[str] = None
    pin: Optional[str] = None
    error: Optional[str] = None


class ReportService:
    """Service for report operations"""

    def __init__(self):
        self.db = get_database()
        self.report_repo = ReportRepository(self.db)
        self.message_repo = MessageRepository(self.db)

    def submit_report(self, data: ReportCreate) -> SubmitResult:
        """
        Submit a new whistleblowing report.

        Args:
            data: Report creation data with 5W+1H

        Returns:
            SubmitResult with report_id and PIN if successful
        """
        # Validate
        errors = data.validate()
        if errors:
            return SubmitResult(success=False, error="; ".join(errors))

        try:
            report_id, pin = self.report_repo.create(data)
            return SubmitResult(
                success=True,
                report_id=report_id,
                pin=pin
            )
        except Exception as e:
            return SubmitResult(success=False, error=f"Gagal menyimpan laporan: {str(e)}")

    def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        return self.report_repo.get_by_id(report_id)

    def get_all_reports(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Report]:
        """Get all reports with optional filters"""
        return self.report_repo.get_all(status=status, category=category, limit=limit)

    def update_status(
        self,
        report_id: str,
        new_status: str,
        notes: Optional[str] = None,
        updated_by: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update report status.

        Returns:
            (success, error_message)
        """
        valid_statuses = ReportStatus.get_all_statuses()
        if new_status not in valid_statuses:
            return False, f"Status tidak valid. Gunakan: {', '.join(valid_statuses)}"

        update = ReportUpdate(status=new_status, resolution_notes=notes)
        success = self.report_repo.update(report_id, update)

        if success:
            # Add system message about status change
            status_name = ReportStatus.get_display_name(new_status)
            self.message_repo.add_system_message(
                report_id,
                f"Status laporan diubah menjadi: {status_name}"
            )
            return True, None

        return False, "Gagal mengubah status"

    def assign_investigator(
        self,
        report_id: str,
        investigator_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Assign investigator to report"""
        update = ReportUpdate(assigned_to=investigator_id)
        success = self.report_repo.update(report_id, update)

        if success:
            self.message_repo.add_system_message(
                report_id,
                "Investigator telah ditugaskan untuk laporan ini"
            )
            return True, None

        return False, "Gagal menugaskan investigator"

    def update_classification(
        self,
        report_id: str,
        category: str,
        severity: str,
        summary: Optional[str] = None
    ) -> bool:
        """Update AI classification results"""
        updates = {
            'category': category,
            'severity': severity,
            'ai_classification': category,
            'ai_priority': severity
        }
        if summary:
            updates['summary'] = summary

        return self.db.update_report(report_id, updates)

    def get_messages(self, report_id: str) -> List[Message]:
        """Get all messages for a report"""
        conv_id = self.message_repo.get_or_create_conversation(report_id)
        return self.message_repo.get_messages(conv_id)

    def send_message(
        self,
        report_id: str,
        content: str,
        sender_type: str,
        sender_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Send message in report conversation.

        Args:
            report_id: Report ID
            content: Message content
            sender_type: 'reporter' or 'manager'
            sender_id: User ID if manager

        Returns:
            (success, error_message)
        """
        if not content.strip():
            return False, "Pesan tidak boleh kosong"

        try:
            conv_id = self.message_repo.get_or_create_conversation(report_id)
            data = MessageCreate(
                conversation_id=conv_id,
                sender_type=sender_type,
                content=content.strip(),
                sender_id=sender_id
            )
            self.message_repo.add_message(data)
            return True, None
        except Exception as e:
            return False, f"Gagal mengirim pesan: {str(e)}"

    def mark_messages_read(self, report_id: str, reader_type: str) -> int:
        """Mark messages as read"""
        conv_id = self.message_repo.get_or_create_conversation(report_id)
        return self.message_repo.mark_read(conv_id, reader_type)

    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        return self.db.get_statistics()

    def get_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get report submission trends"""
        return self.db.get_report_trends(days)

    def get_sla_status(self, report: Report) -> Dict[str, Any]:
        """
        Calculate SLA status for a report.

        Returns:
            Dict with SLA metrics
        """
        if not report.created_at:
            return {'status': 'unknown'}

        days_open = report.days_open
        sla_days = SLA_CONFIG['resolution']

        if report.status in ['resolved', 'closed']:
            return {
                'status': 'completed',
                'days_to_resolve': days_open,
                'within_sla': days_open <= sla_days
            }

        remaining = sla_days - days_open
        if remaining < 0:
            return {
                'status': 'overdue',
                'days_overdue': abs(remaining),
                'within_sla': False
            }
        elif remaining <= 7:
            return {
                'status': 'warning',
                'days_remaining': remaining,
                'within_sla': True
            }
        else:
            return {
                'status': 'on_track',
                'days_remaining': remaining,
                'within_sla': True
            }

    def search_reports(self, query: str, limit: int = 50) -> List[Report]:
        """Search reports by keyword"""
        all_reports = self.get_all_reports(limit=limit * 2)
        query_lower = query.lower()

        results = []
        for report in all_reports:
            if (query_lower in report.what.lower() or
                query_lower in report.who.lower() or
                query_lower in report.where.lower() or
                query_lower in (report.summary or '').lower() or
                query_lower in report.report_id.lower()):
                results.append(report)

            if len(results) >= limit:
                break

        return results
