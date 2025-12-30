"""
WBS BPKH - AI-Powered Whistleblowing System
Main Entry Point - Router to Reporter/Manager Interfaces
Badan Pengelola Keuangan Haji (BPKH)

Modular Architecture v2.0
"""

import sys
from pathlib import Path

# Add src to Python path for modular imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

# Modular imports from src
from src.ui import ISLAMIC_CSS, ARABIC_TEXTS, render_islamic_footer
from src.config import AppConfig

# Page configuration
st.set_page_config(
    page_title="WBS BPKH - Whistleblowing System",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if 'current_portal' not in st.session_state:
    st.session_state.current_portal = 'home'

config = AppConfig()


def show_home():
    """Show home/portal selection page with Islamic theme"""

    # Apply Islamic CSS
    st.markdown(ISLAMIC_CSS, unsafe_allow_html=True)

    # Islamic Header
    st.markdown(f"""
    <div class="islamic-header">
        <div class="islamic-header-content">
            <div class="bismillah">{ARABIC_TEXTS['bismillah']}</div>
            <div class="gold-line"></div>
            <h1 class="header-title">Whistleblowing System</h1>
            <p class="header-subtitle">{ARABIC_TEXTS['assalamualaikum']}</p>
            <p class="header-org">Badan Pengelola Keuangan Haji (BPKH)</p>
            <p style="margin-top: 1rem; opacity: 0.9; font-size: 1rem;">
                Menjaga Amanah Dana Haji dengan Integritas dan Kejujuran
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Kaaba decoration
    st.markdown('<div class="kaaba-decoration">🕋</div>', unsafe_allow_html=True)

    # Video and Welcome Section
    col_video, col_welcome = st.columns([1, 1])

    with col_video:
        st.markdown('<h3 class="section-title">Video Panduan</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="video-container">
            <iframe src="https://www.youtube.com/embed/wAeGnDx5Ex8"
                    title="WBS BPKH Video"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)

    with col_welcome:
        st.markdown('<h3 class="section-title">Tentang WBS BPKH</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="islamic-card">
            <p style="font-size: 1.05rem; line-height: 1.8; color: #2C3E50;">
                <strong>Whistleblowing System</strong> adalah aplikasi yang disediakan oleh
                <strong style="color: #1B5E20;">BPKH</strong> bagi Anda yang memiliki informasi dan ingin
                melaporkan suatu perbuatan berindikasi pelanggaran yang terjadi di lingkungan
                <strong>Badan Pengelola Keuangan Haji Republik Indonesia</strong>.
            </p>
            <div class="gold-line"></div>
            <p style="font-size: 1.05rem; line-height: 1.8; color: #2C3E50;">
                Anda tidak perlu khawatir terungkapnya identitas diri Anda karena BPKH akan
                <strong style="color: #D4AF37;">MERAHASIAKAN IDENTITAS DIRI ANDA</strong> sebagai whistleblower.
            </p>
            <p style="font-size: 1rem; color: #5D6D7E; margin-top: 1rem; font-style: italic;">
                "BPKH menghargai informasi yang Anda laporkan. Fokus kami kepada materi informasi yang Anda Laporkan."
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Unsur Pengaduan Section (5W)
    st.markdown('<h3 class="section-title">Unsur Pengaduan (5W + 1H)</h3>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-section" style="text-align: center; margin-bottom: 1.5rem;">
        <p style="margin: 0; font-size: 1.05rem; color: #2C3E50;">
            <strong>Pengaduan Anda akan mudah ditindaklanjuti apabila memenuhi unsur sebagai berikut:</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    elements_5w = [
        ("What", "Apa", "Perbuatan berindikasi pelanggaran yang diketahui", "❓"),
        ("Where", "Dimana", "Lokasi perbuatan tersebut dilakukan", "📍"),
        ("When", "Kapan", "Waktu perbuatan tersebut dilakukan", "🕐"),
        ("Who", "Siapa", "Pihak yang terlibat dalam perbuatan tersebut", "👤"),
        ("How", "Bagaimana", "Modus dan cara perbuatan dilakukan", "🔍"),
    ]

    for col, (en, id_, desc, icon) in zip([col1, col2, col3, col4, col5], elements_5w):
        with col:
            st.markdown(f"""
            <div class="element-5w">
                <span class="element-5w-icon">{icon}</span>
                <div class="element-5w-title">{en}</div>
                <div class="element-5w-subtitle">{id_}</div>
                <div class="element-5w-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Kerahasiaan Section
    st.markdown('<h3 class="section-title">Kerahasiaan Pelapor</h3>', unsafe_allow_html=True)

    st.markdown("""
    <div class="privacy-section">
        <h4 style="color: #1B5E20; margin-top: 0.5rem;">
            BPKH akan <span style="color: #D4AF37;">merahasiakan identitas pribadi Anda</span> sebagai whistleblower
        </h4>
        <p style="color: #2C3E50; margin: 1rem 0;">
            Karena BPKH hanya fokus pada informasi yang Anda laporkan.
            <strong>Agar kerahasiaan lebih terjaga, perhatikan hal-hal berikut:</strong>
        </p>
        <ul style="color: #2C3E50; line-height: 2;">
            <li>Jika ingin identitas Anda tetap rahasia, <strong>jangan memberitahukan/mengisikan data-data pribadi</strong>, seperti nama Anda, atau hubungan Anda dengan pelaku-pelaku.</li>
            <li>Jangan memberitahukan/mengisikan data-data/informasi yang memungkinkan bagi orang lain untuk melakukan pelacakan siapa Anda.</li>
            <li><strong>Hindari orang lain mengetahui</strong> nama samaran (username), kata sandi (password) serta nomor registrasi Anda.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Portal Selection
    st.markdown('<h3 class="section-title">Pilih Portal</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="portal-card">
            <span class="portal-icon">📝</span>
            <div class="portal-title">Portal Pelapor</div>
            <div class="portal-desc">
                Laporkan pelanggaran dengan aman dan terjamin kerahasiaannya
            </div>
            <div class="feature-box">
                <ul>
                    <li>✅ Submit laporan baru</li>
                    <li>✅ Lacak status laporan</li>
                    <li>✅ Komunikasi anonim dengan pengelola</li>
                    <li>✅ AI Chatbot bantuan</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🕌 Masuk Portal Pelapor", use_container_width=True, type="primary"):
            st.session_state.current_portal = 'reporter'
            st.rerun()

    with col2:
        st.markdown("""
        <div class="portal-card">
            <span class="portal-icon">🛡️</span>
            <div class="portal-title">Portal Pengelola</div>
            <div class="portal-desc">
                Dashboard manajemen untuk tim pengelola WBS BPKH
            </div>
            <div class="feature-box">
                <ul>
                    <li>✅ Dashboard & Analytics</li>
                    <li>✅ Manajemen laporan</li>
                    <li>✅ Assign investigator</li>
                    <li>✅ Komunikasi dengan pelapor</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔐 Masuk Portal Pengelola", use_container_width=True):
            st.session_state.current_portal = 'manager'
            st.rerun()

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Features Section
    st.markdown('<h3 class="section-title">Keunggulan Sistem</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="islamic-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔒</div>
            <h4 style="color: #1B5E20; margin: 0.5rem 0;">Keamanan Terjamin</h4>
            <ul style="text-align: left; color: #5D6D7E; padding-left: 1.5rem; line-height: 1.8;">
                <li>Identitas pelapor dilindungi</li>
                <li>Data terenkripsi</li>
                <li>Sesuai PP 71/2000</li>
                <li>Akses terkontrol</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="islamic-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
            <h4 style="color: #1B5E20; margin: 0.5rem 0;">AI-Powered</h4>
            <ul style="text-align: left; color: #5D6D7E; padding-left: 1.5rem; line-height: 1.8;">
                <li>Processing < 5 detik</li>
                <li>Klasifikasi otomatis</li>
                <li>Compliance 93%+</li>
                <li>6 AI Agents</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="islamic-card" style="text-align: center; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📱</div>
            <h4 style="color: #1B5E20; margin: 0.5rem 0;">Multi-Channel</h4>
            <ul style="text-align: left; color: #5D6D7E; padding-left: 1.5rem; line-height: 1.8;">
                <li>Web Portal</li>
                <li>WhatsApp Integration</li>
                <li>AI Chatbot</li>
                <li>Email Notification</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Contact Section
    st.markdown(f"""
    <div class="contact-section" style="margin-top: 2rem;">
        <h3 style="margin-top: 0; color: #F4E4BA; position: relative;">Butuh Bantuan?</h3>
        <p style="position: relative; line-height: 2;">
            <strong>Email:</strong> {config.contact_info['Email']}<br>
            <strong>WhatsApp:</strong> {config.contact_info['WhatsApp']}<br>
            <strong>Portal:</strong> {config.contact_info['Web Portal']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Islamic Footer
    st.markdown(render_islamic_footer(), unsafe_allow_html=True)


def main():
    """Main entry point with navigation"""

    # Check current portal
    portal = st.session_state.current_portal

    if portal == 'home':
        show_home()
    elif portal == 'reporter':
        # Import and run reporter portal from modular src
        from src.portals import render_reporter_portal
        render_reporter_portal()
    elif portal == 'manager':
        # Import and run manager portal from modular src
        from src.portals import render_manager_portal
        render_manager_portal()
    else:
        show_home()


if __name__ == "__main__":
    main()
