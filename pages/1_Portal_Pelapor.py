"""
WBS BPKH - Portal Pelapor
Redirect to main app
"""

import streamlit as st

st.set_page_config(
    page_title="WBS BPKH - Portal Pelapor",
    page_icon="🛡️",
    layout="wide"
)

st.warning("Silakan akses melalui halaman utama")
st.markdown("[Kembali ke Halaman Utama](./)")

if st.button("Buka Halaman Utama"):
    st.markdown('<meta http-equiv="refresh" content="0;url=./">', unsafe_allow_html=True)
