"""Dark sidebar: wordmark (via st.logo) and project status footer.

Navigation links themselves are rendered by ``st.navigation`` in app.py.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from config import APP_VERSION, BACKEND_MODE, LOGO_PATH, MARK_PATH, PROJECT_STATUS


def render_sidebar_brand() -> None:
    st.logo(str(LOGO_PATH), size="large", icon_image=str(MARK_PATH))


def render_sidebar_footer() -> None:
    backend = "Mock services" if BACKEND_MODE == "mock" else "API"
    rows = [
        ("Project status", f'<span class="fv-dot"></span>{escape(PROJECT_STATUS)}'),
        ("Version", escape(APP_VERSION)),
        ("Backend", escape(backend)),
    ]
    body = "".join(
        f'<div class="fv-sidebar-foot__row"><span class="fv-sidebar-foot__label">{label}</span>'
        f'<span class="fv-sidebar-foot__value">{value}</span></div>'
        for label, value in rows
    )
    st.sidebar.html(f'<div class="fv-sidebar-foot">{body}</div>')
