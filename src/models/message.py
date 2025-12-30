"""
Message and Conversation models
For communication between reporter and manager
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class MessageCreate:
    """Data required to create a new message"""
    conversation_id: int
    sender_type: str  # 'reporter' or 'manager'
    content: str
    sender_id: Optional[int] = None  # user_id for manager
    message_type: str = "chat"

    def validate(self) -> list:
        """Validate message data"""
        errors = []
        if not self.content or len(self.content.strip()) == 0:
            errors.append("Pesan tidak boleh kosong")
        if self.sender_type not in ["reporter", "manager", "system"]:
            errors.append("Tipe pengirim tidak valid")
        return errors


@dataclass
class Message:
    """Complete message model"""
    id: int
    conversation_id: int
    sender_type: str
    sender_id: Optional[int]
    content: str
    message_type: str = "chat"
    is_read: bool = False
    created_at: Optional[datetime] = None

    @property
    def is_from_reporter(self) -> bool:
        return self.sender_type == "reporter"

    @property
    def is_from_manager(self) -> bool:
        return self.sender_type == "manager"

    @property
    def is_system_message(self) -> bool:
        return self.sender_type == "system" or self.message_type in ["status_update", "notification"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'content': self.content,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Message':
        """Create Message from database row"""
        created_at = row.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        return cls(
            id=row.get('id', 0),
            conversation_id=row.get('conversation_id', 0),
            sender_type=row.get('sender_type', ''),
            sender_id=row.get('sender_id'),
            content=row.get('content', ''),
            message_type=row.get('message_type', 'chat'),
            is_read=row.get('is_read', False),
            created_at=created_at
        )


@dataclass
class Conversation:
    """Conversation thread for a report"""
    id: int
    report_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    messages: List[Message] = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def unread_count(self) -> int:
        return sum(1 for m in self.messages if not m.is_read)

    @property
    def last_message(self) -> Optional[Message]:
        if self.messages:
            return self.messages[-1]
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'report_id': self.report_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': self.message_count,
            'unread_count': self.unread_count
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Conversation':
        """Create Conversation from database row"""
        created_at = row.get('created_at')
        updated_at = row.get('updated_at')

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        return cls(
            id=row.get('id', 0),
            report_id=row.get('report_id', ''),
            created_at=created_at,
            updated_at=updated_at
        )
