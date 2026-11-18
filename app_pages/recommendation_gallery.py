"""Page 2 - Recommendation Gallery."""

from __future__ import annotations

from html import escape

import streamlit as st

import state
from components.layout import demo_notice, image_to_data_uri, page_header
from components.recommendation_grid import GridItem, render_product_grid
from data.mock_products import category_by_label, get_categories, get_category, get_product, get_products
from services import load_image

SORT_OPTIONS = (
    "Similarity: high to low",
    "Similarity: low to high",
    "Name: A to Z",
    "Price: low to high",
    "Price: high to low",
)
DEFAULT_REFERENCE_ID = "FV-TS-004"


def _set_reference(product_id: str) -> None:
    st.session_state[state.GALLERY_REF] = product_id
    st.toast(f"Showing products similar to {get_product(product_id).name}")


def _reset_filters() -> None:
    st.session_state[state.GALLERY_CATEGORY] = state.ALL_CATEGORIES
    st.session_state[state.GALLERY_SEARCH] = ""
    st.session_state[state.GALLERY_SORT] = SORT_OPTIONS[0]


def _resolve_reference():
    """Return (vector, html_thumb, title, meta, exclude_id) for the current reference."""
    service = state.get_service()
    ref = st.session_state.get(state.GALLERY_REF)
    result = st.session_state.get(state.RESULT)
    current = st.session_state.get(state.IMAGE)

    if ref in (None, "analysis") and result is not None and current is not None:
        cat = get_category(result.classification.category)
        thumb = image_to_data_uri(load_image(current.data), max_side=200)
        return (result.embedding.vector, thumb, "Your analysed image",
                f"Predicted {cat.singular} · {result.classification.confidence * 100:.0f}% confidence", None)

    product_id = ref if ref not in (None, "analysis") else DEFAULT_REFERENCE_ID
    product = get_product(product_id)
    return (service.product_vector(product_id), product.image_url, product.name,
            f"{product.category_label} · {product.id}", product_id)


page_header(
    "Discover",
    "Recommendation Gallery",
    "Browse the catalogue ranked by visual similarity to a reference item. Analyse an image to "
    "personalise the ranking, or choose “Find similar” on any product to pivot the gallery.",
)
demo_notice()
st.space("small")

vector, thumb, ref_title, ref_meta, exclude_id = _resolve_reference()
scores = state.get_service().score_catalog(vector)

ref_col, reset_col = st.columns([4, 1], vertical_alignment="center")
with ref_col:
    st.html(
        f'<div class="fv-ref"><img src="{thumb}" alt="">'
        f'<div><div class="fv-ref__label">Similarity reference</div>'
        f'<div class="fv-ref__name">{escape(ref_title)}</div>'
        f'<div class="fv-ref__meta">{escape(ref_meta)}</div></div></div>'
    )
with reset_col:
    if st.session_state.get(state.GALLERY_REF) not in (None, "analysis"):
        has_analysis = st.session_state.get(state.RESULT) is not None
        st.button("Use my analysis" if has_analysis else "Reset reference", key="fv_ref_reset",
                  on_click=lambda: st.session_state.update({state.GALLERY_REF: None}), width="stretch")

st.space("small")
category_options = [state.ALL_CATEGORIES] + [c.label for c in get_categories()]
st.pills("Category", category_options, key=state.GALLERY_CATEGORY, required=True,
         label_visibility="collapsed")

search_col, sort_col = st.columns([2.2, 1], gap="small")
with search_col:
    st.text_input("Search", key=state.GALLERY_SEARCH, placeholder="Search by name, colour, material or product ID",
                  label_visibility="collapsed", icon=":material/search:")
with sort_col:
    st.selectbox("Sort by", SORT_OPTIONS, key=state.GALLERY_SORT, label_visibility="collapsed")

# Filter -------------------------------------------------------------------
selected_label = st.session_state[state.GALLERY_CATEGORY] or state.ALL_CATEGORIES
selected_category = category_by_label(selected_label)
query = (st.session_state[state.GALLERY_SEARCH] or "").strip().lower()

products = [p for p in get_products() if p.id != exclude_id]
if selected_category is not None:
    products = [p for p in products if p.category == selected_category.key]
if query:
    terms = query.split()
    products = [p for p in products if all(t in p.search_text for t in terms)]

sort_key = st.session_state[state.GALLERY_SORT]
if sort_key == "Similarity: high to low":
    products.sort(key=lambda p: scores[p.id], reverse=True)
elif sort_key == "Similarity: low to high":
    products.sort(key=lambda p: scores[p.id])
elif sort_key == "Name: A to Z":
    products.sort(key=lambda p: p.name)
elif sort_key == "Price: low to high":
    products.sort(key=lambda p: p.price)
else:
    products.sort(key=lambda p: p.price, reverse=True)

total = len(get_products()) - (1 if exclude_id else 0)
st.html(f'<div class="fv-count">Showing {len(products)} of {total} products</div>')

if not products:
    st.html(
        '<div class="fv-empty" style="min-height:220px"><div class="fv-empty__title">No products match</div>'
        '<div class="fv-empty__text">Try a different search term or category.</div></div>'
    )
    st.button("Reset filters", on_click=_reset_filters, key="fv_reset_filters")
else:
    items = [GridItem(p, scores[p.id]) for p in products]
    render_product_grid(items, columns=4, key_prefix="fv_gallery", action_label="Find similar",
                        on_action=_set_reference)
