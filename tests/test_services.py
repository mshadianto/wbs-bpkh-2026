"""
Services Tests
Tests for business logic services
"""

import pytest
from src.services import AuthService, ReportService
from src.models import ReportCreate
from src.database.factory import DatabaseFactory


class TestAuthService:
    """Test AuthService"""

    def setup_method(self):
        DatabaseFactory.reset()
        self.service = AuthService()

    def test_login_manager_success(self):
        """Test successful manager login"""
        result = self.service.login_manager('admin', 'admin123')

        assert result.success is True
        assert result.user is not None
        assert result.user.username == 'admin'

    def test_login_manager_fail(self):
        """Test failed manager login"""
        result = self.service.login_manager('admin', 'wrongpassword')

        assert result.success is False
        assert result.error is not None

    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        result = self.service.login_manager('', '')

        assert result.success is False


class TestReportService:
    """Test ReportService"""

    def setup_method(self):
        DatabaseFactory.reset()
        self.service = ReportService()

    def test_submit_report_success(self):
        """Test successful report submission"""
        data = ReportCreate(
            what='Detailed description of violation that is long enough',
            where='Jakarta Head Office',
            when='January 2025',
            who='Department Manager',
            how='Through manipulation of financial documents'
        )

        result = self.service.submit_report(data)

        assert result.success is True
        assert result.report_id is not None
        assert result.pin is not None
        assert len(result.pin) == 6

    def test_submit_report_validation_fail(self):
        """Test report submission with invalid data"""
        data = ReportCreate(
            what='Short',  # Too short
            where='',
            when='',
            who='',
            how=''
        )

        result = self.service.submit_report(data)

        assert result.success is False
        assert result.error is not None

    def test_get_report(self):
        """Test get report"""
        # First submit
        data = ReportCreate(
            what='Detailed description of violation that is long enough',
            where='Jakarta',
            when='Januari 2025',
            who='Manager',
            how='Through illegal means'
        )

        submit_result = self.service.submit_report(data)

        # Then get
        report = self.service.get_report(submit_result.report_id)

        assert report is not None
        assert report.report_id == submit_result.report_id

    def test_update_status(self):
        """Test status update"""
        # Submit
        data = ReportCreate(
            what='Detailed description of violation that is long enough',
            where='Jakarta',
            when='Januari 2025',
            who='Manager',
            how='Through illegal means'
        )

        submit_result = self.service.submit_report(data)

        # Update
        success, error = self.service.update_status(
            submit_result.report_id,
            'under_review',
            'Started review process'
        )

        assert success is True

        # Verify
        report = self.service.get_report(submit_result.report_id)
        assert report.status == 'under_review'

    def test_statistics(self):
        """Test statistics generation"""
        stats = self.service.get_statistics()

        assert 'total' in stats
        assert 'by_status' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
