"""
Application constants and enums
Centralized definition of all constant values
"""

from enum import Enum
from typing import Dict, List


class ReportStatus(str, Enum):
    """Report lifecycle statuses"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INVESTIGATION = "investigation"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"

    @classmethod
    def get_display_name(cls, status: str) -> str:
        """Get Indonesian display name for status"""
        names = {
            cls.SUBMITTED: "Disubmit",
            cls.UNDER_REVIEW: "Dalam Review",
            cls.INVESTIGATION: "Investigasi",
            cls.RESOLVED: "Selesai",
            cls.CLOSED: "Ditutup",
            cls.REJECTED: "Ditolak"
        }
        return names.get(status, status)

    @classmethod
    def get_all_statuses(cls) -> List[str]:
        return [s.value for s in cls]


class ReportCategory(str, Enum):
    """Report violation categories"""
    FRAUD = "fraud"
    CORRUPTION = "corruption"
    EMBEZZLEMENT = "embezzlement"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    ABUSE_OF_POWER = "abuse_of_power"
    HARASSMENT = "harassment"
    DISCRIMINATION = "discrimination"
    SAFETY_VIOLATION = "safety_violation"
    POLICY_VIOLATION = "policy_violation"
    OTHER = "other"

    @classmethod
    def get_display_name(cls, category: str) -> str:
        """Get Indonesian display name for category"""
        names = {
            cls.FRAUD: "Penipuan",
            cls.CORRUPTION: "Korupsi",
            cls.EMBEZZLEMENT: "Penggelapan",
            cls.CONFLICT_OF_INTEREST: "Konflik Kepentingan",
            cls.ABUSE_OF_POWER: "Penyalahgunaan Wewenang",
            cls.HARASSMENT: "Pelecehan",
            cls.DISCRIMINATION: "Diskriminasi",
            cls.SAFETY_VIOLATION: "Pelanggaran Keselamatan",
            cls.POLICY_VIOLATION: "Pelanggaran Kebijakan",
            cls.OTHER: "Lainnya"
        }
        return names.get(category, category)


class SeverityLevel(str, Enum):
    """Report severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def get_color(cls, severity: str) -> str:
        """Get color code for severity"""
        colors = {
            cls.CRITICAL: "#dc3545",
            cls.HIGH: "#fd7e14",
            cls.MEDIUM: "#ffc107",
            cls.LOW: "#28a745"
        }
        return colors.get(severity, "#6c757d")


class MessageType(str, Enum):
    """Message types in conversation"""
    TEXT = "text"
    CHAT = "chat"
    FILE = "file"
    STATUS_UPDATE = "status_update"
    NOTIFICATION = "notification"
    SYSTEM = "system"


class UserRole(str, Enum):
    """User roles in system"""
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"
    REPORTER = "reporter"


class SourceChannel(str, Enum):
    """Report source channels"""
    WEB = "web"
    WHATSAPP = "whatsapp"
    CHATBOT = "chatbot"
    EMAIL = "email"


# SLA Configuration (in days)
SLA_CONFIG: Dict[str, int] = {
    "acknowledgment": 1,      # 1 day to acknowledge
    "initial_review": 3,      # 3 days for initial review
    "investigation": 30,      # 30 days for investigation
    "resolution": 45,         # 45 days total resolution
}

# File upload configuration
FILE_CONFIG = {
    "max_size_mb": 10,
    "allowed_extensions": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png"],
}

# Pagination defaults
PAGINATION = {
    "default_page_size": 10,
    "max_page_size": 100,
}
