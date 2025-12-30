"""
Application Settings
Centralized configuration management using environment variables
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseSettings:
    """Database configuration"""
    mode: str = field(default_factory=lambda: os.getenv("DB_MODE", "sqlite"))
    sqlite_path: str = field(default_factory=lambda: os.getenv("DB_PATH", "wbs_database.db"))
    supabase_url: Optional[str] = field(default_factory=lambda: os.getenv("SUPABASE_URL"))
    supabase_key: Optional[str] = field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY"))

    @property
    def is_supabase(self) -> bool:
        return self.mode.lower() == "supabase"


@dataclass
class AISettings:
    """AI/LLM configuration"""
    provider: str = field(default_factory=lambda: os.getenv("AI_PROVIDER", "anthropic"))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    model: str = field(default_factory=lambda: os.getenv("AI_MODEL", "claude-3-haiku-20240307"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("AI_MAX_TOKENS", "1024")))
    temperature: float = field(default_factory=lambda: float(os.getenv("AI_TEMPERATURE", "0.3")))


@dataclass
class WAHASettings:
    """WhatsApp/WAHA integration configuration"""
    enabled: bool = field(default_factory=lambda: os.getenv("WAHA_ENABLED", "false").lower() == "true")
    api_url: str = field(default_factory=lambda: os.getenv("WAHA_API_URL", "http://localhost:3000"))
    session_name: str = field(default_factory=lambda: os.getenv("WAHA_SESSION", "default"))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("WAHA_API_KEY"))


@dataclass
class EmailSettings:
    """Email notification configuration"""
    enabled: bool = field(default_factory=lambda: os.getenv("EMAIL_ENABLED", "false").lower() == "true")
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: Optional[str] = field(default_factory=lambda: os.getenv("SMTP_USER"))
    smtp_password: Optional[str] = field(default_factory=lambda: os.getenv("SMTP_PASSWORD"))
    from_email: str = field(default_factory=lambda: os.getenv("FROM_EMAIL", "wbs@bpkh.go.id"))


@dataclass
class AppSettings:
    """General application settings"""
    name: str = "WBS BPKH"
    version: str = "2.0.0"
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "wbs-bpkh-secret-key-2025"))
    base_url: str = field(default_factory=lambda: os.getenv("BASE_URL", "http://localhost:8501"))

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)

    @property
    def uploads_dir(self) -> Path:
        path = self.base_dir / "uploads"
        path.mkdir(exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        path = self.base_dir / "logs"
        path.mkdir(exist_ok=True)
        return path


@dataclass
class ContactInfo:
    """Organization contact information"""
    email: str = "wbs@bpkh.go.id"
    whatsapp: str = "+62 21 1234 5678"
    web_portal: str = "https://wbs.bpkh.go.id"
    hotline: str = "1500-123"

    def to_dict(self) -> Dict[str, str]:
        return {
            "Email": self.email,
            "WhatsApp": self.whatsapp,
            "Web Portal": self.web_portal,
            "Hotline": self.hotline
        }


@dataclass
class Settings:
    """Main settings container"""
    app: AppSettings = field(default_factory=AppSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    ai: AISettings = field(default_factory=AISettings)
    waha: WAHASettings = field(default_factory=WAHASettings)
    email: EmailSettings = field(default_factory=EmailSettings)
    contact: ContactInfo = field(default_factory=ContactInfo)

    def __post_init__(self):
        """Validate settings after initialization"""
        if self.database.is_supabase:
            if not self.database.supabase_url or not self.database.supabase_key:
                raise ValueError("Supabase URL and key required when DB_MODE=supabase")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use this function to access settings throughout the application.
    """
    return Settings()
