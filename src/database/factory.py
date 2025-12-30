"""
Database Factory
Creates the appropriate database instance based on configuration
"""

from functools import lru_cache
from typing import Optional

from .base import DatabaseInterface
from ..config import get_settings


class DatabaseFactory:
    """Factory for creating database instances"""

    _instance: Optional[DatabaseInterface] = None

    @classmethod
    def create(cls, force_new: bool = False) -> DatabaseInterface:
        """
        Create database instance based on settings.

        Args:
            force_new: If True, create new instance even if one exists

        Returns:
            DatabaseInterface implementation
        """
        if cls._instance is not None and not force_new:
            return cls._instance

        settings = get_settings()

        if settings.database.is_supabase:
            from .supabase import SupabaseDatabase
            cls._instance = SupabaseDatabase(
                url=settings.database.supabase_url,
                key=settings.database.supabase_key
            )
        else:
            from .sqlite import SQLiteDatabase
            cls._instance = SQLiteDatabase(
                db_path=settings.database.sqlite_path
            )

        return cls._instance

    @classmethod
    def get_instance(cls) -> DatabaseInterface:
        """Get existing instance or create new one"""
        if cls._instance is None:
            return cls.create()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton instance"""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None


@lru_cache()
def get_database() -> DatabaseInterface:
    """
    Get cached database instance.
    Use this function throughout the application.
    """
    return DatabaseFactory.create()


# Backward compatibility alias
def WBSDatabase(db_path: str = None) -> DatabaseInterface:
    """
    Backward compatibility wrapper.
    Ignores db_path and uses settings-based configuration.
    """
    return get_database()
