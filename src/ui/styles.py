"""
Islamic Theme Styles for WBS BPKH
Beautiful, professional Islamic UI/UX design with macOS aesthetics
"""

# Islamic Color Palette
COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#2E7D32',
    'light_green': '#4CAF50',
    'gold': '#D4AF37',
    'gold_light': '#F4E4BA',
    'cream': '#FFF8E7',
    'white': '#FFFFFF',
    'dark': '#1A1A2E',
    'text_primary': '#2C3E50',
    'text_secondary': '#5D6D7E',
    'success': '#27AE60',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'info': '#3498DB',
}

# Arabic texts
ARABIC_TEXTS = {
    'bismillah': 'بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ',
    'assalamualaikum': 'السَّلاَمُ عَلَيْكُمْ وَرَحْمَةُ اللهِ وَبَرَكَاتُهُ',
    'jazakallah': 'جَزَاكَ اللَّهُ خَيْرًا',
    'barakallah': 'بَارَكَ اللَّهُ فِيكُمْ',
    'alhamdulillah': 'اَلْحَمْدُ لِلَّهِ',
    'insyaallah': 'إِنْ شَاءَ اللَّهُ',
    'amanah': 'أَمَانَة',
}

# Main CSS for Islamic Theme with macOS Aesthetics
ISLAMIC_CSS = """
<style>
    /* Import Google Fonts - SF Pro like */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Amiri:wght@400;700&display=swap');

    /* Root Variables */
    :root {
        --primary-green: #1B5E20;
        --secondary-green: #2E7D32;
        --light-green: #4CAF50;
        --gold: #D4AF37;
        --gold-light: #F4E4BA;
        --cream: #FFF8E7;
        --dark: #1A1A2E;
        --glass-bg: rgba(255, 255, 255, 0.72);
        --glass-border: rgba(255, 255, 255, 0.18);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
    }

    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 50%, #fff8e1 100%);
    }

    /* ==================== macOS Glassmorphism Sidebar ==================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            rgba(27, 94, 32, 0.95) 0%,
            rgba(46, 125, 50, 0.92) 50%,
            rgba(27, 94, 32, 0.95) 100%) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0 L60 30 L30 60 L0 30 Z' fill='none' stroke='rgba(255,255,255,0.05)' stroke-width='1'/%3E%3C/svg%3E");
        pointer-events: none;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem !important;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.95) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h3 {
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: rgba(244, 228, 186, 0.9) !important;
        margin-bottom: 0.75rem !important;
    }

    /* Sidebar Radio Buttons - macOS Style */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        margin: 2px 0 !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(4px) !important;
    }

    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(212, 175, 55, 0.25) !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        color: #F4E4BA !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
        margin: 1rem 0 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(212, 175, 55, 0.5) !important;
    }

    /* ==================== Islamic Header ==================== */
    .islamic-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #1B5E20 100%);
        padding: 2.5rem 2rem;
        border-radius: 0 0 32px 32px;
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
        margin: -1rem -1rem 2rem -1rem;
    }

    .islamic-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M40 0 L80 40 L40 80 L0 40 Z' fill='none' stroke='rgba(255,255,255,0.08)' stroke-width='1'/%3E%3Ccircle cx='40' cy='40' r='20' fill='none' stroke='rgba(255,255,255,0.05)' stroke-width='1'/%3E%3C/svg%3E");
        opacity: 0.6;
    }

    .islamic-header-content {
        position: relative;
        z-index: 1;
    }

    .bismillah {
        font-family: 'Amiri', serif !important;
        font-size: 1.8rem;
        color: #F4E4BA;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .header-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        letter-spacing: -0.02em;
    }

    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 400;
    }

    .header-org {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-top: 0.5rem;
        color: #F4E4BA;
        font-weight: 500;
    }

    /* Gold Line */
    .gold-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, #D4AF37, transparent);
        margin: 1.5rem auto;
        width: 150px;
    }

    /* ==================== macOS Style 5W Cards ==================== */
    .element-5w {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        padding: 1.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        box-shadow:
            0 4px 24px rgba(0, 0, 0, 0.06),
            0 1px 2px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.6);
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .element-5w::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1B5E20, #D4AF37);
        border-radius: 20px 20px 0 0;
    }

    .element-5w:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 20px 40px rgba(27, 94, 32, 0.15),
            0 8px 16px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border-color: rgba(212, 175, 55, 0.4);
    }

    .element-5w-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        display: block;
    }

    .element-5w-title {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        font-size: 1.5rem;
        color: #1B5E20;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .element-5w-subtitle {
        font-weight: 600;
        font-size: 0.85rem;
        color: #D4AF37;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .element-5w-desc {
        color: #5D6D7E;
        font-size: 0.875rem;
        line-height: 1.5;
        font-weight: 400;
    }

    /* ==================== macOS Glass Cards ==================== */
    .islamic-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 20px;
        padding: 1.75rem;
        box-shadow:
            0 4px 24px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .islamic-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1B5E20, #D4AF37, #1B5E20);
    }

    .islamic-card:hover {
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }

    /* ==================== Portal Cards ==================== */
    .portal-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.7);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .portal-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1B5E20, #D4AF37, #1B5E20);
    }

    .portal-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow:
            0 24px 48px rgba(27, 94, 32, 0.2),
            0 12px 24px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 1);
        border-color: rgba(212, 175, 55, 0.5);
    }

    .portal-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }

    .portal-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.35rem;
        font-weight: 700;
        color: #1B5E20;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .portal-desc {
        color: #5D6D7E;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .feature-box {
        background: linear-gradient(135deg, rgba(248, 253, 248, 0.8) 0%, rgba(255, 248, 231, 0.8) 100%);
        padding: 1rem;
        border-radius: 14px;
        margin-top: 1rem;
        border-left: 3px solid #D4AF37;
    }

    .feature-box ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .feature-box li {
        padding: 0.4rem 0;
        color: #2C3E50;
        font-size: 0.875rem;
        font-weight: 500;
    }

    /* ==================== Section Title ==================== */
    .section-title {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        font-size: 1.5rem;
        color: #1B5E20;
        text-align: center;
        margin: 2.5rem 0 1.5rem 0;
        position: relative;
        padding-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }

    .section-title::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #1B5E20, #D4AF37);
        border-radius: 2px;
    }

    /* ==================== Info & Privacy Sections ==================== */
    .info-section {
        background: rgba(255, 248, 231, 0.85);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        position: relative;
    }

    .info-section::before {
        content: '✦';
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 0 12px;
        color: #D4AF37;
        font-size: 1rem;
        border-radius: 10px;
        box-shadow: var(--shadow-sm);
    }

    .privacy-section {
        background: linear-gradient(135deg, rgba(232, 245, 233, 0.9) 0%, rgba(241, 248, 233, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 1.75rem;
        border-radius: 20px;
        border-left: 4px solid #1B5E20;
        position: relative;
    }

    .privacy-section::before {
        content: '🔒';
        position: absolute;
        top: -14px;
        left: 24px;
        background: white;
        padding: 6px 10px;
        border-radius: 12px;
        font-size: 1.25rem;
        box-shadow: var(--shadow-md);
    }

    /* ==================== macOS Buttons ==================== */
    .stButton > button {
        background: linear-gradient(180deg, #2E7D32 0%, #1B5E20 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow:
            0 2px 8px rgba(27, 94, 32, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow:
            0 6px 20px rgba(27, 94, 32, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow:
            0 2px 4px rgba(27, 94, 32, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #E5C158 0%, #D4AF37 100%) !important;
        color: #1A1A2E !important;
        box-shadow:
            0 2px 8px rgba(212, 175, 55, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    }

    /* ==================== Input Fields - macOS Style ==================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1.5px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1B5E20 !important;
        box-shadow:
            0 0 0 4px rgba(27, 94, 32, 0.1),
            inset 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        outline: none !important;
    }

    .stSelectbox > div > div {
        border-radius: 12px !important;
    }

    /* ==================== Messages - macOS Style ==================== */
    .message-reporter {
        background: linear-gradient(135deg, rgba(227, 242, 253, 0.9) 0%, rgba(232, 245, 233, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 6px 18px;
        margin: 0.75rem 0;
        border: 1px solid rgba(27, 94, 32, 0.1);
        box-shadow: var(--shadow-sm);
    }

    .message-manager {
        background: linear-gradient(135deg, rgba(255, 248, 231, 0.9) 0%, rgba(245, 245, 245, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 6px;
        margin: 0.75rem 0;
        text-align: right;
        border: 1px solid rgba(212, 175, 55, 0.15);
        box-shadow: var(--shadow-sm);
    }

    .message-system {
        background: rgba(248, 249, 250, 0.8);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        font-size: 0.85rem;
        color: #5D6D7E;
        border: 1px dashed rgba(212, 175, 55, 0.3);
    }

    /* ==================== Tabs - macOS Style ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(0, 0, 0, 0.04);
        padding: 4px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 0, 0, 0.04) !important;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #1B5E20 !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ==================== Success & Credential Boxes ==================== */
    .success-box {
        background: linear-gradient(135deg, rgba(212, 237, 218, 0.95) 0%, rgba(195, 230, 203, 0.95) 100%);
        backdrop-filter: blur(10px);
        border: none;
        border-left: 4px solid #28a745;
        color: #155724;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }

    .credential-box {
        background: linear-gradient(135deg, rgba(255, 248, 231, 0.95) 0%, rgba(255, 238, 186, 0.95) 100%);
        backdrop-filter: blur(10px);
        border: 2px solid #D4AF37;
        color: #856404;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        text-align: center;
        position: relative;
        box-shadow: var(--shadow-lg);
    }

    .credential-box::before {
        content: '🔐';
        position: absolute;
        top: -16px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 1.5rem;
        box-shadow: var(--shadow-md);
    }

    /* ==================== Contact Section ==================== */
    .contact-section {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
    }

    .contact-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0 L60 30 L30 60 L0 30 Z' fill='none' stroke='rgba(255,255,255,0.08)' stroke-width='1'/%3E%3C/svg%3E");
        opacity: 0.5;
    }

    .contact-section h3 {
        position: relative;
        color: #F4E4BA;
        font-weight: 600;
    }

    .contact-section p {
        position: relative;
    }

    /* ==================== Video Container ==================== */
    .video-container {
        position: relative;
        padding-bottom: 56.25%;
        height: 0;
        overflow: hidden;
        border-radius: 20px;
        box-shadow: var(--shadow-xl);
        border: 3px solid rgba(212, 175, 55, 0.5);
    }

    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    /* ==================== Footer ==================== */
    .islamic-footer {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        color: white;
        padding: 1.75rem;
        border-radius: 20px 20px 0 0;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.1);
    }

    .islamic-footer p {
        margin: 0.3rem 0;
        opacity: 0.9;
    }

    .dua-text {
        font-family: 'Amiri', serif !important;
        font-size: 1.15rem;
        color: #F4E4BA;
        margin-bottom: 0.75rem;
    }

    /* ==================== Kaaba Decoration ==================== */
    .kaaba-decoration {
        text-align: center;
        font-size: 2.5rem;
        margin: 0.75rem 0;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }

    /* ==================== Metric Cards ==================== */
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 1.25rem;
        border-radius: 16px;
        border-left: 4px solid #1B5E20;
        box-shadow: var(--shadow-md);
    }

    /* ==================== Severity Colors ==================== */
    .severity-critical {
        border-left-color: #dc3545 !important;
        background: linear-gradient(135deg, rgba(255, 245, 245, 0.9) 0%, white 100%) !important;
    }

    .severity-high {
        border-left-color: #fd7e14 !important;
        background: linear-gradient(135deg, rgba(255, 248, 240, 0.9) 0%, white 100%) !important;
    }

    .severity-medium {
        border-left-color: #ffc107 !important;
        background: linear-gradient(135deg, rgba(255, 253, 240, 0.9) 0%, white 100%) !important;
    }

    .severity-low {
        border-left-color: #28a745 !important;
        background: linear-gradient(135deg, rgba(240, 255, 244, 0.9) 0%, white 100%) !important;
    }

    /* ==================== Expander ==================== */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border-left: 3px solid #D4AF37 !important;
    }
</style>
"""

# Helper function to render Islamic header
def render_islamic_header(title: str, subtitle: str = "", org: str = "Badan Pengelola Keuangan Haji"):
    return f"""
    <div class="islamic-header">
        <div class="islamic-header-content">
            <div class="bismillah">{ARABIC_TEXTS['bismillah']}</div>
            <h1 class="header-title">{title}</h1>
            <p class="header-subtitle">{subtitle}</p>
            <p class="header-org">{org}</p>
        </div>
    </div>
    """

# Helper function to render Islamic footer
def render_islamic_footer():
    return f"""
    <div class="islamic-footer">
        <p class="dua-text">{ARABIC_TEXTS['barakallah']}</p>
        <p>&copy; 2025 Badan Pengelola Keuangan Haji (BPKH)</p>
        <p style="font-size: 0.85rem; opacity: 0.8;">Menjaga Amanah Dana Haji dengan Integritas</p>
    </div>
    """

# Helper function to render section title
def render_section_title(title: str):
    return f'<h3 class="section-title">{title}</h3>'

# Helper function to render gold line
def render_gold_line():
    return '<div class="gold-line"></div>'
