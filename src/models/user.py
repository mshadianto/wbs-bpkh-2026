"""
User models
Defines user/manager accounts
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class UserCreate:
    """Data required to create a new user"""
    username: str
    password: str  # Plain text, will be hashed
    full_name: str
    role: str = "investigator"
    unit: Optional[str] = None
    email: Optional[str] = None

    def validate(self) -> list:
        """Validate user data"""
        errors = []
        if not self.username or len(self.username) < 3:
            errors.append("Username minimal 3 karakter")
        if not self.password or len(self.password) < 6:
            errors.append("Password minimal 6 karakter")
        if not self.full_name:
            errors.append("Nama lengkap harus diisi")
        if self.role not in ["admin", "investigator", "viewer"]:
            errors.append("Role tidak valid")
        return errors


@dataclass
class User:
    """Complete user model"""
    id: int
    username: str
    password_hash: str
    full_name: str
    role: str = "investigator"
    unit: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def can_assign(self) -> bool:
        return self.role in ["admin", "investigator"]

    @property
    def display_name(self) -> str:
        return self.full_name or self.username

    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'unit': self.unit,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'User':
        """Create User from database row"""
        created_at = row.get('created_at')
        last_login = row.get('last_login')

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00'))

        return cls(
            id=row.get('id', 0),
            username=row.get('username', ''),
            password_hash=row.get('password_hash', ''),
            full_name=row.get('full_name', ''),
            role=row.get('role', 'investigator'),
            unit=row.get('unit'),
            email=row.get('email'),
            is_active=row.get('is_active', True),
            created_at=created_at,
            last_login=last_login
        )
