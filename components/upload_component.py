"""Image input (upload / webcam / sample library) and the preview panel."""

from __future__ import annotations

from html import escape

import streamlit as st

import state
from components.layout import card_heading
from config import ALLOWED_IMAGE_TYPES, MAX_UPLOAD_MB
from data.mock_products import SAMPLE_PRODUCT_IDS, get_product
from services import InvalidImageError, load_image

INPUT_MODES = ("Upload", "Webcam", "Sample library")


def _use_sample(product_id: str) -> None:
    product = get_product(product_id)
    state.set_image(product.image_path.read_bytes(), f"{product.id}.jpg", "Sample", f"sample:{product.id}")


def render_image_input() -> None:
    """Left panel: choose an image source and provide an image."""
    card_heading("Image source", "Upload a product photo, capture one with your webcam, or try a sample.")
    nonce = st.session_state[state.INPUT_NONCE]
    mode = st.segmented_control(
        "Image source", INPUT_MODES, default=INPUT_MODES[0], required=True,
        key="fv_input_mode", label_visibility="collapsed",
    )

    if mode == "Upload":
        uploaded = st.file_uploader(
            "Product image",
            type=list(ALLOWED_IMAGE_TYPES),
            key=f"fv_uploader_{nonce}",
            help=f"JPG, JPEG or PNG, up to {MAX_UPLOAD_MB} MB. A single garment on a plain background works best.",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            state.set_image(uploaded.getvalue(), uploaded.name, "Upload", f"upload:{uploaded.file_id}")
        st.caption("Tip: photograph one item at a time, front-facing, in even light.")

    elif mode == "Webcam":
        shot = st.camera_input("Capture a garment", key=f"fv_camera_{nonce}", label_visibility="collapsed")
        if shot is not None:
            state.set_image(shot.getvalue(), "webcam-capture.jpg", "Webcam", f"camera:{shot.file_id}")
        st.caption("Your browser will ask for camera permission. Frames are processed in this session only.")

    else:
        cols = st.columns(3, gap="small")
        current = st.session_state.get(state.IMAGE)
        for i, product_id in enumerate(SAMPLE_PRODUCT_IDS):
            product = get_product(product_id)
            with cols[i % 3]:
                st.html(
                    f'<div class="fv-sample"><img src="{product.image_url}" alt="{escape(product.name)}"></div>'
                    f'<div class="fv-sample__name">{escape(product.name)}</div>'
                )
                selected = current is not None and current.token == f"sample:{product_id}"
                st.button(
                    "Selected" if selected else "Use image",
                    key=f"fv_sample_{product_id}",
                    on_click=_use_sample,
                    args=(product_id,),
                    disabled=selected,
                    width="stretch",
                )


def render_image_preview() -> bool:
    """Right panel: preview + Analyze / Clear. Returns True when Analyze was clicked."""
    card_heading("Preview")
    current: state.CurrentImage | None = st.session_state.get(state.IMAGE)

    if current is None:
        st.html(
            '<div class="fv-empty"><div class="fv-empty__mark">FV</div>'
            '<div class="fv-empty__title">No image selected</div>'
            '<div class="fv-empty__text">Add a JPG or PNG, capture a photo, or pick an item from the '
            "sample library to begin.</div></div>"
        )
    else:
        try:
            image = load_image(current.data)
        except InvalidImageError as exc:
            st.session_state[state.INPUT_ERROR] = str(exc)
            image = None
        if image is not None:
            with st.container(key="preview_frame"):
                st.image(image, width="stretch")
            st.html(
                '<div class="fv-meta-row">'
                f"<span><b>{escape(current.name)}</b></span>"
                f"<span>{image.width} &times; {image.height}px</span>"
                f"<span>{current.size_bytes / 1024:,.0f} KB</span>"
                f"<span>Source: {escape(current.source)}</span></div>"
            )

    error = st.session_state.get(state.INPUT_ERROR)
    if error:
        st.error(error)

    has_image = current is not None and not error
    c1, c2 = st.columns([1.6, 1], gap="small")
    analyze = c1.button("Analyze image", type="primary", width="stretch", disabled=not has_image,
                        key="fv_analyze")
    c2.button("Clear image", width="stretch", on_click=state.clear_image,
              disabled=current is None and st.session_state.get(state.RESULT) is None, key="fv_clear")
    return analyze and has_image
