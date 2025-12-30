"""
Base model classes
Provides common functionality for all models
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from abc import ABC


@dataclass
class BaseModel(ABC):
    """Base class for all models"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary"""
        # Filter only valid fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)


@dataclass
class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix"""
    import uuid
    unique = uuid.uuid4().hex[:8].upper()
    if prefix:
        return f"{prefix}-{unique}"
    return unique
