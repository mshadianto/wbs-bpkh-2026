"""
Authentication Service
Handles user and reporter authentication
"""

import hashlib
from typing import Optional, Tuple
from dataclasses import dataclass

import bcrypt

from ..database import get_database, ReportRepository, UserRepository
from ..models import User


@dataclass
class AuthResult:
    """Authentication result"""
    success: bool
    user: Optional[User] = None
    error: Optional[str] = None


class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        self.db = get_database()
        self.user_repo = UserRepository(self.db)

    def login_manager(self, username: str, password: str) -> AuthResult:
        """
        Authenticate manager/investigator login.

        Args:
            username: User username
            password: Plain text password

        Returns:
            AuthResult with user data if successful
        """
        if not username or not password:
            return AuthResult(success=False, error="Username dan password harus diisi")

        user = self.user_repo.verify(username, password)

        if user:
            if not user.is_active:
                return AuthResult(success=False, error="Akun tidak aktif")
            return AuthResult(success=True, user=user)

        return AuthResult(success=False, error="Username atau password salah")

    def verify_reporter_access(self, report_id: str, pin: str) -> Tuple[bool, Optional[str]]:
        """
        Verify reporter access with Report ID and PIN.

        Args:
            report_id: Report ID (e.g., WBS-2025-000001)
            pin: 6-digit PIN

        Returns:
            (success, error_message)
        """
        if not report_id:
            return False, "Report ID harus diisi"

        if not pin or len(pin) != 6:
            return False, "PIN harus 6 digit"

        report_repo = ReportRepository(self.db)
        if report_repo.verify_access(report_id, pin):
            return True, None

        return False, "Report ID atau PIN tidak valid"

    def verify_reporter_anonymous(self, report_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify reporter access with Report ID only (for anonymous chat).

        Args:
            report_id: Report ID

        Returns:
            (success, error_message)
        """
        if not report_id:
            return False, "Report ID harus diisi"

        report_repo = ReportRepository(self.db)
        report = report_repo.get_by_id(report_id)

        if report:
            return True, None

        return False, "Report ID tidak ditemukan"

    def create_user(
        self,
        username: str,
        password: str,
        full_name: str,
        role: str = "investigator",
        unit: Optional[str] = None,
        email: Optional[str] = None
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Create new user account.

        Returns:
            (user_id, error_message)
        """
        # Validate
        if not username or len(username) < 3:
            return None, "Username minimal 3 karakter"

        if not password or len(password) < 6:
            return None, "Password minimal 6 karakter"

        if not full_name:
            return None, "Nama lengkap harus diisi"

        # Check if username exists
        existing = self.user_repo.get_by_username(username)
        if existing:
            return None, "Username sudah digunakan"

        try:
            from ..models import UserCreate
            user_data = UserCreate(
                username=username,
                password=password,
                full_name=full_name,
                role=role,
                unit=unit,
                email=email
            )
            user_id = self.user_repo.create(user_data)
            return user_id, None
        except Exception as e:
            return None, f"Gagal membuat user: {str(e)}"

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user password.

        Returns:
            (success, error_message)
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "User tidak ditemukan"

        # Verify old password
        if not bcrypt.checkpw(old_password.encode(), user.password_hash.encode()):
            return False, "Password lama salah"

        if len(new_password) < 6:
            return False, "Password baru minimal 6 karakter"

        # Update password
        new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        success = self.db.update_user(user_id, {'password_hash': new_hash})

        if success:
            return True, None
        return False, "Gagal mengubah password"

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash PIN using SHA256"""
        return hashlib.sha256(pin.encode()).hexdigest()
