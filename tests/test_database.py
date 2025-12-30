"""
Database Tests
Tests for database operations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from database import get_database, ReportRepository, UserRepository, MessageRepository
from models import ReportCreate, UserCreate


class TestDatabase:
    """Test database operations"""

    def setup_method(self):
        """Setup test database"""
        # Use SQLite for testing
        import os
        os.environ['DB_MODE'] = 'sqlite'
        os.environ['DB_PATH'] = ':memory:'

        # Get fresh database
        from database.factory import DatabaseFactory
        DatabaseFactory.reset()
        self.db = get_database()

    def test_health_check(self):
        """Test database health check"""
        assert self.db.health_check() is True

    def test_insert_report(self):
        """Test report insertion"""
        report_data = {
            'what': 'Test violation description that is long enough',
            'where_location': 'Test Location',
            'when_time': 'January 2025',
            'who_involved': 'Test Person',
            'how_method': 'Test method description'
        }

        report_id, pin = self.db.insert_report(report_data)

        assert report_id.startswith('WBS-')
        assert len(pin) == 6
        assert pin.isdigit()

    def test_get_report(self):
        """Test report retrieval"""
        # Insert first
        report_data = {
            'what': 'Test violation description that is long enough',
            'where_location': 'Test Location',
            'when_time': 'January 2025',
            'who_involved': 'Test Person',
            'how_method': 'Test method description'
        }

        report_id, pin = self.db.insert_report(report_data)

        # Retrieve
        report = self.db.get_report_by_id(report_id)

        assert report is not None
        assert report['report_id'] == report_id
        assert report['what'] == report_data['what']

    def test_verify_access(self):
        """Test report access verification"""
        report_data = {
            'what': 'Test violation description that is long enough',
            'where_location': 'Test Location',
            'when_time': 'January 2025',
            'who_involved': 'Test Person',
            'how_method': 'Test method description'
        }

        report_id, pin = self.db.insert_report(report_data)

        # Correct PIN
        assert self.db.verify_report_access(report_id, pin) is True

        # Wrong PIN
        assert self.db.verify_report_access(report_id, '000000') is False

    def test_user_operations(self):
        """Test user CRUD operations"""
        # Get admin user (created by default)
        user = self.db.get_user_by_username('admin')

        assert user is not None
        assert user['role'] == 'admin'

    def test_verify_user(self):
        """Test user verification"""
        # Default admin credentials
        user = self.db.verify_user('admin', 'admin123')

        assert user is not None
        assert user['username'] == 'admin'

        # Wrong password
        user = self.db.verify_user('admin', 'wrongpassword')
        assert user is None

    def test_statistics(self):
        """Test statistics generation"""
        stats = self.db.get_statistics()

        assert 'total' in stats
        assert 'by_status' in stats
        assert isinstance(stats['total'], int)


class TestReportRepository:
    """Test ReportRepository"""

    def setup_method(self):
        """Setup"""
        import os
        os.environ['DB_MODE'] = 'sqlite'
        os.environ['DB_PATH'] = ':memory:'

        from database.factory import DatabaseFactory
        DatabaseFactory.reset()
        self.db = get_database()
        self.repo = ReportRepository(self.db)

    def test_create_and_get(self):
        """Test report creation via repository"""
        data = ReportCreate(
            what='Test violation that is detailed enough for validation',
            where='Jakarta Office',
            when='December 2025',
            who='Manager XYZ',
            how='Through manipulation of records'
        )

        report_id, pin = self.repo.create(data)

        assert report_id is not None

        # Get it back
        report = self.repo.get_by_id(report_id)

        assert report is not None
        assert report.report_id == report_id


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
