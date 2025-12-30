"""
WBS BPKH - AI-Powered Whistleblowing System
Main Application Entry Point
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config import get_settings
from portals import render_home_page, render_reporter_portal, render_manager_portal


def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="WBS BPKH - Whistleblowing System",
        page_icon="🕌",
        layout="wide",
        initial_sidebar_state="collapsed"
    )


def initialize_state():
    """Initialize session state"""
    if 'current_portal' not in st.session_state:
        st.session_state.current_portal = 'home'


def main():
    """Main application entry point"""

    configure_page()
    initialize_state()

    # Route to appropriate portal
    portal = st.session_state.current_portal

    if portal == 'home':
        render_home_page()
    elif portal == 'reporter':
        render_reporter_portal()
    elif portal == 'manager':
        render_manager_portal()
    else:
        st.session_state.current_portal = 'home'
        render_home_page()


if __name__ == "__main__":
    main()
