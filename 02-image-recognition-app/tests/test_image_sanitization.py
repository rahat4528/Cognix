import os
import tempfile
import pytest
from PIL import Image
import io

from backend.preprocessing.image_sanitizer import (
    sanitize_and_save_image,
    calculate_dhash,
    ImageSanitizationError
)


def test_sanitize_valid_jpeg(sample_jpeg_bytes):
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.makedirs(os.path.join(tmp_dir, "thumbnails"), exist_ok=True)
        res = sanitize_and_save_image(sample_jpeg_bytes, "test.jpg", tmp_dir)

        assert res["original_name"] == "test.jpg"
        assert res["mime_type"] == "image/jpeg"
        assert res["width"] == 320
        assert res["height"] == 240
        assert os.path.exists(res["file_path"])
        assert os.path.exists(res["thumbnail_path"])
        assert len(res["perceptual_hash"]) == 16


def test_sanitize_valid_png(sample_png_bytes):
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.makedirs(os.path.join(tmp_dir, "thumbnails"), exist_ok=True)
        res = sanitize_and_save_image(sample_png_bytes, "graphic.png", tmp_dir)

        assert res["original_name"] == "graphic.png"
        assert res["mime_type"] == "image/png"
        assert res["width"] == 200
        assert res["height"] == 200


def test_sanitize_corrupt_file_rejected():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corrupt_bytes = b"NOT_AN_IMAGE_DATA_HEADER_CORRUPT"
        with pytest.raises(ImageSanitizationError) as exc_info:
            sanitize_and_save_image(corrupt_bytes, "bad.jpg", tmp_dir)
        assert "Failed to decode image" in str(exc_info.value) or "Unsupported" in str(exc_info.value)


def test_sanitize_empty_file_rejected():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with pytest.raises(ImageSanitizationError) as exc_info:
            sanitize_and_save_image(b"", "empty.jpg", tmp_dir)
        assert "empty" in str(exc_info.value).lower()


def test_perceptual_hash_determinism(sample_jpeg_bytes):
    img = Image.open(io.BytesIO(sample_jpeg_bytes))
    hash1 = calculate_dhash(img)
    hash2 = calculate_dhash(img)
    assert hash1 == hash2
    assert len(hash1) == 16
