import io
from PIL import Image
from inference.models.detector import SSDLiteDetector


def test_detector_bounding_box_coordinates(sample_jpeg_bytes):
    detector = SSDLiteDetector()
    img = Image.open(io.BytesIO(sample_jpeg_bytes))
    w, h = img.size

    result = detector.detect(img, score_threshold=0.10)

    assert result["image_width"] == w
    assert result["image_height"] == h
    assert "detected_objects" in result
    assert "class_counts" in result

    for obj in result["detected_objects"]:
        x1, y1, x2, y2 = obj["bbox_pixels"]
        nx1, ny1, nx2, ny2 = obj["bbox_normalized"]

        # Valid box dimensions
        assert x1 >= 0 and x1 <= w
        assert y1 >= 0 and y1 <= h
        assert x2 >= x1
        assert y2 >= y1

        # Normalized coordinates strictly between 0.0 and 1.0
        assert 0.0 <= nx1 <= 1.0
        assert 0.0 <= ny1 <= 1.0
        assert 0.0 <= nx2 <= 1.0
        assert 0.0 <= ny2 <= 1.0


def test_detector_threshold_filtering(sample_jpeg_bytes):
    detector = SSDLiteDetector()
    img = Image.open(io.BytesIO(sample_jpeg_bytes))

    # Low threshold should yield at least or more detections than high threshold
    res_low = detector.detect(img, score_threshold=0.15)
    res_high = detector.detect(img, score_threshold=0.85)

    assert res_low["total_objects_count"] >= res_high["total_objects_count"]
