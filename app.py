"""Streamlit entry point for Social Media Sage Analysis System."""

import streamlit as st

from modules.database_manager import initialize_database
from modules.data_service import get_display_posts
from modules.ui import apply_app_style, show_data_mode

st.set_page_config(
    page_title="Social Media Sage",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_app_style()
initialize_database()
_, using_demo = get_display_posts(st.session_state)
show_data_mode(using_demo)

pages = [
    st.Page("pages/1_Dashboard.py", title="Dashboard", icon="📊", default=True),
    st.Page("pages/2_Text_Analysis.py", title="Single Text Analysis", icon="✍️"),
    st.Page("pages/3_Dataset_Analysis.py", title="Dataset Analysis", icon="📁"),
    st.Page("pages/4_Trending_Topics.py", title="Trending Topics", icon="🔎"),
    st.Page("pages/5_Analysis_History.py", title="Analysis History", icon="🕘"),
    st.Page("pages/6_About_Project.py", title="About Project", icon="ℹ️"),
]
navigation = st.navigation(pages, position="sidebar")
navigation.run()
