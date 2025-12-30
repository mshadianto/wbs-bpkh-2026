"""
WBS BPKH - Manager Interface (Pengelola WBS)
Dashboard untuk pengelolaan laporan whistleblowing
"""

import streamlit as st
import json
from datetime import datetime

from config import AppConfig, REPORT_STATUSES, USER_ROLES, ROUTING_UNITS
from db_factory import get_database
from auth import ManagerAuth, init_session_state, render_login_form
from utils import format_datetime, get_severity_icon, get_severity_color
from styles import ISLAMIC_CSS, ARABIC_TEXTS, render_islamic_footer

# Initialize config
config = AppConfig()


def get_db():
    """Get or create database connection"""
    if "db" not in st.session_state:
        st.session_state.db = get_database()
    return st.session_state.db


def get_manager_auth():
    """Get or create manager auth"""
    if "manager_auth" not in st.session_state:
        st.session_state.manager_auth = ManagerAuth(get_db())
    return st.session_state.manager_auth


def render_css():
    """Render Islamic CSS"""
    st.markdown(ISLAMIC_CSS, unsafe_allow_html=True)


def render_header():
    """Render Islamic application header"""
    user = get_manager_auth().get_current_user()
    user_name = user.get('full_name', 'User') if user else 'User'
    role = user.get('role', '') if user else ''

    st.markdown(f"""
    <div class="islamic-header" style="padding: 1.5rem;">
        <div class="islamic-header-content">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="text-align: left;">
                    <div class="bismillah" style="font-size: 1.2rem; margin-bottom: 0.3rem;">{ARABIC_TEXTS['bismillah']}</div>
                    <h2 style="margin: 0; font-size: 1.5rem;">Pengelola WBS BPKH</h2>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.95rem;">Dashboard Manajemen Whistleblowing</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; color: #F4E4BA;"><b>{user_name}</b></p>
                    <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">{USER_ROLES.get(role, {{}}).get('name', role)}</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_navigation():
    """Sidebar navigation"""
    with st.sidebar:
        # Back to home button
        if st.button("< Kembali ke Home", use_container_width=True):
            st.session_state.current_portal = 'home'
            st.session_state.manager_authenticated = False
            st.rerun()

        st.markdown("---")
        st.markdown("### Menu Pengelola")

        user = get_manager_auth().get_current_user()
        role = user.get('role', '') if user else ''

        # Build menu based on role
        menu_options = ["Dashboard"]

        if role in ['admin', 'manager', 'investigator']:
            menu_options.append("Laporan")
            menu_options.append("Pesan Masuk")

        if role in ['admin', 'manager']:
            menu_options.append("Investigator")

        if role == 'admin':
            menu_options.append("Manajemen User")

        menu_options.append("Pengaturan")

        page = st.radio(
            "Menu:",
            menu_options,
            label_visibility="collapsed"
        )

        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            get_manager_auth().logout()
            st.rerun()

        return page


def page_dashboard():
    """Dashboard page"""
    st.markdown('<h2 class="section-title">Dashboard</h2>', unsafe_allow_html=True)

    # Get statistics
    stats = get_db().get_statistics()

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Laporan", stats.get('total_reports', 0))
    with col2:
        st.metric("Critical", stats.get('critical_reports', 0),
                 delta="Urgent" if stats.get('critical_reports', 0) > 0 else None,
                 delta_color="inverse")
    with col3:
        st.metric("Avg Compliance", f"{stats.get('avg_compliance_score', 0):.1f}%")
    with col4:
        st.metric("7 Hari Terakhir", stats.get('reports_last_7_days', 0))

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Laporan per Severity")
        severity_data = {
            "Critical": stats.get('critical_reports', 0),
            "High": stats.get('high_reports', 0),
            "Medium": stats.get('medium_reports', 0),
            "Low": stats.get('low_reports', 0)
        }
        if sum(severity_data.values()) > 0:
            st.bar_chart(severity_data)
        else:
            st.info("Belum ada data")

    with col2:
        st.markdown("### Laporan per Unit")
        unit_data = stats.get('by_unit', {})
        if unit_data:
            st.bar_chart(unit_data)
        else:
            st.info("Belum ada data")

    # Recent reports
    st.markdown("### Laporan Terbaru")
    reports = get_manager_auth().get_accessible_reports()[:10]

    if reports:
        for report in reports:
            severity = report.get('severity', 'Low')
            with st.expander(f"{get_severity_icon(severity)} {report['report_id']} - {report['title'][:40]}..."):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Status:** {report.get('status', 'N/A')}")
                    st.markdown(f"**Severity:** {severity}")
                with col2:
                    st.markdown(f"**Unit:** {report.get('assigned_unit', 'N/A')}")
                    st.markdown(f"**Jenis:** {report.get('violation_type', 'N/A')}")
                with col3:
                    st.markdown(f"**Tanggal:** {format_datetime(report.get('created_at', ''))}")

                if st.button("Lihat Detail", key=f"view_{report['report_id']}"):
                    st.session_state.selected_report = report['report_id']
                    st.session_state.current_page = "Laporan"
                    st.rerun()
    else:
        st.info("Belum ada laporan")


def page_reports():
    """Reports management page"""
    st.markdown("## Manajemen Laporan")

    # Check if viewing specific report
    if 'selected_report' in st.session_state and st.session_state.selected_report:
        show_report_detail(st.session_state.selected_report)
        if st.button("Kembali ke Daftar"):
            st.session_state.selected_report = None
            st.rerun()
        return

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search = st.text_input("Cari", placeholder="Keyword...")
    with col2:
        severity_filter = st.selectbox("Severity", ["Semua", "Critical", "High", "Medium", "Low"])
    with col3:
        status_filter = st.selectbox("Status", ["Semua"] + REPORT_STATUSES)
    with col4:
        limit = st.number_input("Tampilkan", min_value=10, max_value=200, value=50)

    # Get reports based on filters
    if search:
        reports = get_db().search_reports(search)
    elif severity_filter != "Semua":
        reports = get_db().get_reports_by_severity(severity_filter)
    else:
        reports = get_manager_auth().get_accessible_reports()

    # Filter by status if needed
    if status_filter != "Semua":
        reports = [r for r in reports if r.get('status') == status_filter]

    reports = reports[:limit]

    st.markdown(f"**{len(reports)} laporan ditemukan**")

    # Display reports
    for report in reports:
        severity = report.get('severity', 'Low')
        severity_class = f"severity-{severity.lower()}"

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])

            with col1:
                st.markdown(f"**{report['report_id']}**")
                st.markdown(f"{report['title'][:30]}...")

            with col2:
                st.markdown(f"{report.get('violation_type', 'N/A')}")
                st.markdown(f"Unit: {report.get('assigned_unit', 'N/A')[:20]}")

            with col3:
                st.markdown(f"{get_severity_icon(severity)} {severity}")

            with col4:
                st.markdown(f"**{report.get('status', 'New')}**")

            with col5:
                if st.button("Detail", key=f"d_{report['report_id']}"):
                    st.session_state.selected_report = report['report_id']
                    st.rerun()

            st.markdown("---")


def show_report_detail(report_id: str):
    """Show detailed report view"""
    report = get_db().get_report(report_id)

    if not report:
        st.error("Laporan tidak ditemukan")
        return

    st.markdown(f"## Detail Laporan: {report_id}")

    # Status bar
    severity = report.get('severity', 'N/A')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Status", report.get('status', 'New'))
    with col2:
        st.markdown(f"**Severity**\n\n{get_severity_icon(severity)} {severity}")
    with col3:
        st.metric("Compliance", f"{report.get('compliance_score', 0):.0f}%")
    with col4:
        st.metric("Unit", report.get('assigned_unit', 'N/A')[:15])

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Informasi", "Investigasi", "Komunikasi", "Aksi"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Detail Laporan")
            st.markdown(f"**Judul:** {report.get('title', 'N/A')}")
            st.markdown(f"**Jenis Pelanggaran:** {report.get('violation_type', 'N/A')}")
            st.markdown(f"**Kode:** {report.get('violation_code', 'N/A')}")
            st.markdown(f"**Priority:** {report.get('priority', 'N/A')}")

        with col2:
            st.markdown("#### Timeline")
            st.markdown(f"**Tanggal Lapor:** {format_datetime(report.get('created_at', ''))}")
            st.markdown(f"**Update Terakhir:** {format_datetime(report.get('updated_at', ''))}")
            st.markdown(f"**Tanggal Kejadian:** {report.get('incident_date', 'N/A')}")
            st.markdown(f"**Lokasi:** {report.get('location', 'N/A')}")

        st.markdown("#### Deskripsi")
        st.text_area("", value=report.get('description', ''), height=150, disabled=True, label_visibility="collapsed")

        st.markdown("#### Bukti")
        st.text_area("", value=report.get('evidence', ''), height=100, disabled=True, label_visibility="collapsed")

    with tab2:
        st.markdown("#### Rencana Investigasi")

        # Get full result for investigation details
        full_result = json.loads(report.get('full_result', '{}'))
        investigation = full_result.get('investigation', {})

        st.markdown(f"**Plan:** {investigation.get('investigation_plan', 'N/A')}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Evidence Needed:**")
            for e in investigation.get('evidence_needed', []):
                st.markdown(f"- {e}")

        with col2:
            st.markdown("**Witnesses:**")
            for w in investigation.get('witnesses', []):
                st.markdown(f"- {w}")

        st.markdown("#### Catatan Manager")
        notes = st.text_area("Catatan", value=report.get('manager_notes', ''), height=100)
        if st.button("Simpan Catatan"):
            get_db().update_manager_notes(report_id, notes)
            st.success("Catatan disimpan!")

    with tab3:
        st.markdown("#### Komunikasi dengan Pelapor")

        # Mark as read
        get_db().mark_messages_read(report_id, 'manager')

        # Messages
        messages = get_db().get_messages(report_id)

        for msg in messages:
            if msg['sender_type'] == 'reporter':
                st.markdown(f"""
                <div class="message-reporter">
                    <small><b>Pelapor</b> - {msg['created_at']}</small><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            elif msg['sender_type'] == 'manager':
                st.markdown(f"""
                <div class="message-manager">
                    <small><b>{msg.get('sender_name', 'Manager')}</b> - {msg['created_at']}</small><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"[System] {msg['content']}")

        st.markdown("---")
        with st.form("send_message"):
            new_msg = st.text_area("Kirim Pesan ke Pelapor")
            if st.form_submit_button("Kirim"):
                if new_msg:
                    user = get_manager_auth().get_current_user()
                    get_db().add_message(
                        report_id, 'manager', new_msg,
                        sender_id=user.get('id')
                    )
                    st.success("Pesan terkirim!")
                    st.rerun()

    with tab4:
        st.markdown("#### Aksi")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Update Status**")
            new_status = st.selectbox("Status Baru", REPORT_STATUSES,
                                     index=REPORT_STATUSES.index(report.get('status', 'New'))
                                     if report.get('status') in REPORT_STATUSES else 0)
            if st.button("Update Status"):
                get_db().update_report_status(report_id, new_status)
                # Add system message
                get_db().add_message(
                    report_id, 'system',
                    f"Status diubah menjadi: {new_status}",
                    message_type='status_update'
                )
                st.success("Status diperbarui!")
                st.rerun()

        with col2:
            st.markdown("**Assign Investigator**")
            investigators = get_db().get_users(role='investigator')
            inv_options = {f"{i['full_name']} ({i['unit']})": i['id'] for i in investigators}

            if inv_options:
                selected_inv = st.selectbox("Pilih Investigator", list(inv_options.keys()))
                if st.button("Assign"):
                    get_db().assign_investigator(report_id, inv_options[selected_inv])
                    st.success("Investigator ditugaskan!")
            else:
                st.warning("Belum ada investigator terdaftar")


def page_investigators():
    """Investigator management page"""
    st.markdown("## Manajemen Investigator")

    investigators = get_db().get_users(role='investigator')

    if investigators:
        for inv in investigators:
            with st.expander(f"{inv['full_name']} - {inv['unit']}"):
                st.markdown(f"**Email:** {inv['email']}")
                st.markdown(f"**Status:** {'Aktif' if inv['is_active'] else 'Nonaktif'}")

                # Get assigned reports count
                reports = get_db().get_reports_by_investigator(inv['id'])
                st.metric("Laporan Ditangani", len(reports))
    else:
        st.info("Belum ada investigator terdaftar")


def page_users():
    """User management page (admin only)"""
    if not get_manager_auth().is_admin():
        st.error("Akses ditolak. Halaman ini hanya untuk Admin.")
        return

    st.markdown("## Manajemen User")

    tab1, tab2 = st.tabs(["Daftar User", "Tambah User"])

    with tab1:
        users = get_db().get_users()

        for user in users:
            with st.expander(f"{user['username']} - {user['full_name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Email:** {user['email']}")
                    st.markdown(f"**Role:** {USER_ROLES.get(user['role'], {}).get('name', user['role'])}")
                with col2:
                    st.markdown(f"**Unit:** {user['unit'] or 'N/A'}")
                    st.markdown(f"**Status:** {'Aktif' if user['is_active'] else 'Nonaktif'}")

                if user['username'] != 'admin':
                    if st.button(f"{'Nonaktifkan' if user['is_active'] else 'Aktifkan'}",
                               key=f"toggle_{user['id']}"):
                        get_db().update_user(user['id'], is_active=not user['is_active'])
                        st.rerun()

    with tab2:
        st.markdown("### Tambah User Baru")

        with st.form("add_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
                email = st.text_input("Email *")

            with col2:
                full_name = st.text_input("Nama Lengkap *")
                role = st.selectbox("Role *", list(USER_ROLES.keys()))
                unit = st.selectbox("Unit", list(ROUTING_UNITS.keys()))

            submit = st.form_submit_button("Tambah User", use_container_width=True)

        if submit:
            if all([username, password, email, full_name]):
                success = get_db().create_user(
                    username, password, email, full_name, role, unit
                )
                if success:
                    st.success("User berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Gagal menambahkan user. Username/email mungkin sudah terdaftar.")
            else:
                st.warning("Mohon lengkapi semua field wajib")


def page_inbox():
    """Inbox page - all incoming messages from reporters"""
    st.markdown("## Pesan Masuk")
    st.markdown("Pesan dari pelapor yang memerlukan tanggapan.")

    # Get all reports with unread messages
    reports = get_manager_auth().get_accessible_reports()

    # Collect all messages and group by report
    inbox_items = []
    for report in reports:
        report_id = report['report_id']
        messages = get_db().get_messages(report_id)

        # Filter to only reporter chat messages
        reporter_messages = [
            m for m in messages
            if m['sender_type'] == 'reporter' and m.get('message_type', 'chat') == 'chat'
        ]

        if reporter_messages:
            # Get the latest message
            latest_msg = reporter_messages[-1]
            unread_count = sum(1 for m in reporter_messages if not m.get('is_read', False))

            inbox_items.append({
                'report_id': report_id,
                'title': report.get('title', 'N/A'),
                'status': report.get('status', 'New'),
                'severity': report.get('severity', 'Low'),
                'latest_message': latest_msg['content'][:100] + '...' if len(latest_msg['content']) > 100 else latest_msg['content'],
                'latest_time': latest_msg['created_at'],
                'unread_count': unread_count,
                'total_messages': len(reporter_messages)
            })

    # Sort by unread first, then by time
    inbox_items.sort(key=lambda x: (-x['unread_count'], x['latest_time']), reverse=True)

    # Display count
    total_unread = sum(item['unread_count'] for item in inbox_items)
    if total_unread > 0:
        st.warning(f"Anda memiliki **{total_unread}** pesan belum dibaca dari **{len([i for i in inbox_items if i['unread_count'] > 0])}** laporan")

    st.markdown("---")

    if not inbox_items:
        st.info("Belum ada pesan dari pelapor.")
        return

    # Check if viewing specific conversation
    if 'inbox_selected_report' in st.session_state and st.session_state.inbox_selected_report:
        show_conversation(st.session_state.inbox_selected_report)
        if st.button("< Kembali ke Inbox"):
            st.session_state.inbox_selected_report = None
            st.rerun()
        return

    # Display inbox
    for item in inbox_items:
        severity = item['severity']

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                if item['unread_count'] > 0:
                    st.markdown(f"**{item['report_id']}** 🔴 {item['unread_count']} baru")
                else:
                    st.markdown(f"**{item['report_id']}**")
                st.markdown(f"*{item['latest_message']}*")

            with col2:
                st.markdown(f"Status: {item['status']}")
                st.markdown(f"{get_severity_icon(severity)} {severity}")

            with col3:
                st.markdown(f"{item['total_messages']} pesan")
                st.markdown(f"{format_datetime(item['latest_time'])[:10]}")

            with col4:
                if st.button("Balas", key=f"inbox_{item['report_id']}"):
                    st.session_state.inbox_selected_report = item['report_id']
                    st.rerun()

            st.markdown("---")


def show_conversation(report_id: str):
    """Show conversation with reporter"""
    report = get_db().get_report(report_id)

    if not report:
        st.error("Laporan tidak ditemukan")
        return

    st.markdown(f"### Percakapan: {report_id}")

    # Show report summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Status:** {report.get('status', 'New')}")
    with col2:
        severity = report.get('severity', 'Low')
        st.markdown(f"**Severity:** {get_severity_icon(severity)} {severity}")
    with col3:
        st.markdown(f"**Judul:** {report.get('title', 'N/A')[:30]}...")

    st.markdown("---")

    # Mark messages as read
    get_db().mark_messages_read(report_id, 'manager')

    # Get messages - filter to chat only
    messages = get_db().get_messages(report_id)
    chat_messages = [m for m in messages if m.get('message_type', 'chat') == 'chat']

    # Display messages
    st.markdown("#### Riwayat Percakapan")

    msg_container = st.container()
    with msg_container:
        if chat_messages:
            for msg in chat_messages:
                if msg['sender_type'] == 'reporter':
                    st.markdown(f"""
                    <div class="message-reporter">
                        <small style="color: #666;"><b>Pelapor</b> - {format_datetime(msg['created_at'])}</small><br>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg['sender_type'] == 'manager':
                    sender_name = msg.get('sender_name', 'Tim Pengelola')
                    st.markdown(f"""
                    <div class="message-manager">
                        <small style="color: #666;"><b>{sender_name}</b> - {format_datetime(msg['created_at'])}</small><br>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Belum ada percakapan.")

    # Reply form
    st.markdown("---")
    st.markdown("#### Balas Pesan")

    with st.form("reply_form", clear_on_submit=True):
        reply_msg = st.text_area(
            "Pesan balasan",
            placeholder="Ketik balasan untuk pelapor...",
            height=100,
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([3, 1])
        with col2:
            submit = st.form_submit_button("Kirim Balasan", use_container_width=True, type="primary")

    if submit and reply_msg.strip():
        user = get_manager_auth().get_current_user()
        get_db().add_message(
            report_id, 'manager', reply_msg.strip(),
            sender_id=user.get('id'),
            message_type='chat'
        )
        st.success("Balasan terkirim!")
        st.rerun()
    elif submit and not reply_msg.strip():
        st.warning("Pesan tidak boleh kosong.")

    # Quick actions
    st.markdown("---")
    st.markdown("#### Aksi Cepat")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lihat Detail Laporan", use_container_width=True):
            st.session_state.selected_report = report_id
            st.session_state.inbox_selected_report = None
            st.session_state.current_page = "Laporan"
            st.rerun()


def page_settings():
    """Settings page"""
    st.markdown("## Pengaturan")

    user = get_manager_auth().get_current_user()

    st.markdown("### Profil Saya")
    st.markdown(f"**Username:** {user.get('username', 'N/A')}")
    st.markdown(f"**Nama:** {user.get('full_name', 'N/A')}")
    st.markdown(f"**Email:** {user.get('email', 'N/A')}")
    st.markdown(f"**Role:** {USER_ROLES.get(user.get('role', ''), {}).get('name', user.get('role', 'N/A'))}")
    st.markdown(f"**Unit:** {user.get('unit', 'N/A')}")

    st.markdown("---")

    st.markdown("### API Configuration")
    api_key = st.text_input("Groq API Key",
                           value=st.session_state.get("groq_api_key", ""),
                           type="password")
    if st.button("Simpan API Key"):
        st.session_state.groq_api_key = api_key
        st.success("API Key disimpan!")

    st.markdown("---")

    st.markdown("### Tentang Sistem")
    st.markdown(f"**Versi:** {config.version}")
    st.markdown("**Developer:** Audit Committee BPKH")


def main():
    """Main application"""
    # Initialize
    init_session_state()
    render_css()

    # Check authentication
    if not get_manager_auth().is_authenticated():
        st.markdown(f"""
        <div class="islamic-header">
            <div class="islamic-header-content">
                <div class="bismillah">{ARABIC_TEXTS['bismillah']}</div>
                <div class="gold-line"></div>
                <h1 class="header-title">Pengelola WBS BPKH</h1>
                <p class="header-subtitle">{ARABIC_TEXTS['assalamualaikum']}</p>
                <p style="margin-top: 1rem; opacity: 0.9;">Silakan login untuk mengakses dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="max-width: 400px; margin: 0 auto;">', unsafe_allow_html=True)
        render_login_form(get_manager_auth())
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(render_islamic_footer(), unsafe_allow_html=True)
        return

    render_header()

    # Navigation
    page = sidebar_navigation()

    # Route pages
    if page == "Dashboard":
        page_dashboard()
    elif page == "Laporan":
        page_reports()
    elif page == "Pesan Masuk":
        page_inbox()
    elif page == "Investigator":
        page_investigators()
    elif page == "Manajemen User":
        page_users()
    elif page == "Pengaturan":
        page_settings()

    # Islamic Footer
    st.markdown(render_islamic_footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
