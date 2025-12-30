"""
Repository classes
High-level data access with model conversion
"""

from typing import List, Optional
from ..models import Report, ReportCreate, ReportUpdate, User, UserCreate, Message, MessageCreate, Conversation
from .base import DatabaseInterface


class ReportRepository:
    """Repository for Report operations"""

    def __init__(self, db: DatabaseInterface):
        self.db = db

    def create(self, data: ReportCreate) -> tuple:
        """Create new report, returns (report_id, pin)"""
        report_data = {
            'what': data.what,
            'where_location': data.where,
            'when_time': data.when,
            'who_involved': data.who,
            'how_method': data.how,
            'evidence_description': data.evidence_description,
            'source_channel': data.source_channel
        }
        return self.db.insert_report(report_data)

    def get_by_id(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        row = self.db.get_report_by_id(report_id)
        if row:
            return Report.from_db_row(row)
        return None

    def get_all(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Report]:
        """Get all reports with filters"""
        rows = self.db.get_all_reports(status, category, limit, offset)
        return [Report.from_db_row(row) for row in rows]

    def update(self, report_id: str, data: ReportUpdate) -> bool:
        """Update report"""
        updates = {}
        if data.status:
            updates['status'] = data.status
        if data.category:
            updates['category'] = data.category
        if data.severity:
            updates['severity'] = data.severity
        if data.assigned_to:
            updates['assigned_to'] = data.assigned_to
        if data.resolution_notes:
            updates['resolution_notes'] = data.resolution_notes

        if updates:
            return self.db.update_report(report_id, updates)
        return False

    def verify_access(self, report_id: str, pin: str) -> bool:
        """Verify reporter access with PIN"""
        return self.db.verify_report_access(report_id, pin)

    def get_open_reports(self) -> List[Report]:
        """Get all open (non-resolved) reports"""
        reports = []
        for status in ['submitted', 'under_review', 'investigation']:
            reports.extend(self.get_all(status=status))
        return reports

    def get_critical_reports(self) -> List[Report]:
        """Get critical severity reports"""
        all_reports = self.get_all()
        return [r for r in all_reports if r.severity == 'critical']


class UserRepository:
    """Repository for User operations"""

    def __init__(self, db: DatabaseInterface):
        self.db = db

    def create(self, data: UserCreate) -> int:
        """Create new user, returns user_id"""
        import bcrypt
        password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

        user_data = {
            'username': data.username,
            'password_hash': password_hash,
            'full_name': data.full_name,
            'role': data.role,
            'unit': data.unit,
            'email': data.email
        }
        return self.db.create_user(user_data)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        row = self.db.get_user_by_username(username)
        if row:
            return User.from_db_row(row)
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        row = self.db.get_user_by_id(user_id)
        if row:
            return User.from_db_row(row)
        return None

    def get_all(self, role: Optional[str] = None) -> List[User]:
        """Get all users"""
        rows = self.db.get_all_users(role)
        return [User.from_db_row(row) for row in rows]

    def verify(self, username: str, password: str) -> Optional[User]:
        """Verify credentials and return user"""
        row = self.db.verify_user(username, password)
        if row:
            return User.from_db_row(row)
        return None

    def get_investigators(self) -> List[User]:
        """Get all investigators"""
        return self.get_all(role='investigator')

    def get_admins(self) -> List[User]:
        """Get all admins"""
        return self.get_all(role='admin')


class MessageRepository:
    """Repository for Message and Conversation operations"""

    def __init__(self, db: DatabaseInterface):
        self.db = db

    def get_or_create_conversation(self, report_id: str) -> int:
        """Get or create conversation for report"""
        return self.db.get_or_create_conversation(report_id)

    def add_message(self, data: MessageCreate) -> int:
        """Add message to conversation"""
        return self.db.add_message(
            conversation_id=data.conversation_id,
            sender_type=data.sender_type,
            content=data.content,
            sender_id=data.sender_id,
            message_type=data.message_type
        )

    def get_messages(
        self,
        conversation_id: int,
        limit: int = 100
    ) -> List[Message]:
        """Get messages for conversation"""
        rows = self.db.get_messages(conversation_id, limit)
        return [Message.from_db_row(row) for row in rows]

    def mark_read(self, conversation_id: int, reader_type: str) -> int:
        """Mark messages as read"""
        return self.db.mark_messages_read(conversation_id, reader_type)

    def send_reporter_message(
        self,
        report_id: str,
        content: str
    ) -> int:
        """Send message from reporter"""
        conv_id = self.get_or_create_conversation(report_id)
        return self.db.add_message(conv_id, 'reporter', content)

    def send_manager_message(
        self,
        report_id: str,
        content: str,
        sender_id: int
    ) -> int:
        """Send message from manager"""
        conv_id = self.get_or_create_conversation(report_id)
        return self.db.add_message(conv_id, 'manager', content, sender_id)

    def add_system_message(
        self,
        report_id: str,
        content: str
    ) -> int:
        """Add system notification message"""
        conv_id = self.get_or_create_conversation(report_id)
        return self.db.add_message(conv_id, 'system', content, message_type='notification')
