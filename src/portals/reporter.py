"""
Reporter Portal
Interface for whistleblowers to submit and track reports
"""

import streamlit as st
from datetime import datetime

from ..ui.styles import ISLAMIC_CSS, ARABIC_TEXTS, render_islamic_header, render_islamic_footer
from ..services import AuthService, ReportService
from ..models import ReportCreate
from ..agents import AgentPipeline
from ..config import get_settings


def render_reporter_portal():
    """Main entry point for reporter portal"""

    # Apply CSS
    st.markdown(ISLAMIC_CSS, unsafe_allow_html=True)

    # Initialize services
    auth_service = AuthService()
    report_service = ReportService()

    # Sidebar navigation
    _render_sidebar()

    # Get current page
    page = st.session_state.get('reporter_page', 'submit')

    # Render selected page
    if page == 'submit':
        _render_submit_page(report_service)
    elif page == 'track':
        _render_track_page(report_service, auth_service)
    elif page == 'chat':
        _render_chat_page(report_service)
    elif page == 'chatbot':
        _render_chatbot_page()


def _render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2rem;">📝</div>
            <h2 style="color: #F4E4BA; margin: 0.5rem 0;">Portal Pelapor</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        pages = {
            'submit': '📋 Buat Laporan',
            'track': '🔍 Lacak Laporan',
            'chat': '💬 Pesan Anonim',
            'chatbot': '🤖 AI Chatbot'
        }

        current_page = st.session_state.get('reporter_page', 'submit')

        for key, label in pages.items():
            if st.button(label, use_container_width=True,
                        type="primary" if key == current_page else "secondary"):
                st.session_state.reporter_page = key
                st.rerun()

        st.markdown("---")

        # Back to home
        if st.button("🏠 Kembali ke Home", use_container_width=True):
            st.session_state.current_portal = 'home'
            st.rerun()


