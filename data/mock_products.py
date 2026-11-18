"""Mock product catalogue used by the frontend demo.

This module is the single source of truth for demo data. When the PostgreSQL
backend is connected, replace ``get_products`` / ``get_product`` with calls to
the API and keep the ``Product`` / ``Category`` shapes as the contract.

Photography credits
-------------------
* ``dummyjson``  - product renders from https://dummyjson.com (free demo API)
* ``fakestore``  - product photos from https://fakestoreapi.com (free demo API)
* ``generated``  - flat-lay placeholders rendered locally by tools/build_assets.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_IMAGE_DIR = PROJECT_ROOT / "static" / "images" / "products"
STATIC_URL_PREFIX = "app/static/images/products"


@dataclass(frozen=True)
class Category:
    key: str
    label: str          # plural, used for navigation and filters
    singular: str       # used for model predictions ("T-shirt")
    code: str           # product-ID prefix
    description: str
    cover_product_id: str


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str       # Category.key
    color: str
    material: str
    price: float
    source: str         # dummyjson | fakestore | generated
    source_ref: str     # remote URL, or a render spec for generated items
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def image_path(self) -> Path:
        return PRODUCT_IMAGE_DIR / f"{self.id}.jpg"

    @property
    def image_url(self) -> str:
        """URL served by Streamlit static file serving."""
        return f"{STATIC_URL_PREFIX}/{self.id}.jpg"

    @property
    def category_label(self) -> str:
        return get_category(self.category).label

    @property
    def search_text(self) -> str:
        cat = get_category(self.category)
        return " ".join(
            [self.id, self.name, self.color, self.material, cat.label, cat.singular, *self.tags]
        ).lower()


CATEGORIES: tuple[Category, ...] = (
    Category("tshirt", "T-shirts", "T-shirt", "TS",
             "Crew, V-neck and henley tees in cotton and performance jersey.", "FV-TS-004"),
    Category("shirt", "Shirts", "Shirt", "SH",
             "Woven shirts: oxford, flannel, poplin and camp collars.", "FV-SH-002"),
    Category("pants", "Pants", "Pants", "PT",
             "Denim, chinos, tailored trousers and utility cuts.", "FV-PT-001"),
    Category("dress", "Dresses", "Dress", "DR",
             "Day dresses, midi silhouettes and evening gowns.", "FV-DR-003"),
    Category("jacket", "Jackets", "Jacket", "JK",
             "Field jackets, moto leather and weatherproof shells.", "FV-JK-003"),
    Category("shoes", "Shoes", "Shoes", "SO",
             "Sneakers, pumps, heels and sandals.", "FV-SO-005"),
    Category("bag", "Bags", "Bag", "BG",
             "Totes, satchels, hobos and backpacks.", "FV-BG-002"),
    Category("accessory", "Accessories", "Accessory", "AC",
             "Eyewear, watches and jewellery.", "FV-AC-005"),
)

_DJ = "https://cdn.dummyjson.com/product-images"
_FS = "https://fakestoreapi.com/img"

PRODUCTS: tuple[Product, ...] = (
    # T-shirts -----------------------------------------------------------
    Product("FV-TS-001", "Raglan Henley Tee", "tshirt", "Heather grey / black", "Cotton jersey", 29.00,
            "fakestore", f"{_FS}/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_t.png", ("henley", "raglan", "casual")),
    Product("FV-TS-002", "Long-Sleeve V-Neck Tee", "tshirt", "Slate blue", "Cotton blend", 34.00,
            "fakestore", f"{_FS}/71YXzeOuslL._AC_UY879_t.png", ("long sleeve", "v-neck", "slim fit")),
    Product("FV-TS-003", "Draped Boat-Neck Tee", "tshirt", "White", "Modal jersey", 26.00,
            "fakestore", f"{_FS}/71z3kpMAYsL._AC_UY879_t.png", ("boat neck", "relaxed", "womens")),
    Product("FV-TS-004", "Performance V-Neck Tee", "tshirt", "Red", "Moisture-wicking polyester", 22.00,
            "fakestore", f"{_FS}/51eg55uWmdL._AC_UX679_t.png", ("sport", "v-neck", "quick dry")),
    Product("FV-TS-005", "Graphic Slogan Tee", "tshirt", "Plum", "Cotton", 24.00,
            "fakestore", f"{_FS}/61pHAEJ4NML._AC_UX679_t.png", ("graphic", "print", "casual")),
    # Shirts ---------------------------------------------------------------
    Product("FV-SH-001", "Gingham Oxford Shirt", "shirt", "Blue / white", "Cotton oxford", 49.00,
            "dummyjson", f"{_DJ}/mens-shirts/blue-&-black-check-shirt/1.webp", ("gingham", "check", "button-down")),
    Product("FV-SH-002", "Buffalo Check Flannel Shirt", "shirt", "Red / black", "Brushed flannel", 54.00,
            "dummyjson", f"{_DJ}/mens-shirts/man-plaid-shirt/1.webp", ("flannel", "check", "plaid")),
    Product("FV-SH-003", "Tropical Print Camp Shirt", "shirt", "Indigo floral", "Viscose", 45.00,
            "dummyjson", f"{_DJ}/mens-shirts/man-short-sleeve-shirt/1.webp", ("short sleeve", "floral", "resort")),
    Product("FV-SH-004", "Tartan Poplin Shirt", "shirt", "Teal / grey", "Cotton poplin", 52.00,
            "dummyjson", f"{_DJ}/mens-shirts/men-check-shirt/1.webp", ("tartan", "check", "plaid")),
    # Pants (locally generated flat-lay placeholders) ------------------------
    Product("FV-PT-001", "Straight-Leg Denim Jeans", "pants", "Indigo", "Rigid denim", 69.00,
            "generated", "pants:jeans:#34445E", ("denim", "jeans", "straight leg")),
    Product("FV-PT-002", "Slim Chino Trousers", "pants", "Stone", "Cotton twill", 59.00,
            "generated", "pants:chino:#B9A98A", ("chino", "slim", "smart casual")),
    Product("FV-PT-003", "Tailored Wool Trousers", "pants", "Charcoal", "Wool blend", 89.00,
            "generated", "pants:tailored:#3E3E40", ("tailored", "formal", "pleated")),
    Product("FV-PT-004", "Relaxed Cargo Pants", "pants", "Olive", "Cotton ripstop", 64.00,
            "generated", "pants:cargo:#5E6145", ("cargo", "utility", "relaxed")),
    # Dresses --------------------------------------------------------------
    Product("FV-DR-001", "Polka Dot Skater Dress", "dress", "Powder blue", "Cotton sateen", 58.00,
            "dummyjson", f"{_DJ}/tops/blue-frock/1.webp", ("polka dot", "skater", "short sleeve")),
    Product("FV-DR-002", "Leaf Print Maxi Dress", "dress", "Black / ivory", "Crepe", 79.00,
            "dummyjson", f"{_DJ}/tops/girl-summer-dress/1.webp", ("maxi", "print", "off shoulder")),
    Product("FV-DR-003", "Button-Front Midi Dress", "dress", "Sage grey", "Linen blend", 72.00,
            "dummyjson", f"{_DJ}/tops/gray-dress/1.webp", ("midi", "sleeveless", "linen")),
    Product("FV-DR-004", "Tiered Bandeau Dress", "dress", "Teal", "Chiffon", 64.00,
            "dummyjson", f"{_DJ}/tops/short-frock/1.webp", ("strapless", "tiered", "mini")),
    Product("FV-DR-005", "Gingham Bow Dress", "dress", "Black / white", "Cotton", 61.00,
            "dummyjson", f"{_DJ}/tops/tartan-dress/1.webp", ("gingham", "check", "bow")),
    Product("FV-DR-006", "Floral Off-Shoulder Gown", "dress", "Black floral", "Satin", 145.00,
            "dummyjson", f"{_DJ}/womens-dresses/black-women's-gown/1.webp", ("gown", "evening", "floral")),
    Product("FV-DR-007", "Strapless Column Gown", "dress", "Scarlet", "Silk blend", 168.00,
            "dummyjson", f"{_DJ}/womens-dresses/corset-leather-with-skirt/1.webp", ("gown", "evening", "strapless")),
    Product("FV-DR-008", "Polka Dot Tea Dress", "dress", "Ivory", "Cotton poplin", 66.00,
            "dummyjson", f"{_DJ}/womens-dresses/dress-pea/1.webp", ("polka dot", "midi", "vintage")),
    # Jackets --------------------------------------------------------------
    Product("FV-JK-001", "Cotton Field Jacket", "jacket", "Khaki", "Cotton canvas", 98.00,
            "fakestore", f"{_FS}/71li-ujtlUL._AC_UX679_t.png", ("field", "utility", "stand collar")),
    Product("FV-JK-002", "3-in-1 Hooded Shell Jacket", "jacket", "Violet", "Nylon shell, fleece liner", 139.00,
            "fakestore", f"{_FS}/51Y5NI-I5jL._AC_UX679_t.png", ("outdoor", "hooded", "waterproof")),
    Product("FV-JK-003", "Hooded Faux-Leather Moto Jacket", "jacket", "Black", "Faux leather", 119.00,
            "fakestore", f"{_FS}/81XH0e8fefL._AC_UY879_t.png", ("moto", "biker", "leather")),
    Product("FV-JK-004", "Belted Rain Parka", "jacket", "Navy", "Coated cotton", 112.00,
            "fakestore", f"{_FS}/71HblAHs5xL._AC_UY879_-2t.png", ("rain", "parka", "hooded")),
    # Shoes ----------------------------------------------------------------
    Product("FV-SO-001", "Retro Runner Trainers", "shoes", "Multicolour", "Suede and mesh", 95.00,
            "dummyjson", f"{_DJ}/mens-shoes/puma-future-rider-trainers/1.webp", ("sneakers", "running", "retro")),
    Product("FV-SO-002", "Court Low-Top Sneakers", "shoes", "White / red", "Leather", 89.00,
            "dummyjson", f"{_DJ}/mens-shoes/sports-sneakers-off-white-red/1.webp", ("sneakers", "low top", "court")),
    Product("FV-SO-003", "Pointed Leather Pumps", "shoes", "Black / cognac", "Calf leather", 120.00,
            "dummyjson", f"{_DJ}/womens-shoes/black-&-brown-slipper/1.webp", ("pumps", "heels", "pointed toe")),
    Product("FV-SO-004", "Square-Toe Slide Sandals", "shoes", "Black", "Leather", 75.00,
            "dummyjson", f"{_DJ}/womens-shoes/calvin-klein-heel-shoes/1.webp", ("sandals", "slides", "block heel")),
    Product("FV-SO-005", "Metallic Stiletto Pumps", "shoes", "Champagne gold", "Metallic leather", 135.00,
            "dummyjson", f"{_DJ}/womens-shoes/golden-shoes-woman/1.webp", ("stiletto", "heels", "evening")),
    Product("FV-SO-006", "Patent Pointed Heels", "shoes", "Red", "Patent leather", 115.00,
            "dummyjson", f"{_DJ}/womens-shoes/red-shoes/1.webp", ("heels", "patent", "pointed toe")),
    # Bags -----------------------------------------------------------------
    Product("FV-BG-001", "Structured Leather Tote", "bag", "Navy", "Pebbled leather", 159.00,
            "dummyjson", f"{_DJ}/womens-bags/blue-women's-handbag/1.webp", ("tote", "structured", "work")),
    Product("FV-BG-002", "Leather Hobo Bag", "bag", "Tan", "Full-grain leather", 175.00,
            "dummyjson", f"{_DJ}/womens-bags/heshe-women's-leather-bag/1.webp", ("hobo", "shoulder bag", "slouchy")),
    Product("FV-BG-003", "Mini Drawstring Backpack", "bag", "White", "Faux leather", 85.00,
            "dummyjson", f"{_DJ}/womens-bags/white-faux-leather-backpack/1.webp", ("backpack", "mini", "drawstring")),
    Product("FV-BG-004", "Top-Handle Satchel", "bag", "Black", "Saffiano leather", 189.00,
            "dummyjson", f"{_DJ}/womens-bags/women-handbag-black/1.webp", ("satchel", "top handle", "structured")),
    # Accessories ----------------------------------------------------------
    Product("FV-AC-001", "Browline Sunglasses", "accessory", "Tortoise / green", "Acetate and metal", 65.00,
            "dummyjson", f"{_DJ}/sunglasses/black-sun-glasses/1.webp", ("sunglasses", "eyewear", "browline")),
    Product("FV-AC-002", "Gradient Aviator Sunglasses", "accessory", "Gold / blue", "Metal", 72.00,
            "dummyjson", f"{_DJ}/sunglasses/classic-sun-glasses/1.webp", ("sunglasses", "eyewear", "aviator")),
    Product("FV-AC-003", "Tinted Aviator Sunglasses", "accessory", "Black / mint", "Metal", 68.00,
            "dummyjson", f"{_DJ}/sunglasses/green-and-black-glasses/1.webp", ("sunglasses", "eyewear", "aviator")),
    Product("FV-AC-004", "Leather Strap Moonphase Watch", "accessory", "Gold / brown", "Steel and leather", 245.00,
            "dummyjson", f"{_DJ}/mens-watches/brown-leather-belt-watch/1.webp", ("watch", "leather strap", "classic")),
    Product("FV-AC-005", "Gold-Tone Bracelet Watch", "accessory", "Gold / navy", "Stainless steel", 210.00,
            "dummyjson", f"{_DJ}/womens-watches/watch-gold-for-women/1.webp", ("watch", "bracelet", "minimal")),
    Product("FV-AC-006", "Steel Link Watch", "accessory", "Silver / black", "Stainless steel", 195.00,
            "dummyjson", f"{_DJ}/womens-watches/women's-wrist-watch/1.webp", ("watch", "link bracelet", "minimal")),
    Product("FV-AC-007", "Crystal Drop Earring", "accessory", "Emerald", "Crystal and gold-tone", 38.00,
            "dummyjson", f"{_DJ}/womens-jewellery/green-crystal-earring/1.webp", ("earring", "jewellery", "drop")),
    Product("FV-AC-008", "Checkered Hoop Earring", "accessory", "Mint / cream", "Resin", 32.00,
            "dummyjson", f"{_DJ}/womens-jewellery/green-oval-earring/1.webp", ("earring", "jewellery", "hoop")),
)

# Products offered as one-click examples on the Fashion Analysis page.
SAMPLE_PRODUCT_IDS: tuple[str, ...] = (
    "FV-TS-004", "FV-SH-002", "FV-PT-001", "FV-DR-003", "FV-JK-003", "FV-SO-002",
)


@lru_cache(maxsize=1)
def _product_index() -> dict[str, Product]:
    return {p.id: p for p in PRODUCTS}


@lru_cache(maxsize=1)
def _category_index() -> dict[str, Category]:
    return {c.key: c for c in CATEGORIES}


def get_products() -> tuple[Product, ...]:
    return PRODUCTS


def get_product(product_id: str) -> Product:
    return _product_index()[product_id]


def get_categories() -> tuple[Category, ...]:
    return CATEGORIES


def get_category(key: str) -> Category:
    return _category_index()[key]


def category_by_label(label: str) -> Category | None:
    return next((c for c in CATEGORIES if c.label == label), None)


def product_counts() -> dict[str, int]:
    counts = {c.key: 0 for c in CATEGORIES}
    for p in PRODUCTS:
        counts[p.category] += 1
    return counts
