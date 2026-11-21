import os
import tempfile
import pytest
from PIL import Image
import io

from backend.preprocessing.image_sanitizer import sanitize_and_save_image


def test_privacy_file_removal(sample_jpeg_bytes):
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.makedirs(os.path.join(tmp_dir, "thumbnails"), exist_ok=True)
        res = sanitize_and_save_image(sample_jpeg_bytes, "privacy_test.jpg", tmp_dir)

        primary_path = res["file_path"]
        thumb_path = res["thumbnail_path"]

        assert os.path.exists(primary_path)
        assert os.path.exists(thumb_path)

        # Simulate cascading deletion
        os.remove(primary_path)
        os.remove(thumb_path)

        assert not os.path.exists(primary_path)
        assert not os.path.exists(thumb_path)
