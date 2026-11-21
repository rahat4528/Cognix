import os
import sys
import pytest
from PIL import Image, ImageDraw
import io

# Setup path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (320, 240), color=(50, 100, 150))
    draw = ImageDraw.Draw(img)
    draw.rectangle([60, 60, 260, 180], fill=(200, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


@pytest.fixture
def sample_png_bytes() -> bytes:
    img = Image.new("RGB", (200, 200), color=(20, 180, 80))
    draw = ImageDraw.Draw(img)
    draw.ellipse([40, 40, 160, 160], fill=(255, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_webp_bytes() -> bytes:
    img = Image.new("RGB", (150, 150), color=(100, 50, 200))
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()
