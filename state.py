"""Session-state keys and shared resources.

All cross-page state lives here so pages and components never invent keys.
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from services import RecommendationService, build_recommendation_service

# Session-state keys -------------------------------------------------------
IMAGE = "fv_image"                  # CurrentImage | None
RESULT = "fv_result"                # AnalysisResult | None
INPUT_NONCE = "fv_input_nonce"      # int - bump to reset uploader / camera
INPUT_ERROR = "fv_input_error"      # str | None
GALLERY_REF = "fv_gallery_ref"      # "analysis" | product id | None
GALLERY_CATEGORY = "fv_gallery_category"
GALLERY_SEARCH = "fv_gallery_search"
GALLERY_SORT = "fv_gallery_sort"

ALL_CATEGORIES = "All"
PERSISTENT_WIDGET_KEYS = (GALLERY_CATEGORY, GALLERY_SEARCH, GALLERY_SORT)


@dataclass(frozen=True)
class CurrentImage:
    data: bytes
    name: str
    source: str            # "Upload" | "Webcam" | "Sample"
    token: str             # identity of the widget value that produced it

    @property
    def size_bytes(self) -> int:
        return len(self.data)


def init_state() -> None:
    defaults = {
        IMAGE: None,
        RESULT: None,
        INPUT_NONCE: 0,
        INPUT_ERROR: None,
        GALLERY_REF: None,
        GALLERY_CATEGORY: ALL_CATEGORIES,
        GALLERY_SEARCH: "",
        GALLERY_SORT: "Similarity: high to low",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    # Streamlit drops a widget's keyed value when the widget is not rendered on
    # the current page. Re-assigning keeps gallery filters across navigation.
    for key in PERSISTENT_WIDGET_KEYS:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]


def set_image(data: bytes, name: str, source: str, token: str) -> None:
    current: CurrentImage | None = st.session_state.get(IMAGE)
    if current is not None and current.token == token:
        return
    st.session_state[IMAGE] = CurrentImage(data, name, source, token)
    st.session_state[RESULT] = None
    st.session_state[INPUT_ERROR] = None


def clear_image() -> None:
    st.session_state[IMAGE] = None
    st.session_state[RESULT] = None
    st.session_state[INPUT_ERROR] = None
    st.session_state[INPUT_NONCE] = st.session_state.get(INPUT_NONCE, 0) + 1
    if st.session_state.get(GALLERY_REF) == "analysis":
        st.session_state[GALLERY_REF] = None


@st.cache_resource(show_spinner=False)
def get_service() -> RecommendationService:
    """One service instance per server process (models would load once here)."""
    return build_recommendation_service()
