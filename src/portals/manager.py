"""
Manager Portal
Dashboard for WBS managers and investigators
"""

import streamlit as st
from datetime import datetime

from ..ui.styles import ISLAMIC_CSS, render_islamic_header, render_islamic_footer
from ..services import AuthService, ReportService
from ..config import ReportStatus, SeverityLevel, get_settings


def render_manager_portal():
    """Main entry point for manager portal"""

    # Apply CSS
    st.markdown(ISLAMIC_CSS, unsafe_allow_html=True)

    # Initialize services
    auth_service = AuthService()
    report_service = ReportService()

    # Check authentication
    if not st.session_state.get('manager_authenticated'):
        _render_login(auth_service)
        return

    # Render sidebar and main content
    _render_sidebar()

    page = st.session_state.get('manager_page', 'dashboard')

    if page == 'dashboard':
        _render_dashboard(report_service)
    elif page == 'reports':
        _render_reports_list(report_service)
    elif page == 'report_detail':
        _render_report_detail(report_service)
    elif page == 'users':
        _render_users_page(auth_service)
    elif page == 'settings':
        _render_settings_page()


def _render_login(auth_service: AuthService):
    """Render login page"""

    st.markdown(render_islamic_header("Portal Pengelola", "Login untuk Melanjutkan"), unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="islamic-card">', unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### 🔐 Login Pengelola")

            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")

            submitted = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")

            if submitted:
                result = auth_service.login_manager(username, password)

                if result.success:
                    st.session_state.manager_authenticated = True
                    st.session_state.manager_user = result.user
                    st.rerun()
                else:
                    st.error(result.error)

        st.markdown('</div>', unsafe_allow_html=True)

        # Back button
        if st.button("🏠 Kembali ke Home", use_container_width=True):
            st.session_state.current_portal = 'home'
            st.rerun()


def _render_sidebar():
    """Render sidebar navigation"""
    user = st.session_state.get('manager_user')

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2rem;">🛡️</div>
            <h2 style="color: #F4E4BA; margin: 0.5rem 0;">Portal Pengelola</h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.85rem;">
                {user.display_name if user else 'User'}<br>
                <small>{user.role.upper() if user else ''}</small>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        pages = {
            'dashboard': '📊 Dashboard',
            'reports': '📋 Laporan',
            'users': '👥 Pengguna',
            'settings': '⚙️ Pengaturan'
        }

        current_page = st.session_state.get('manager_page', 'dashboard')

        for key, label in pages.items():
            # Only show users page for admin
            if key == 'users' and (not user or user.role != 'admin'):
                continue

            if st.button(label, use_container_width=True,
                        type="primary" if key == current_page else "secondary"):
                st.session_state.manager_page = key
                st.rerun()

        st.markdown("---")

        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.manager_authenticated = False
            st.session_state.manager_user = None
            st.session_state.current_portal = 'home'
            st.rerun()


def _render_dashboard(report_service: ReportService):
    """Render dashboard page"""

    st.markdown(render_islamic_header("Dashboard", "Ringkasan Whistleblowing System"), unsafe_allow_html=True)

    # Get statistics
    stats = report_service.get_statistics()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("📋 Total Laporan", stats.get('total', 0), "#1B5E20"),
        ("📥 Laporan Baru", stats.get('by_status', {}).get('submitted', 0), "#3498DB"),
        ("🔍 Dalam Proses", stats.get('open', 0), "#F39C12"),
        ("✅ Selesai", stats.get('resolved', 0), "#27AE60")
    ]

    for col, (title, value, color) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <p style="color: #5D6D7E; margin: 0; font-size: 0.85rem;">{title}</p>
                <h2 style="color: {color}; margin: 0.25rem 0;">{value}</h2>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Distribusi Status")
        status_data = stats.get('by_status', {})
        if status_data:
            import pandas as pd
            df = pd.DataFrame([
                {'Status': ReportStatus.get_display_name(k), 'Jumlah': v}
                for k, v in status_data.items()
            ])
            st.bar_chart(df.set_index('Status'))
        else:
            st.info("Belum ada data")

    with col2:
        st.markdown("### 📈 Distribusi Kategori")
        category_data = stats.get('by_category', {})
        if category_data:
            import pandas as pd
            df = pd.DataFrame([
                {'Kategori': k, 'Jumlah': v}
                for k, v in list(category_data.items())[:5]
            ])
            st.bar_chart(df.set_index('Kategori'))
        else:
            st.info("Belum ada data")

    # Recent reports
    st.markdown("### 📋 Laporan Terbaru")

    reports = report_service.get_all_reports(limit=5)

    if reports:
        for report in reports:
            status_color = {
                'submitted': '#3498DB',
                'under_review': '#F39C12',
                'investigation': '#2E7D32',
                'resolved': '#27AE60',
                'closed': '#5D6D7E'
            }.get(report.status, '#5D6D7E')

            severity_color = SeverityLevel.get_color(report.severity) if report.severity else '#5D6D7E'

            st.markdown(f"""
            <div class="islamic-card" style="margin-bottom: 0.75rem; border-left: 4px solid {severity_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #1B5E20;">{report.report_id}</strong>
                        <span style="color: #5D6D7E; margin-left: 1rem;">
                            {report.created_at.strftime('%d %b %Y') if report.created_at else ''}
                        </span>
                    </div>
                    <span style="background: {status_color}20; color: {status_color};
                           padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                        {ReportStatus.get_display_name(report.status)}
                    </span>
                </div>
                <p style="color: #5D6D7E; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                    {report.what[:100]}{'...' if len(report.what) > 100 else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("📋 Lihat Semua Laporan", use_container_width=True):
            st.session_state.manager_page = 'reports'
            st.rerun()
    else:
        st.info("Belum ada laporan")


def _render_reports_list(report_service: ReportService):
    """Render reports list page"""

    st.markdown(render_islamic_header("Daftar Laporan", "Kelola Semua Laporan WBS"), unsafe_allow_html=True)

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter Status",
            options=['Semua'] + ReportStatus.get_all_statuses(),
            format_func=lambda x: ReportStatus.get_display_name(x) if x != 'Semua' else x
        )

    with col2:
        search = st.text_input("🔍 Cari Report ID", placeholder="WBS-2025-...")

    with col3:
        sort_by = st.selectbox("Urutkan", ["Terbaru", "Terlama", "Prioritas Tinggi"])

    # Get reports
    status = None if status_filter == 'Semua' else status_filter
    reports = report_service.get_all_reports(status=status, limit=50)

    # Filter by search
    if search:
        reports = [r for r in reports if search.upper() in r.report_id.upper()]

    # Sort
    if sort_by == "Terlama":
        reports = sorted(reports, key=lambda x: x.created_at or datetime.min)
    elif sort_by == "Prioritas Tinggi":
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, None: 4}
        reports = sorted(reports, key=lambda x: severity_order.get(x.severity, 4))

    st.markdown(f"**{len(reports)} laporan ditemukan**")

    # Display reports
    for report in reports:
        severity_color = SeverityLevel.get_color(report.severity) if report.severity else '#5D6D7E'
        status_color = {
            'submitted': '#3498DB',
            'under_review': '#F39C12',
            'investigation': '#2E7D32',
            'resolved': '#27AE60',
            'closed': '#5D6D7E',
            'rejected': '#E74C3C'
        }.get(report.status, '#5D6D7E')

        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"""
            <div class="islamic-card" style="border-left: 4px solid {severity_color}; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <strong style="color: #1B5E20; font-size: 1.1rem;">{report.report_id}</strong>
                        <br>
                        <span style="color: #5D6D7E; font-size: 0.85rem;">
                            📁 {report.category or 'Belum dikategorikan'} |
                            ⚡ {report.severity or 'N/A'} |
                            📅 {report.created_at.strftime('%d %b %Y') if report.created_at else 'N/A'}
                        </span>
                    </div>
                    <span style="background: {status_color}20; color: {status_color};
                           padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                        {ReportStatus.get_display_name(report.status)}
                    </span>
                </div>
                <p style="color: #2C3E50; margin: 0.75rem 0 0 0;">
                    {report.what[:150]}{'...' if len(report.what) > 150 else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("Detail", key=f"detail_{report.report_id}", use_container_width=True):
                st.session_state.manager_page = 'report_detail'
                st.session_state.selected_report_id = report.report_id
                st.rerun()


def _render_report_detail(report_service: ReportService):
    """Render report detail page"""

    report_id = st.session_state.get('selected_report_id')

    if not report_id:
        st.session_state.manager_page = 'reports'
        st.rerun()
        return

    report = report_service.get_report(report_id)

    if not report:
        st.error("Laporan tidak ditemukan")
        return

    st.markdown(render_islamic_header(f"Detail Laporan", report.report_id), unsafe_allow_html=True)

    # Back button
    if st.button("← Kembali ke Daftar"):
        st.session_state.manager_page = 'reports'
        st.rerun()

    # Status and info
    col1, col2 = st.columns([2, 1])

    with col1:
        # Report content
        st.markdown("### 📋 Isi Laporan")

        fields = [
            ("❓ What (Kejadian)", report.what),
            ("📍 Where (Lokasi)", report.where),
            ("🕐 When (Waktu)", report.when),
            ("👤 Who (Pihak Terlibat)", report.who),
            ("🔍 How (Kronologi)", report.how)
        ]

        for label, value in fields:
            st.markdown(f"""
            <div class="islamic-card" style="margin-bottom: 0.75rem;">
                <strong style="color: #1B5E20;">{label}</strong>
                <p style="margin: 0.5rem 0 0 0;">{value}</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # Status and actions
        st.markdown("### ⚙️ Kelola Laporan")

        # Current status
        st.markdown(f"""
        <div class="islamic-card" style="text-align: center;">
            <p style="color: #5D6D7E; margin: 0;">Status Saat Ini</p>
            <h3 style="color: #1B5E20; margin: 0.5rem 0;">
                {ReportStatus.get_display_name(report.status)}
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Update status
        new_status = st.selectbox(
            "Ubah Status",
            options=ReportStatus.get_all_statuses(),
            index=ReportStatus.get_all_statuses().index(report.status) if report.status in ReportStatus.get_all_statuses() else 0,
            format_func=ReportStatus.get_display_name
        )

        notes = st.text_area("Catatan", placeholder="Tambahkan catatan...")

        if st.button("💾 Simpan Perubahan", use_container_width=True, type="primary"):
            success, error = report_service.update_status(
                report.report_id,
                new_status,
                notes
            )
            if success:
                st.success("Status berhasil diperbarui")
                st.rerun()
            else:
                st.error(error)

        st.markdown("---")

        # Messages
        st.markdown("### 💬 Pesan")

        messages = report_service.get_messages(report.report_id)

        message_container = st.container(height=200)
        with message_container:
            for msg in messages[-10:]:  # Last 10 messages
                if msg.sender_type == 'reporter':
                    st.markdown(f"**Pelapor:** {msg.content}")
                else:
                    st.markdown(f"**Anda:** {msg.content}")

        # Send message
        new_msg = st.text_input("Kirim pesan", placeholder="Ketik pesan...")
        if st.button("📤 Kirim", use_container_width=True):
            if new_msg:
                user = st.session_state.get('manager_user')
                success, error = report_service.send_message(
                    report.report_id,
                    new_msg,
                    'manager',
                    user.id if user else None
                )
                if success:
                    st.rerun()
                else:
                    st.error(error)


def _render_users_page(auth_service: AuthService):
    """Render users management page (admin only)"""

    st.markdown(render_islamic_header("Manajemen Pengguna", "Kelola Tim Pengelola WBS"), unsafe_allow_html=True)

    from ..database import get_database, UserRepository

    db = get_database()
    user_repo = UserRepository(db)

    users = user_repo.get_all()

    st.markdown(f"**{len(users)} pengguna terdaftar**")

    for user in users:
        role_color = '#1B5E20' if user.role == 'admin' else '#3498DB'

        st.markdown(f"""
        <div class="islamic-card" style="margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #1B5E20;">{user.full_name}</strong>
                    <span style="color: #5D6D7E; margin-left: 0.5rem;">@{user.username}</span>
                </div>
                <span style="background: {role_color}20; color: {role_color};
                       padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.8rem;">
                    {user.role.upper()}
                </span>
            </div>
            <p style="color: #5D6D7E; margin: 0.5rem 0 0 0; font-size: 0.85rem;">
                Unit: {user.unit or 'N/A'} | Email: {user.email or 'N/A'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Add new user form
    st.markdown("---")
    st.markdown("### ➕ Tambah Pengguna Baru")

    with st.form("add_user"):
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("Username")
            new_fullname = st.text_input("Nama Lengkap")
            new_email = st.text_input("Email")

        with col2:
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["investigator", "admin", "viewer"])
            new_unit = st.text_input("Unit")

        if st.form_submit_button("➕ Tambah User", use_container_width=True, type="primary"):
            user_id, error = auth_service.create_user(
                username=new_username,
                password=new_password,
                full_name=new_fullname,
                role=new_role,
                unit=new_unit,
                email=new_email
            )
            if user_id:
                st.success(f"User {new_username} berhasil dibuat")
                st.rerun()
            else:
                st.error(error)


def _render_settings_page():
    """Render settings page"""

    st.markdown(render_islamic_header("Pengaturan", "Konfigurasi Sistem WBS"), unsafe_allow_html=True)

    settings = get_settings()

    st.markdown("### ⚙️ Konfigurasi Sistem")

    st.markdown(f"""
    <div class="islamic-card">
        <h4 style="color: #1B5E20; margin-top: 0;">Database</h4>
        <p>Mode: <strong>{settings.database.mode.upper()}</strong></p>
        {'<p>URL: ' + settings.database.supabase_url + '</p>' if settings.database.is_supabase else ''}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="islamic-card" style="margin-top: 1rem;">
        <h4 style="color: #1B5E20; margin-top: 0;">WhatsApp Integration</h4>
        <p>Status: <strong>{'Enabled' if settings.waha.enabled else 'Disabled'}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="islamic-card" style="margin-top: 1rem;">
        <h4 style="color: #1B5E20; margin-top: 0;">Email Notification</h4>
        <p>Status: <strong>{'Enabled' if settings.email.enabled else 'Disabled'}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Health check
    st.markdown("---")
    st.markdown("### 🔍 Health Check")

    from ..database import get_database

    db = get_database()
    db_status = "✅ Connected" if db.health_check() else "❌ Disconnected"

    st.markdown(f"**Database:** {db_status}")
