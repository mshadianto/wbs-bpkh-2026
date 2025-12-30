"""Database module with repository pattern"""

from .base import DatabaseInterface
from .factory import get_database, DatabaseFactory
from .repositories import ReportRepository, UserRepository, MessageRepository

__all__ = [
    'DatabaseInterface',
    'get_database',
    'DatabaseFactory',
    'ReportRepository',
    'UserRepository',
    'MessageRepository'
]
