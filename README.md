# FashionVision AI

**Fashion Detection & Visual Similarity Recommendation System** (university project)

FashionVision AI lets a user upload or photograph a garment, identifies its fashion category
(T-shirts, shirts, pants, dresses, jackets, shoes, bags, accessories), and recommends visually
similar products ranked by cosine similarity.

> **Status: Frontend Demo (v1.0.0).** This release contains the complete Streamlit frontend.
> Classification, embeddings and similarity scores come from **mock services**. No trained
> model, API or database is connected yet, and the UI labels every demo result as such.

---

## Quick start

Requires **Python 3.12+**.

```bash
cd prediction
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

The app opens at <http://localhost:8501>.

All product images are already in `static/images/products/`, so the app runs offline.
To rebuild them (for example after editing the catalogue), run:

```bash
python tools/build_assets.py           # builds only missing images
python tools/build_assets.py --force   # rebuilds everything
```

### Run the tests

```bash
python -m pytest -q
```

The tests use Streamlit's `AppTest` harness. They render every page and exercise the main
interactions: sample selection, analyse, clear, gallery filter/search/sort, "Find similar", and
browsing from a category into the gallery.

---

## Pages

| Page | What it does |
|---|---|
| **Fashion Analysis** | Upload a JPG/PNG, capture from the webcam, or pick a sample. Preview, then **Analyze** to get the predicted category, confidence, the full class-probability distribution, a visual analysis (model-input crop, edge-energy map, dominant colours, luminance histogram, embedding preview and summary) and the **top 5 similar products**. **Clear** resets everything. |
| **Recommendation Gallery** | The full catalogue ranked by similarity to your analysed image (or to any product via **Find similar**). Category filter, free-text search (name, colour, material, ID) and sorting. |
| **Categories** | The eight categories, each with a cover image and product count. **Browse** opens the gallery pre-filtered. |
| **Model Information** | Planned architecture: EfficientNetB0 classifier, CNN feature extractor, KNN + cosine similarity + FAISS. Shows the pipeline, integration roadmap and service contracts. No fabricated metrics. |
| **About Project** | Description, objectives, technologies, ML workflow and team. |

---

## Project structure

```
prediction/
├── app.py                      # Entry point: page config, CSS, navigation, sidebar
├── config.py                   # App constants, backend mode, model I/O contract
├── state.py                    # Session-state keys + cached service instance
├── app_pages/                  # One file per page (run by st.navigation)
│   ├── fashion_analysis.py
│   ├── recommendation_gallery.py
│   ├── categories.py
│   ├── model_information.py
│   └── about.py
├── components/                 # Reusable UI pieces (no ML logic)
│   ├── layout.py               # Page header, section titles, cards, notices, footer
│   ├── sidebar.py              # Logo + project status footer
│   ├── upload_component.py     # Upload / webcam / samples + preview panel
│   ├── prediction_result.py    # Classification, visual analysis, matches
│   ├── product_card.py         # Product card HTML
│   └── recommendation_grid.py  # Responsive product grid
├── services/                   # ML service layer (no Streamlit imports)
│   ├── __init__.py             # build_recommendation_service(): mock vs api switch
│   ├── types.py                # Result dataclasses: the frontend/backend contract
│   ├── preprocessing.py        # Real image loading, 224x224 crop, pixel statistics
│   ├── classification.py       # FashionClassifier protocol + mock
│   ├── feature_extraction.py   # FeatureExtractor protocol + mock
│   ├── similarity_search.py    # SimilarityIndex protocol + NumPy cosine k-NN
│   ├── recommendation.py       # Orchestrates the full pipeline
│   └── mock_space.py           # Deterministic synthetic embedding space (demo only)
├── data/mock_products.py       # Mock catalogue: 43 products, 8 categories
├── static/                     # Served by Streamlit static file serving
│   ├── images/products/        # Product photos (800x1000 studio canvas)
│   └── brand/                  # logo.png, mark.png
├── styles/main.css             # Grayscale design system
├── tools/build_assets.py       # Downloads and normalises images, renders brand assets
├── tests/test_app.py           # AppTest smoke + interaction tests
└── .streamlit/config.toml      # Theme (palette, fonts, dark sidebar) + server settings
```

Two deliberate departures from the suggested layout:

* `pages/` is named **`app_pages/`**. Streamlit treats a folder called `pages/` as its legacy
  auto-discovered multipage app, which conflicts with `st.navigation`.
* `assets/images` is **`static/`**. Streamlit only serves files over HTTP from a folder named
  `static/`, which lets product cards use `<img>` tags without base64 encoding.

---

## How the mock pipeline behaves

* **Sample images** are recognised with a perceptual hash and return their true category.
* **Any other upload or webcam frame** returns the documented demo prediction: **T-shirt, 96%**.
* **Embeddings** are synthetic 1,280-d unit vectors clustered by category, so they behave like
  real ones. Cosine similarity and k-NN ranking are then computed genuinely in NumPy (the same
  operation as a FAISS `IndexFlatIP`).
* **Pixel statistics** (dominant colours, luminance, brightness/contrast, the 224×224 crop and
  the edge map) are real computations on the user's image.

---

## Integrating the real models

The UI talks only to `RecommendationService` (`services/recommendation.py`), which composes three
protocols:

| Protocol | Method | Replace mock with |
|---|---|---|
| `FashionClassifier` | `classify(image) -> ClassificationResult` | EfficientNetB0 from Hugging Face, or a FastAPI `/classify` call |
| `FeatureExtractor` | `extract(image) -> EmbeddingResult` | Backbone pooled features (1,280-d, L2-normalised) |
| `SimilarityIndex` | `search(vector, k) -> list[SimilarityMatch]`, `score_all(vector)` | FAISS index + PostgreSQL product metadata |

Steps:

1. Implement the protocols, or a FastAPI client that returns the dataclasses in `services/types.py`.
2. Register it in `services/__init__.py` under `BACKEND_MODE == "api"`.
3. Run with `FASHIONVISION_BACKEND=api` (and `FASHIONVISION_API_URL=...`).
4. Replace `data/mock_products.py` lookups with catalogue queries; keep the `Product` shape.

Model loading belongs in `state.get_service()`, which is wrapped in `@st.cache_resource` so it
runs once per server process.

---

## Image credits

Product photos are demo assets from [DummyJSON](https://dummyjson.com) and
[Fake Store API](https://fakestoreapi.com), re-composited onto a uniform studio background.
The pants images are flat-lay placeholders rendered by `tools/build_assets.py`. Product names in
the catalogue are generic and invented for the demo.

## Team

| Member | Role |
|---|---|
| Pheng Sopanha | Team Leader · AI/ML Engineering |
| Den Chankarona | Frontend Development |
| Tith AnnChengly | Backend Development |
| Phearun Lidasaknit | Database Engineering |
