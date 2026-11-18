"""Smoke and interaction tests using Streamlit's AppTest harness.

Run from the project root:  python -m pytest -q
"""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import config
import state
from data.mock_products import get_products

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    "app_pages/fashion_analysis.py",
    "app_pages/recommendation_gallery.py",
    "app_pages/categories.py",
    "app_pages/model_information.py",
    "app_pages/about.py",
]


@pytest.fixture(autouse=True)
def _fast(monkeypatch):
    monkeypatch.setattr(config, "SIMULATED_STAGE_DELAY_S", 0.0)


def _app() -> AppTest:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def _button(at: AppTest, key: str):
    return next(b for b in at.button if b.key == key)


def test_static_assets_exist():
    missing = [p.id for p in get_products() if not p.image_path.exists()]
    assert not missing, f"Run tools/build_assets.py - missing images: {missing}"
    assert config.LOGO_PATH.exists() and config.MARK_PATH.exists()


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders(page):
    at = _app()
    at.switch_page(page).run()
    assert not at.exception, at.exception


def test_analysis_flow_with_sample_image():
    at = _app()
    at.segmented_control(key="fv_input_mode").set_value("Sample library").run()
    _button(at, "fv_sample_FV-SH-002").click().run()
    assert at.session_state[state.IMAGE].source == "Sample"

    _button(at, "fv_analyze").click().run()
    assert not at.exception, at.exception
    result = at.session_state[state.RESULT]
    assert result is not None
    assert result.classification.category == "shirt"
    assert len(result.matches) == config.TOP_K_RECOMMENDATIONS
    assert all(m.product_id != "FV-SH-002" for m in result.matches)
    scores = [m.score for m in result.matches]
    assert scores == sorted(scores, reverse=True)

    _button(at, "fv_clear").click().run()
    assert at.session_state[state.IMAGE] is None
    assert at.session_state[state.RESULT] is None


def test_gallery_filter_search_sort_and_find_similar():
    at = _app()
    at.switch_page("app_pages/recommendation_gallery.py").run()

    at.button_group(key=state.GALLERY_CATEGORY).set_value("Shoes").run()
    finds = [b for b in at.button if b.key.startswith("fv_gallery_")]
    assert len(finds) == 6

    at.text_input(key=state.GALLERY_SEARCH).set_value("red").run()
    finds = [b.key for b in at.button if b.key.startswith("fv_gallery_")]
    assert finds and all(k.split("fv_gallery_")[1].startswith("FV-SO") for k in finds)

    at.text_input(key=state.GALLERY_SEARCH).set_value("zzz-no-match").run()
    assert any(b.key == "fv_reset_filters" for b in at.button)
    _button(at, "fv_reset_filters").click().run()
    assert at.session_state[state.GALLERY_CATEGORY] == state.ALL_CATEGORIES

    at.selectbox(key=state.GALLERY_SORT).set_value("Price: low to high").run()
    assert not at.exception

    _button(at, "fv_gallery_FV-BG-002").click().run()
    assert at.session_state[state.GALLERY_REF] == "FV-BG-002"
    assert not at.exception


def test_category_browse_sets_gallery_filter():
    at = _app()
    at.switch_page("app_pages/categories.py").run()
    _button(at, "fv_browse_dress").click().run()
    assert not at.exception, at.exception
    assert at.session_state[state.GALLERY_CATEGORY] == "Dresses"
    finds = [b for b in at.button if b.key.startswith("fv_gallery_")]
    assert len(finds) == 8


def test_uploaded_unknown_image_returns_documented_demo_prediction():
    from PIL import Image
    from services import build_recommendation_service

    service = build_recommendation_service("mock")
    result = service.analyze(Image.new("RGB", (400, 500), (90, 20, 20)), 10_000)
    assert result.classification.category == "tshirt"
    assert result.classification.confidence == pytest.approx(0.96)
    assert abs(sum(s.probability for s in result.classification.scores) - 1) < 1e-6
    assert result.embedding.dim == config.EMBEDDING_DIM
