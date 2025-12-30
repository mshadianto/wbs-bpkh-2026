"""
Authentication Module for WBS BPKH
Reporter (PIN-based) and Manager (login-based) authentication
"""

import streamlit as st
from typing import Optional, Dict
from database import WBSDatabase


class ReporterAuth:
    """Authentication handler for reporters using Report ID + PIN"""

    def __init__(self, db: WBSDatabase):
        self.db = db

    def validate_access(self, report_id: str, pin: str) -> bool:
        """Validate Report ID + PIN combination"""
        if not report_id or not pin:
            return False
        return self.db.validate_report_access(report_id, pin)

    def get_report(self, report_id: str) -> Optional[Dict]:
        """Get sanitized report for reporter view"""
        return self.db.get_report_for_reporter(report_id)

    def get_full_report(self, report_id: str) -> Optional[Dict]:
        """Get full report data"""
        return self.db.get_report(report_id)

    def get_messages(self, report_id: str) -> list:
        """Get messages for report"""
        return self.db.get_messages(report_id)

    def send_message(self, report_id: str, content: str) -> bool:
        """Send message as reporter"""
        return self.db.add_message(report_id, 'reporter', content)

    def mark_read(self, report_id: str) -> bool:
        """Mark messages as read by reporter"""
        return self.db.mark_messages_read(report_id, 'reporter')


class ManagerAuth:
    """Authentication handler for managers using username/password"""

    def __init__(self, db: WBSDatabase):
        self.db = db

    def login(self, username: str, password: str) -> Optional[Dict]:
        """Validate login credentials"""
        if not username or not password:
            return None
        return self.db.validate_user(username, password)

    def logout(self):
        """Clear session"""
        if 'manager_user' in st.session_state:
            del st.session_state.manager_user
        if 'manager_authenticated' in st.session_state:
            del st.session_state.manager_authenticated

    def is_authenticated(self) -> bool:
        """Check if manager is authenticated"""
        return st.session_state.get('manager_authenticated', False)

    def get_current_user(self) -> Optional[Dict]:
        """Get current logged in user"""
        return st.session_state.get('manager_user', None)

    def has_role(self, *roles) -> bool:
        """Check if current user has one of the specified roles"""
        user = self.get_current_user()
        if not user:
            return False
        return user.get('role') in roles

    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.has_role('admin')

    def can_manage_users(self) -> bool:
        """Check if current user can manage users"""
        return self.has_role('admin')

    def can_assign_investigators(self) -> bool:
        """Check if current user can assign investigators"""
        return self.has_role('admin', 'manager')

    def can_view_all_reports(self) -> bool:
        """Check if current user can view all reports"""
        return self.has_role('admin', 'manager', 'auditor')

    def get_accessible_reports(self) -> list:
        """Get reports accessible to current user based on role"""
        user = self.get_current_user()
        if not user:
            return []

        role = user.get('role')
        if role in ['admin', 'auditor']:
            # Can see all reports
            return self.db.get_all_reports(limit=500)
        elif role == 'manager':
            # Can see reports in their unit
            unit = user.get('unit')
            if unit:
                return self.db.get_reports_by_unit(unit)
            return self.db.get_all_reports(limit=500)
        elif role == 'investigator':
            # Can see only assigned reports
            return self.db.get_reports_by_investigator(user.get('id'))
        return []


def init_session_state():
    """Initialize authentication session state"""
    if 'manager_authenticated' not in st.session_state:
        st.session_state.manager_authenticated = False
    if 'manager_user' not in st.session_state:
        st.session_state.manager_user = None
    if 'reporter_authenticated' not in st.session_state:
        st.session_state.reporter_authenticated = False
    if 'reporter_report_id' not in st.session_state:
        st.session_state.reporter_report_id = None


def render_login_form(manager_auth: ManagerAuth) -> bool:
    """Render manager login form and handle authentication"""
    st.markdown("## Login Pengelola WBS")
    st.markdown("Masukkan kredensial Anda untuk mengakses sistem.")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        submit = st.form_submit_button("Login", use_container_width=True)

    if submit:
        if username and password:
            user = manager_auth.login(username, password)
            if user:
                st.session_state.manager_authenticated = True
                st.session_state.manager_user = user
                st.success(f"Selamat datang, {user['full_name']}!")
                st.rerun()
            else:
                st.error("Username atau password salah!")
        else:
            st.warning("Mohon masukkan username dan password.")

    st.markdown("---")
    st.markdown("**Default Admin:**")
    st.code("Username: admin\nPassword: admin123")

    return st.session_state.get('manager_authenticated', False)


def render_reporter_access_form(reporter_auth: ReporterAuth) -> Optional[str]:
    """Render reporter access form and return report_id if valid"""
    st.markdown("## Lacak Laporan")
    st.markdown("Masukkan Report ID dan PIN yang Anda terima saat melapor.")

    with st.form("reporter_access_form"):
        report_id = st.text_input("Report ID", placeholder="WBS-2025-000001")
        pin = st.text_input("PIN", type="password", max_chars=6, placeholder="6 digit PIN")
        submit = st.form_submit_button("Akses Laporan", use_container_width=True)

    if submit:
        if report_id and pin:
            if reporter_auth.validate_access(report_id, pin):
                st.session_state.reporter_authenticated = True
                st.session_state.reporter_report_id = report_id
                st.success("Akses diberikan!")
                st.rerun()
            else:
                st.error("Report ID atau PIN tidak valid!")
        else:
            st.warning("Mohon masukkan Report ID dan PIN.")

    return st.session_state.get('reporter_report_id', None)


def require_manager_auth(manager_auth: ManagerAuth):
    """Decorator-like function to require manager authentication"""
    if not manager_auth.is_authenticated():
        render_login_form(manager_auth)
        st.stop()


def require_reporter_auth(reporter_auth: ReporterAuth):
    """Decorator-like function to require reporter authentication"""
    if not st.session_state.get('reporter_authenticated', False):
        render_reporter_access_form(reporter_auth)
        st.stop()
