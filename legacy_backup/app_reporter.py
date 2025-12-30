"""
WBS BPKH - Reporter Interface (Pelapor)
Portal untuk submit laporan dan tracking status
"""

import streamlit as st
import json
import time
from datetime import datetime

from config import AppConfig, VIOLATION_TYPES
from db_factory import get_database
from agents import OrchestratorAgent
from auth import ReporterAuth, init_session_state
from utils import format_datetime, get_severity_icon, generate_report_summary
from styles import ISLAMIC_CSS, ARABIC_TEXTS, render_islamic_footer

# Initialize config
config = AppConfig()


def get_db():
    """Get or create database connection"""
    if "db" not in st.session_state:
        st.session_state.db = get_database()
    return st.session_state.db


def get_reporter_auth():
    """Get or create reporter auth"""
    if "reporter_auth" not in st.session_state:
        st.session_state.reporter_auth = ReporterAuth(get_db())
    return st.session_state.reporter_auth


def render_css():
    """Render Islamic CSS"""
    st.markdown(ISLAMIC_CSS, unsafe_allow_html=True)


def render_header():
    """Render Islamic application header"""
    st.markdown(f"""
    <div class="islamic-header">
        <div class="islamic-header-content">
            <div class="bismillah" style="font-size: 1.5rem;">{ARABIC_TEXTS['bismillah']}</div>
            <h1 class="header-title" style="font-size: 1.8rem;">Portal Pelapor WBS</h1>
            <p class="header-subtitle">Laporkan pelanggaran dengan aman dan terjamin kerahasiaannya</p>
            <p class="header-org">Badan Pengelola Keuangan Haji (BPKH)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_navigation():
    """Sidebar navigation"""
    with st.sidebar:
        # Back to home button
        if st.button("< Kembali ke Home", use_container_width=True):
            st.session_state.current_portal = 'home'
            st.rerun()

        st.markdown("---")
        st.markdown("### Menu Pelapor")

        # Check if user has active session (full access with PIN)
        if st.session_state.get('reporter_authenticated'):
            report_id = st.session_state.get('reporter_report_id')
            st.success(f"Akses: {report_id}")
            if st.button("Keluar", use_container_width=True):
                st.session_state.reporter_authenticated = False
                st.session_state.reporter_report_id = None
                st.session_state.chat_authenticated = False
                st.session_state.chat_report_id = None
                st.rerun()
            st.markdown("---")

        # Check if user has chat-only session
        if st.session_state.get('chat_authenticated') and not st.session_state.get('reporter_authenticated'):
            chat_id = st.session_state.get('chat_report_id')
            st.info(f"Chat: {chat_id}")
            if st.button("Keluar Chat", use_container_width=True):
                st.session_state.chat_authenticated = False
                st.session_state.chat_report_id = None
                st.rerun()
            st.markdown("---")

        page = st.radio(
            "Pilih Menu:",
            ["Buat Laporan Baru", "Lacak Status Laporan", "Komunikasi Anonim", "Bantuan & FAQ"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Kontak")
        st.markdown(f"**Email:** {config.contact_info['Email']}")
        st.markdown(f"**WhatsApp:** {config.contact_info['WhatsApp']}")

        st.markdown("---")
        st.markdown("### Jaminan Keamanan")
        st.markdown("""
        - Identitas pelapor dilindungi
        - Data dienkripsi
        - Sesuai PP 71/2000
        """)

        return page


def page_submit_report():
    """Page for submitting new report"""
    st.markdown('<h2 class="section-title">Buat Laporan Baru</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #5D6D7E; margin-bottom: 1.5rem;">
        Isi formulir berikut untuk melaporkan pelanggaran. Semua field bertanda * wajib diisi.
    </p>
    """, unsafe_allow_html=True)

    # Info boxes with Islamic styling
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="islamic-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔒</div>
            <b style="color: #1B5E20;">Kerahasiaan Terjamin</b><br>
            <small style="color: #5D6D7E;">Identitas Anda dilindungi UU</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="islamic-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <b style="color: #1B5E20;">Proses Cepat</b><br>
            <small style="color: #5D6D7E;">AI processing < 5 detik</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="islamic-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <b style="color: #1B5E20;">Tracking Real-time</b><br>
            <small style="color: #5D6D7E;">Pantau progress laporan</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Report form
    with st.form("report_form"):
        st.markdown("### Informasi Laporan (4W+1H)")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Judul Laporan (What) *",
                placeholder="Contoh: Dugaan penyalahgunaan anggaran..."
            )

            description = st.text_area(
                "Deskripsi Detail (What) *",
                placeholder="Jelaskan kronologi kejadian secara detail...",
                height=150
            )

            reported_person = st.text_input(
                "Nama Terlapor (Who) *",
                placeholder="Nama lengkap atau jabatan"
            )

        with col2:
            incident_date = st.date_input(
                "Tanggal Kejadian (When) *"
            )

            location = st.text_input(
                "Lokasi Kejadian (Where) *",
                placeholder="Contoh: Kantor Pusat BPKH, Lantai 5"
            )

            evidence = st.text_area(
                "Bukti/Evidence (How) *",
                placeholder="Jelaskan bukti yang ada: dokumen, saksi, dll...",
                height=150
            )

        st.markdown("### Data Kontak (Opsional)")
        st.markdown("*Data ini hanya untuk notifikasi dan tidak akan dipublikasikan*")

        col3, col4 = st.columns(2)
        with col3:
            reporter_email = st.text_input(
                "Email",
                placeholder="Untuk menerima notifikasi (opsional)"
            )
        with col4:
            reporter_phone = st.text_input(
                "No. WhatsApp",
                placeholder="Untuk menerima notifikasi via WA (opsional)"
            )

        submit_button = st.form_submit_button(
            "Kirim Laporan",
            use_container_width=True,
            type="primary"
        )

    if submit_button:
        # Validate required fields
        if not all([title, description, reported_person, location, evidence]):
            st.error("Mohon lengkapi semua field yang bertanda *")
        else:
            with st.spinner("Memproses laporan dengan AI..."):
                # Generate Report ID
                report_id = get_db().generate_report_id()

                report_data = {
                    "title": title,
                    "description": description,
                    "reported_person": reported_person,
                    "incident_date": str(incident_date),
                    "location": location,
                    "evidence": evidence,
                    "reporter_name": "Anonim",
                    "reporter_contact": reporter_email or reporter_phone or "N/A"
                }

                # Initialize orchestrator
                api_key = st.session_state.get("groq_api_key", config.groq_api_key)
                orchestrator = OrchestratorAgent(api_key)

                # Process report
                start_time = time.time()
                result = orchestrator.process_report(report_data)
                processing_time = time.time() - start_time

                # Override report_id with our generated one
                result["report_id"] = report_id

                # Save to database
                success = get_db().insert_report(report_data, result)

                if success:
                    # Generate PIN
                    pin = get_db().create_report_access(
                        report_id,
                        email=reporter_email,
                        phone=reporter_phone
                    )

                    # Create initial conversation
                    get_db().create_conversation(report_id, 'web')

                    # Add system message
                    get_db().add_message(
                        report_id, 'system',
                        f"Laporan diterima dan sedang diproses. Klasifikasi: {result['classification']['violation_type']}, Severity: {result['classification']['severity']}",
                        message_type='status_update'
                    )

                    # Success display
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>Laporan Berhasil Dikirim!</h3>
                        <p>Laporan Anda telah diterima dan diproses dalam {processing_time:.2f} detik.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="credential-box">
                        <h3>SIMPAN KREDENSIAL INI</h3>
                        <p style="font-size: 1.5em; font-weight: bold;">Report ID: {report_id}</p>
                        <p style="font-size: 1.5em; font-weight: bold;">PIN: {pin}</p>
                        <p>Gunakan Report ID dan PIN untuk melacak status laporan Anda.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show summary
                    with st.expander("Lihat Ringkasan Laporan"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Jenis Pelanggaran", result['classification']['violation_type'])
                        with col2:
                            severity = result['classification']['severity']
                            st.metric("Severity", f"{get_severity_icon(severity)} {severity}")
                        with col3:
                            st.metric("Unit Penanganan", result['routing']['assigned_unit'])

                        st.markdown(f"**SLA:** {result['routing']['sla_hours']} jam")
                        st.markdown(f"**Compliance Score:** {result['compliance']['compliance_score']:.1f}%")

                else:
                    st.error("Gagal menyimpan laporan. Silakan coba lagi.")


def page_track_status():
    """Page for tracking report status"""
    st.markdown("## Lacak Status Laporan")

    # Check if already authenticated
    if st.session_state.get('reporter_authenticated'):
        report_id = st.session_state.reporter_report_id
        show_report_details(report_id)
    else:
        st.markdown("Masukkan Report ID dan PIN untuk melihat status laporan Anda.")

        with st.form("track_form"):
            col1, col2 = st.columns(2)
            with col1:
                report_id = st.text_input("Report ID", placeholder="WBS-2025-000001")
            with col2:
                pin = st.text_input("PIN", type="password", max_chars=6, placeholder="6 digit PIN")

            submit = st.form_submit_button("Cek Status", use_container_width=True, type="primary")

        if submit:
            if report_id and pin:
                if get_reporter_auth().validate_access(report_id, pin):
                    st.session_state.reporter_authenticated = True
                    st.session_state.reporter_report_id = report_id
                    st.rerun()
                else:
                    st.error("Report ID atau PIN tidak valid!")
            else:
                st.warning("Mohon masukkan Report ID dan PIN.")


def show_report_details(report_id: str):
    """Show report details and messaging"""
    report = get_db().get_report(report_id)

    if not report:
        st.error("Laporan tidak ditemukan.")
        return

    # Status Overview
    st.markdown(f"### Laporan: {report_id}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Status", report.get('status', 'New'))
    with col2:
        severity = report.get('severity', 'N/A')
        st.markdown(f"**Severity**\n\n{get_severity_icon(severity)} {severity}")
    with col3:
        st.metric("Unit", report.get('assigned_unit', 'N/A')[:15] + "...")
    with col4:
        st.metric("Compliance", f"{report.get('compliance_score', 0):.0f}%")

    st.markdown("---")

    # Tabs for details and messages
    tab1, tab2 = st.tabs(["Detail Laporan", "Komunikasi"])

    with tab1:
        st.markdown("#### Informasi Laporan")
        st.markdown(f"**Judul:** {report.get('title', 'N/A')}")
        st.markdown(f"**Jenis Pelanggaran:** {report.get('violation_type', 'N/A')}")
        st.markdown(f"**Tanggal Lapor:** {format_datetime(report.get('created_at', ''))}")
        st.markdown(f"**Terakhir Update:** {format_datetime(report.get('updated_at', ''))}")

        with st.expander("Lihat Detail Lengkap"):
            st.markdown(f"**Deskripsi:** {report.get('description', 'N/A')}")
            st.markdown(f"**Lokasi:** {report.get('location', 'N/A')}")
            st.markdown(f"**Tanggal Kejadian:** {report.get('incident_date', 'N/A')}")

    with tab2:
        st.markdown("#### Pesan")
        st.markdown("Berkomunikasi dengan tim pengelola WBS.")

        # Mark messages as read
        get_db().mark_messages_read(report_id, 'reporter')

        # Show messages
        messages = get_db().get_messages(report_id)

        message_container = st.container()
        with message_container:
            if messages:
                for msg in messages:
                    if msg['sender_type'] == 'reporter':
                        st.markdown(f"""
                        <div class="message-reporter">
                            <small>{msg['created_at']}</small><br>
                            {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        sender = msg.get('sender_name', 'Tim WBS')
                        st.markdown(f"""
                        <div class="message-manager">
                            <small><b>{sender}</b> - {msg['created_at']}</small><br>
                            {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Belum ada pesan.")

        # Send message form
        st.markdown("---")
        with st.form("message_form"):
            new_message = st.text_area("Tulis pesan", placeholder="Ketik pesan Anda...")
            send = st.form_submit_button("Kirim", use_container_width=True)

        if send and new_message:
            get_db().add_message(report_id, 'reporter', new_message)
            st.success("Pesan terkirim!")
            st.rerun()


def page_anonymous_chat():
    """Anonymous chat page - login with Report ID only"""
    st.markdown("## Komunikasi Anonim")

    st.markdown("""
    <div class="info-card">
        <b>Komunikasi Aman</b><br>
        Berkomunikasi dengan tim pengelola WBS tanpa mengungkap identitas.
        Login hanya dengan Report ID, tanpa PIN.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Check if already authenticated for chat
    if st.session_state.get('chat_authenticated') or st.session_state.get('reporter_authenticated'):
        # Use chat_report_id or reporter_report_id
        report_id = st.session_state.get('chat_report_id') or st.session_state.get('reporter_report_id')
        show_anonymous_chat(report_id)
    else:
        st.markdown("### Login Chat")
        st.markdown("Masukkan Report ID untuk memulai komunikasi anonim dengan tim pengelola.")

        with st.form("chat_login_form"):
            report_id = st.text_input(
                "Report ID",
                placeholder="WBS-2025-000001",
                help="Report ID yang Anda terima saat membuat laporan"
            )

            submit = st.form_submit_button("Masuk Chat", use_container_width=True, type="primary")

        if submit:
            if report_id:
                # Validate report exists
                report = get_db().get_report(report_id)
                if report:
                    st.session_state.chat_authenticated = True
                    st.session_state.chat_report_id = report_id
                    st.rerun()
                else:
                    st.error("Report ID tidak ditemukan. Pastikan Report ID yang Anda masukkan benar.")
            else:
                st.warning("Mohon masukkan Report ID.")

        st.markdown("---")
        st.markdown("""
        **Catatan Keamanan:**
        - Identitas Anda tetap terlindungi
        - Hanya tim pengelola WBS yang dapat membaca pesan
        - Komunikasi ini tidak memerlukan PIN untuk menjaga anonimitas
        """)


def show_anonymous_chat(report_id: str):
    """Show anonymous chat interface"""
    report = get_db().get_report(report_id)

    if not report:
        st.error("Laporan tidak ditemukan.")
        return

    # Chat header
    st.markdown(f"### Chat: {report_id}")

    # Show minimal report info (no sensitive details)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Status:** {report.get('status', 'New')}")
    with col2:
        st.markdown(f"**Terakhir Update:** {format_datetime(report.get('updated_at', ''))}")

    st.markdown("---")

    # Mark messages as read for reporter
    get_db().mark_messages_read(report_id, 'reporter')

    # Chat messages container
    messages = get_db().get_messages(report_id)

    # Filter to only show chat messages (not system messages)
    chat_messages = [m for m in messages if m.get('message_type', 'chat') == 'chat']

    st.markdown("#### Percakapan")

    chat_container = st.container()
    with chat_container:
        if chat_messages:
            for msg in chat_messages:
                if msg['sender_type'] == 'reporter':
                    st.markdown(f"""
                    <div class="message-reporter">
                        <small style="color: #666;">{format_datetime(msg['created_at'])}</small><br>
                        <span style="color: #1565c0;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    sender = "Tim Pengelola WBS"
                    st.markdown(f"""
                    <div class="message-manager">
                        <small style="color: #666;"><b>{sender}</b> - {format_datetime(msg['created_at'])}</small><br>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Belum ada percakapan. Mulai dengan mengirim pesan di bawah.")

    # Send message form
    st.markdown("---")
    st.markdown("#### Kirim Pesan")

    with st.form("anonymous_chat_form", clear_on_submit=True):
        new_message = st.text_area(
            "Pesan Anda",
            placeholder="Ketik pesan untuk tim pengelola WBS...",
            height=100,
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([3, 1])
        with col2:
            send = st.form_submit_button("Kirim", use_container_width=True, type="primary")

    if send and new_message.strip():
        # Add message as reporter
        get_db().add_message(report_id, 'reporter', new_message.strip(), message_type='chat')
        st.success("Pesan terkirim!")
        time.sleep(0.5)
        st.rerun()
    elif send and not new_message.strip():
        st.warning("Pesan tidak boleh kosong.")


def page_help():
    """Help and FAQ page"""
    st.markdown("## Bantuan & FAQ")

    st.markdown("### Apa itu Whistleblowing?")
    st.markdown("""
    Whistleblowing adalah pengungkapan pelanggaran atau tindakan tidak etis yang dilakukan
    oleh pegawai atau pihak lain dalam organisasi kepada pihak yang berwenang.
    """)

    st.markdown("### Jenis Pelanggaran yang Dapat Dilaporkan")
    for vtype, vdata in VIOLATION_TYPES.items():
        with st.expander(f"{vdata['code']} - {vtype}"):
            st.markdown(f"**Dasar Hukum:** {vdata['legal_basis']}")
            st.markdown(f"**Severity:** {vdata['severity']}")

    st.markdown("### FAQ")

    with st.expander("Apakah identitas saya akan dilindungi?"):
        st.markdown("""
        Ya, identitas pelapor dilindungi sesuai PP 71/2000. Data Anda dienkripsi dan hanya
        dapat diakses oleh tim investigasi yang berwenang.
        """)

    with st.expander("Bagaimana cara melacak status laporan?"):
        st.markdown("""
        Setelah melapor, Anda akan menerima Report ID dan PIN. Gunakan kredensial ini
        di menu "Lacak Status Laporan" untuk melihat progress.
        """)

    with st.expander("Berapa lama proses investigasi?"):
        st.markdown("""
        Waktu proses tergantung severity:
        - Critical: SLA 4 jam
        - High: SLA 24 jam
        - Medium: SLA 48 jam
        - Low: SLA 72 jam
        """)

    with st.expander("Bagaimana jika saya lupa PIN?"):
        st.markdown("""
        Hubungi tim WBS melalui email atau WhatsApp untuk reset kredensial.
        Anda perlu memverifikasi identitas terlebih dahulu.
        """)

    st.markdown("### Kontak Bantuan")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Email:** {config.contact_info['Email']}")
        st.markdown(f"**WhatsApp:** {config.contact_info['WhatsApp']}")
    with col2:
        st.markdown(f"**Portal:** {config.contact_info['Web Portal']}")
        st.markdown(f"**IT Support:** {config.contact_info['Support']}")


def main():
    """Main application"""
    # Initialize
    init_session_state()
    render_css()

    render_header()

    # Navigation
    page = sidebar_navigation()

    # Route pages
    if "Buat Laporan" in page:
        page_submit_report()
    elif "Lacak Status" in page:
        page_track_status()
    elif "Komunikasi Anonim" in page:
        page_anonymous_chat()
    elif "Bantuan" in page:
        page_help()

    # Islamic Footer
    st.markdown(render_islamic_footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
