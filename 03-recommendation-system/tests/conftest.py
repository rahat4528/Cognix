import os
import sys
import pytest
import pandas as pd

# Setup path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


@pytest.fixture
def sample_items_df() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "id": "aud-01",
            "title": "Aura Pro Wireless Headphones",
            "category": "Audio",
            "tags": "wireless bluetooth anc audiophile",
            "description": "Active noise cancelling over-ear headphones with high resolution audio."
        },
        {
            "id": "aud-02",
            "title": "WaveBuds ANC Earbuds",
            "category": "Audio",
            "tags": "wireless bluetooth earbuds anc waterproof",
            "description": "True wireless in-ear earbuds with ambient mode and water resistance."
        },
        {
            "id": "cmp-01",
            "title": "TitanBook Pro 16 Laptop",
            "category": "Computing",
            "tags": "laptop workstation developer 32gb",
            "description": "High performance laptop with 16 cores and 32GB RAM for programming."
        },
        {
            "id": "cmp-02",
            "title": "ApexMech Wireless Mechanical Keyboard",
            "category": "Computing",
            "tags": "keyboard mechanical wireless rgb",
            "description": "75% layout wireless tactile mechanical keyboard with hot-swappable switches."
        },
        {
            "id": "off-01",
            "title": "ErgoLift Dual-Motor Standing Desk",
            "category": "Smart Office",
            "tags": "standing-desk motorized ergonomic office",
            "description": "Electric height adjustable sit-stand desk frame with memory presets."
        }
    ])


@pytest.fixture
def sample_interactions_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"user_id": "u1", "item_id": "aud-01", "weight": 5.0, "session_id": "s1", "timestamp": 100.0},
        {"user_id": "u1", "item_id": "aud-02", "weight": 3.0, "session_id": "s1", "timestamp": 110.0},
        {"user_id": "u2", "item_id": "cmp-01", "weight": 5.0, "session_id": "s2", "timestamp": 120.0},
        {"user_id": "u2", "item_id": "cmp-02", "weight": 3.0, "session_id": "s2", "timestamp": 130.0},
        {"user_id": "u3", "item_id": "aud-01", "weight": 2.0, "session_id": "s3", "timestamp": 140.0},
        {"user_id": "u3", "item_id": "cmp-01", "weight": 5.0, "session_id": "s3", "timestamp": 150.0},
        {"user_id": "u4", "item_id": "off-01", "weight": 5.0, "session_id": "s4", "timestamp": 160.0},
        {"user_id": "u4", "item_id": "cmp-02", "weight": 2.0, "session_id": "s4", "timestamp": 170.0},
    ])
