"""
Home Page Portal
Landing page with portal selection
"""

import streamlit as st
from ..ui.styles import ISLAMIC_CSS, ARABIC_TEXTS, render_islamic_footer
from ..config import get_settings


def render_home_page():
    """Render the home/landing page"""

    settings = get_settings()

    # Apply CSS
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
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # 5W+1H Section
    _render_5w_section()

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Privacy Section
    _render_privacy_section()

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Portal Selection
    _render_portal_selection()

    st.markdown('<div class="gold-line" style="width: 100%; margin: 2rem 0;"></div>', unsafe_allow_html=True)

    # Features Section
    _render_features_section()

    # Contact Section
    contact = settings.contact.to_dict()
    st.markdown(f"""
    <div class="contact-section" style="margin-top: 2rem;">
        <h3 style="margin-top: 0; color: #F4E4BA; position: relative;">Butuh Bantuan?</h3>
        <p style="position: relative; line-height: 2;">
            <strong>Email:</strong> {contact['Email']}<br>
            <strong>WhatsApp:</strong> {contact['WhatsApp']}<br>
            <strong>Portal:</strong> {contact['Web Portal']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(render_islamic_footer(), unsafe_allow_html=True)


def _render_5w_section():
    """Render 5W+1H section"""
    st.markdown('<h3 class="section-title">Unsur Pengaduan (5W + 1H)</h3>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-section" style="text-align: center; margin-bottom: 1.5rem;">
        <p style="margin: 0; font-size: 1.05rem; color: #2C3E50;">
            <strong>Pengaduan Anda akan mudah ditindaklanjuti apabila memenuhi unsur sebagai berikut:</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    elements_5w = [
        ("What", "Apa", "Perbuatan berindikasi pelanggaran yang diketahui", "❓"),
        ("Where", "Dimana", "Lokasi perbuatan tersebut dilakukan", "📍"),
        ("When", "Kapan", "Waktu perbuatan tersebut dilakukan", "🕐"),
        ("Who", "Siapa", "Pihak yang terlibat dalam perbuatan tersebut", "👤"),
        ("How", "Bagaimana", "Modus dan cara perbuatan dilakukan", "🔍"),
    ]

    cols = st.columns(5)
    for col, (en, id_, desc, icon) in zip(cols, elements_5w):
        with col:
            st.markdown(f"""
            <div class="element-5w">
                <span class="element-5w-icon">{icon}</span>
                <div class="element-5w-title">{en}</div>
                <div class="element-5w-subtitle">{id_}</div>
                <div class="element-5w-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_privacy_section():
    """Render privacy/confidentiality section"""
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
            <li>Jika ingin identitas Anda tetap rahasia, <strong>jangan memberitahukan/mengisikan data-data pribadi</strong></li>
            <li>Jangan memberitahukan data/informasi yang memungkinkan pelacakan identitas Anda</li>
            <li><strong>Hindari orang lain mengetahui</strong> username, password serta nomor registrasi Anda</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def _render_portal_selection():
    """Render portal selection cards"""
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
                    <li>Submit laporan baru</li>
                    <li>Lacak status laporan</li>
                    <li>Komunikasi anonim dengan pengelola</li>
                    <li>AI Chatbot bantuan</li>
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
                    <li>Dashboard & Analytics</li>
                    <li>Manajemen laporan</li>
                    <li>Assign investigator</li>
                    <li>Komunikasi dengan pelapor</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔐 Masuk Portal Pengelola", use_container_width=True):
            st.session_state.current_portal = 'manager'
            st.rerun()


def _render_features_section():
    """Render system features section"""
    st.markdown('<h3 class="section-title">Keunggulan Sistem</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    features = [
        ("🔒", "Keamanan Terjamin", [
            "Identitas pelapor dilindungi",
            "Data terenkripsi",
            "Sesuai PP 71/2000",
            "Akses terkontrol"
        ]),
        ("🤖", "AI-Powered", [
            "Processing < 5 detik",
            "Klasifikasi otomatis",
            "Compliance 93%+",
            "6 AI Agents"
        ]),
        ("📱", "Multi-Channel", [
            "Web Portal",
            "WhatsApp Integration",
            "AI Chatbot",
            "Email Notification"
        ])
    ]

    for col, (icon, title, items) in zip([col1, col2, col3], features):
        with col:
            items_html = "\n".join([f"<li>{item}</li>" for item in items])
            st.markdown(f"""
            <div class="islamic-card" style="text-align: center; height: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <h4 style="color: #1B5E20; margin: 0.5rem 0;">{title}</h4>
                <ul style="text-align: left; color: #5D6D7E; padding-left: 1.5rem; line-height: 1.8;">
                    {items_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
