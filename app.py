"""FashionVision AI - Streamlit entry point.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

import state
from components.layout import footer, load_css
from components.sidebar import render_sidebar_brand, render_sidebar_footer
from config import APP_NAME, MARK_PATH

st.set_page_config(
    page_title=APP_NAME,
    page_icon=str(MARK_PATH),
    layout="wide",
    initial_sidebar_state="auto",  # expanded on desktop, collapsed on phones
)

load_css()
state.init_state()
render_sidebar_brand()

page = st.navigation(
    [
        st.Page("app_pages/fashion_analysis.py", title="Fashion Analysis",
                icon=":material/center_focus_strong:", default=True),
        st.Page("app_pages/recommendation_gallery.py", title="Recommendation Gallery",
                icon=":material/grid_view:"),
        st.Page("app_pages/categories.py", title="Categories",
                icon=":material/category:"),
        st.Page("app_pages/model_information.py", title="Model Information",
                icon=":material/schema:"),
        st.Page("app_pages/about.py", title="About Project",
                icon=":material/info:"),
    ],
    position="sidebar",
)

render_sidebar_footer()
page.run()
footer()