def _render_submit_page(report_service: ReportService):
    """Render report submission page"""

    st.markdown(render_islamic_header("Buat Laporan Baru", "Sampaikan Laporan Anda dengan Aman"), unsafe_allow_html=True)

    # Check if we have a successful submission
    if st.session_state.get('submit_success'):
        result = st.session_state.submit_success

        st.markdown(f"""
        <div class="success-box">
            <h3 style="margin-top: 0;">✅ Laporan Berhasil Disubmit!</h3>
        </div>
        <div class="credential-box">
            <h4 style="margin-top: 1rem;">Kredensial Akses Anda</h4>
            <p><strong>Report ID:</strong></p>
            <h2 style="color: #1B5E20; margin: 0.5rem 0;">{result['report_id']}</h2>
            <p><strong>PIN:</strong></p>
            <h2 style="color: #D4AF37; margin: 0.5rem 0;">{result['pin']}</h2>
            <p style="color: #856404; font-size: 0.9rem; margin-top: 1rem;">
                ⚠️ <strong>PENTING:</strong> Simpan Report ID dan PIN Anda dengan aman.<br>
                Informasi ini diperlukan untuk melacak status laporan.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Buat Laporan Baru", use_container_width=True):
            del st.session_state.submit_success
            st.rerun()

        return

    # Report form
    st.markdown('<h3 class="section-title">Formulir Laporan (5W + 1H)</h3>', unsafe_allow_html=True)

    with st.form("report_form"):
        # What
        st.markdown("**❓ What (Apa yang terjadi?)**")
        what = st.text_area(
            "Jelaskan kejadian yang ingin dilaporkan",
            height=120,
            placeholder="Deskripsikan secara detail apa yang terjadi...",
            key="what"
        )

        col1, col2 = st.columns(2)

        with col1:
            # Where
            st.markdown("**📍 Where (Dimana?)**")
            where = st.text_input(
                "Lokasi kejadian",
                placeholder="Contoh: Kantor Pusat BPKH, Jakarta",
                key="where"
            )

            # When
            st.markdown("**🕐 When (Kapan?)**")
            when = st.text_input(
                "Waktu kejadian",
                placeholder="Contoh: Januari 2025 atau 15 Januari 2025",
                key="when"
            )

        with col2:
            # Who
            st.markdown("**👤 Who (Siapa yang terlibat?)**")
            who = st.text_input(
                "Pihak yang terlibat",
                placeholder="Jabatan/posisi pihak yang terlibat",
                key="who"
            )

            # Evidence
            st.markdown("**📎 Bukti Pendukung (opsional)**")
            evidence = st.text_input(
                "Deskripsi bukti",
                placeholder="Jelaskan bukti yang Anda miliki",
                key="evidence"
            )

        # How
        st.markdown("**🔍 How (Bagaimana kronologinya?)**")
        how = st.text_area(
            "Kronologi kejadian",
            height=100,
            placeholder="Jelaskan bagaimana kejadian tersebut dilakukan...",
            key="how"
        )

        st.markdown("---")

        submitted = st.form_submit_button("📤 Submit Laporan", use_container_width=True, type="primary")

        if submitted:
            # Validate
            report_data = ReportCreate(
                what=what,
                where=where,
                when=when,
                who=who,
                how=how,
                evidence_description=evidence,
                source_channel='web'
            )

            errors = report_data.validate()
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Submit report
                with st.spinner("Memproses laporan..."):
                    result = report_service.submit_report(report_data)

                    if result.success:
                        # Process with AI pipeline
                        pipeline = AgentPipeline()
                        pipeline.process_report({
                            'what': what,
                            'where': where,
                            'when': when,
                            'who': who,
                            'how': how
                        })

                        st.session_state.submit_success = {
                            'report_id': result.report_id,
                            'pin': result.pin
                        }
                        st.rerun()
                    else:
                        st.error(f"Gagal submit: {result.error}")

    st.markdown(render_islamic_footer(), unsafe_allow_html=True)


def _render_track_page(report_service: ReportService, auth_service: AuthService):
    """Render report tracking page"""

    st.markdown(render_islamic_header("Lacak Laporan", "Cek Status Laporan Anda"), unsafe_allow_html=True)

    # Check if already authenticated
    if st.session_state.get('tracked_report'):
        report = st.session_state.tracked_report
        _display_report_status(report, report_service)
        return

    # Login form
    st.markdown('<div class="islamic-card">', unsafe_allow_html=True)

    with st.form("track_form"):
        st.markdown("### 🔐 Masukkan Kredensial")

        report_id = st.text_input(
            "Report ID",
            placeholder="Contoh: WBS-2025-000001"
        )

        pin = st.text_input(
            "PIN",
            type="password",
            placeholder="6 digit PIN"
        )

        submitted = st.form_submit_button("🔍 Cek Status", use_container_width=True, type="primary")

        if submitted:
            if not report_id or not pin:
                st.error("Report ID dan PIN harus diisi")
            else:
                success, error = auth_service.verify_reporter_access(report_id.upper(), pin)

                if success:
                    report = report_service.get_report(report_id.upper())
                    if report:
                        st.session_state.tracked_report = report
                        st.rerun()
                    else:
                        st.error("Laporan tidak ditemukan")
                else:
                    st.error(error)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(render_islamic_footer(), unsafe_allow_html=True)


def _display_report_status(report, report_service):
    """Display report status details"""
    from ..config import ReportStatus, SeverityLevel

    # Status badge color
    status_colors = {
        'submitted': '#3498DB',
        'under_review': '#F39C12',
        'investigation': '#2E7D32',
        'resolved': '#27AE60',
        'closed': '#5D6D7E',
        'rejected': '#E74C3C'
    }

    status_color = status_colors.get(report.status, '#5D6D7E')
    status_name = ReportStatus.get_display_name(report.status)

    st.markdown(f"""
    <div class="islamic-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #1B5E20;">{report.report_id}</h3>
            <span style="background: {status_color}20; color: {status_color};
                   padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600;">
                {status_name}
            </span>
        </div>
        <div class="gold-line" style="margin: 1rem 0;"></div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <p style="color: #5D6D7E; margin: 0;">📁 Kategori</p>
                <p style="font-weight: 600; margin: 0.25rem 0;">{report.category or 'Dalam proses'}</p>
            </div>
            <div>
                <p style="color: #5D6D7E; margin: 0;">⚡ Prioritas</p>
                <p style="font-weight: 600; margin: 0.25rem 0;">{report.severity or 'Dalam proses'}</p>
            </div>
            <div>
                <p style="color: #5D6D7E; margin: 0;">📅 Tanggal Lapor</p>
                <p style="font-weight: 600; margin: 0.25rem 0;">{report.created_at.strftime('%d %b %Y') if report.created_at else 'N/A'}</p>
            </div>
            <div>
                <p style="color: #5D6D7E; margin: 0;">📊 Hari Berjalan</p>
                <p style="font-weight: 600; margin: 0.25rem 0;">{report.days_open} hari</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Summary
    if report.summary:
        st.markdown(f"""
        <div class="islamic-card" style="margin-top: 1rem;">
            <h4 style="color: #1B5E20; margin-top: 0;">📋 Ringkasan</h4>
            <p>{report.summary}</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Buka Pesan", use_container_width=True):
            st.session_state.reporter_page = 'chat'
            st.session_state.chat_report_id = report.report_id
            st.rerun()

    with col2:
        if st.button("🔙 Kembali", use_container_width=True):
            del st.session_state.tracked_report
            st.rerun()


def _render_chat_page(report_service: ReportService):
    """Render anonymous chat page"""

    st.markdown(render_islamic_header("Pesan Anonim", "Komunikasi dengan Pengelola WBS"), unsafe_allow_html=True)

    # Check if we have a report ID
    report_id = st.session_state.get('chat_report_id')

    if not report_id:
        # Login with report ID only (anonymous)
        st.markdown('<div class="islamic-card">', unsafe_allow_html=True)

        with st.form("chat_login"):
            st.markdown("### 🔐 Masukkan Report ID")
            report_id_input = st.text_input(
                "Report ID",
                placeholder="Contoh: WBS-2025-000001"
            )

            submitted = st.form_submit_button("💬 Buka Chat", use_container_width=True, type="primary")

            if submitted and report_id_input:
                report = report_service.get_report(report_id_input.upper())
                if report:
                    st.session_state.chat_report_id = report.report_id
                    st.rerun()
                else:
                    st.error("Report ID tidak ditemukan")

        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Load messages
    messages = report_service.get_messages(report_id)

    # Display messages
    st.markdown(f"### 💬 Chat - {report_id}")

    message_container = st.container()
    with message_container:
        for msg in messages:
            if msg.sender_type == 'reporter':
                st.markdown(f"""
                <div class="message-reporter">
                    <small>Anda • {msg.created_at.strftime('%H:%M') if msg.created_at else ''}</small>
                    <p style="margin: 0.25rem 0 0 0;">{msg.content}</p>
                </div>
                """, unsafe_allow_html=True)
            elif msg.sender_type == 'manager':
                st.markdown(f"""
                <div class="message-manager">
                    <small>Pengelola • {msg.created_at.strftime('%H:%M') if msg.created_at else ''}</small>
                    <p style="margin: 0.25rem 0 0 0;">{msg.content}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-system">
                    {msg.content}
                </div>
                """, unsafe_allow_html=True)

    # Send message form
    with st.form("send_message", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            new_message = st.text_input("Ketik pesan...", key="new_msg", label_visibility="collapsed")
        with col2:
            send = st.form_submit_button("📤", use_container_width=True)

        if send and new_message:
            success, error = report_service.send_message(report_id, new_message, 'reporter')
            if success:
                st.rerun()
            else:
                st.error(error)

    # Exit button
    if st.button("🔙 Keluar Chat", use_container_width=True):
        del st.session_state.chat_report_id
        st.rerun()


def _render_chatbot_page():
    """Render AI chatbot page"""
    from ..agents import ChatbotAgent

    st.markdown(render_islamic_header("AI Chatbot", "Asisten Virtual WBS BPKH"), unsafe_allow_html=True)

    chatbot = ChatbotAgent()

    # Initialize chat history
    if 'chatbot_messages' not in st.session_state:
        st.session_state.chatbot_messages = []

        # Add welcome message
        welcome = chatbot.process({'message': 'halo', 'session_id': 'streamlit'})
        st.session_state.chatbot_messages.append({
            'role': 'assistant',
            'content': welcome.data.get('response', 'Selamat datang!')
        })

    # Display chat history
    for msg in st.session_state.chatbot_messages:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="message-reporter">
                <p style="margin: 0;">{msg['content']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-manager">
                <p style="margin: 0;">{msg['content']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Input
    with st.form("chatbot_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Ketik pesan...", key="chatbot_input", label_visibility="collapsed")
        with col2:
            send = st.form_submit_button("📤")

        if send and user_input:
            # Add user message
            st.session_state.chatbot_messages.append({
                'role': 'user',
                'content': user_input
            })

            # Get response
            result = chatbot.process({
                'message': user_input,
                'session_id': 'streamlit'
            })

            # Add bot response
            st.session_state.chatbot_messages.append({
                'role': 'assistant',
                'content': result.data.get('response', 'Maaf, saya tidak mengerti.')
            })

            st.rerun()

    # Clear button
    if st.button("🗑️ Hapus Riwayat", use_container_width=True):
        st.session_state.chatbot_messages = []
        chatbot.reset_session('streamlit')
        st.rerun()
