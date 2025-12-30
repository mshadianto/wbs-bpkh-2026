"""
Database Interface
Abstract base class defining the database contract
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class DatabaseInterface(ABC):
    """
    Abstract database interface.
    All database implementations must follow this contract.
    """

    # ==================== Report Operations ====================

    @abstractmethod
    def insert_report(self, report_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Insert a new report.
        Returns: (report_id, pin)
        """
        pass

    @abstractmethod
    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report by report_id"""
        pass

    @abstractmethod
    def get_all_reports(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all reports with optional filters"""
        pass

    @abstractmethod
    def update_report(self, report_id: str, updates: Dict[str, Any]) -> bool:
        """Update report fields"""
        pass

    @abstractmethod
    def verify_report_access(self, report_id: str, pin: str) -> bool:
        """Verify reporter PIN access"""
        pass

    # ==================== User Operations ====================

    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """Create new user, return user_id"""
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        pass

    @abstractmethod
    def get_all_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all users with optional role filter"""
        pass

    @abstractmethod
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials, return user data if valid"""
        pass

    @abstractmethod
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user fields"""
        pass

    # ==================== Message Operations ====================

    @abstractmethod
    def get_or_create_conversation(self, report_id: str) -> int:
        """Get existing or create new conversation, return conversation_id"""
        pass

    @abstractmethod
    def add_message(
        self,
        conversation_id: int,
        sender_type: str,
        content: str,
        sender_id: Optional[int] = None,
        message_type: str = "chat"
    ) -> int:
        """Add message to conversation, return message_id"""
        pass

    @abstractmethod
    def get_messages(
        self,
        conversation_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages for conversation"""
        pass

    @abstractmethod
    def mark_messages_read(
        self,
        conversation_id: int,
        reader_type: str
    ) -> int:
        """Mark messages as read, return count of updated messages"""
        pass

    # ==================== Statistics ====================

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get dashboard statistics.
        Returns dict with counts by status, category, severity, etc.
        """
        pass

    @abstractmethod
    def get_report_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get report submission trends over time"""
        pass

    # ==================== Utility ====================

    @abstractmethod
    def health_check(self) -> bool:
        """Check database connectivity"""
        pass

    def close(self):
        """Close database connection (optional override)"""
        pass
