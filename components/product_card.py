"""Product card markup (pure function -> HTML string)."""

from __future__ import annotations

from html import escape

from data.mock_products import Product


def format_score(score: float) -> str:
    return f"{max(0.0, score) * 100:.1f}%"


def product_card_html(product: Product, score: float | None = None, rank: int | None = None) -> str:
    rank_html = f'<span class="fv-rank">{rank:02d}</span>' if rank is not None else ""
    if score is not None:
        width = max(0.0, min(1.0, score)) * 100
        score_html = (
            f'<span class="fv-score">{format_score(score)}<small>match</small></span>'
        )
        meter_html = f'<div class="fv-meter"><span style="width:{width:.1f}%"></span></div>'
    else:
        score_html, meter_html = "", ""

    return (
        '<article class="fv-product">'
        f'<div class="fv-product__media"><img src="{product.image_url}" alt="{escape(product.name)}" loading="lazy">{rank_html}</div>'
        '<div class="fv-product__body">'
        f'<div class="fv-product__cat">{escape(product.category_label)} &middot; {escape(product.color)}</div>'
        f'<div class="fv-product__name">{escape(product.name)}</div>'
        f'<div class="fv-product__id">{escape(product.id)}</div>'
        f'<div class="fv-product__foot"><span class="fv-product__price">${product.price:,.2f}</span>{score_html}</div>'
        f"{meter_html}"
        "</div></article>"
    )
