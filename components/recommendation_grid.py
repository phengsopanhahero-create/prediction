"""Responsive product grid built from ``product_card_html``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import streamlit as st

from components.product_card import product_card_html
from data.mock_products import Product


@dataclass(frozen=True)
class GridItem:
    product: Product
    score: float | None = None
    rank: int | None = None


def render_product_grid(
    items: Sequence[GridItem],
    columns: int = 4,
    *,
    key_prefix: str,
    action_label: str | None = None,
    on_action: Callable[[str], None] | None = None,
) -> None:
    """Render products ``columns`` per row. Columns stack automatically on mobile.

    If ``on_action`` is provided each card gets a small text button that calls
    ``on_action(product_id)``.
    """
    for start in range(0, len(items), columns):
        row = items[start:start + columns]
        cols = st.columns(columns, gap="medium")
        for col, item in zip(cols, row):
            with col:
                st.html(product_card_html(item.product, item.score, item.rank))
                if on_action and action_label:
                    st.button(
                        action_label,
                        key=f"{key_prefix}_{item.product.id}",
                        type="tertiary",
                        on_click=on_action,
                        args=(item.product.id,),
                    )
