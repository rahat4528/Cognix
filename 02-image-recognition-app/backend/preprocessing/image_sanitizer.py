import io
import os
import uuid
from typing import Tuple, Dict, Any
from PIL import Image, ImageOps, UnidentifiedImageError

# Safe image processing settings
MAX_IMAGE_PIXELS = 25_000_000  # 25 Megapixels
MAX_DIMENSION = 8192
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageSanitizationError(Exception):
    pass


def calculate_dhash(image: Image.Image, hash_size: int = 8) -> str:
    """
    Computes difference hash (dHash) for perceptual similarity comparison.
    Resizes to (hash_size + 1, hash_size), converts to grayscale, and compares adjacent pixels.
    """
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(resized.getdata())
    diff = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = pixels[row * (hash_size + 1) + col]
            pixel_right = pixels[row * (hash_size + 1) + col + 1]
            diff.append(pixel_left > pixel_right)
    # Convert bool list to hex string
    decimal_val = 0
    hex_str = []
    for index, value in enumerate(diff):
        if value:
            decimal_val += 2 ** (index % 4)
        if (index % 4) == 3:
            hex_str.append(hex(decimal_val)[2:])
            decimal_val = 0
    return "".join(hex_str)


def sanitize_and_save_image(
    file_bytes: bytes,
    original_filename: str,
    upload_dir: str
) -> Dict[str, Any]:
    """
    Validates, sanitizes, strips EXIF, generates thumbnails, and computes perceptual hash.
    Protects against decompression bombs, format spoofing, and metadata/GPS leakage.
    """
    if len(file_bytes) == 0:
        raise ImageSanitizationError("Uploaded file is empty.")

    try:
        # Step 1: Verify valid image header and format
        raw_stream = io.BytesIO(file_bytes)
        with Image.open(raw_stream) as img:
            img.verify()
            detected_format = img.format

        if not detected_format or detected_format.upper() not in ALLOWED_FORMATS:
            raise ImageSanitizationError(f"Unsupported image format: {detected_format}. Allowed: JPEG, PNG, WEBP.")

        # Step 2: Fully reload and validate dimensions (mitigate decompression bombs)
        img_load = Image.open(io.BytesIO(file_bytes))
        width, height = img_load.size
        num_pixels = width * height

        if num_pixels > MAX_IMAGE_PIXELS or width > MAX_DIMENSION or height > MAX_DIMENSION:
            raise ImageSanitizationError(f"Image dimensions ({width}x{height}) exceed maximum allowed threshold.")

        # Step 3: Handle EXIF orientation then strip ALL metadata
        # Transposing applies rotation orientation, then we convert to pure RGB/RGBA without EXIF tags
        sanitized_img = ImageOps.exif_transpose(img_load)
        if sanitized_img.mode not in ("RGB", "RGBA", "L"):
            sanitized_img = sanitized_img.convert("RGB")

        # Step 4: Generate unique storage names
        unique_id = str(uuid.uuid4())
        ext = ".jpg" if detected_format.upper() == "JPEG" else f".{detected_format.lower()}"
        clean_filename = f"{unique_id}{ext}"
        thumb_filename = f"thumb_{unique_id}.jpg"

        file_path = os.path.join(upload_dir, clean_filename)
        thumb_path = os.path.join(upload_dir, "thumbnails", thumb_filename)

        # Step 5: Save sanitized primary image without any EXIF/metadata
        if sanitized_img.mode == "RGBA" and ext in [".jpg", ".jpeg"]:
            save_img = sanitized_img.convert("RGB")
        else:
            save_img = sanitized_img

        save_img.save(file_path, format=detected_format, quality=95)
        saved_file_size = os.path.getsize(file_path)

        # Step 6: Create square/aspect-preserved thumbnail
        thumbnail_img = save_img.copy()
        thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        if thumbnail_img.mode != "RGB":
            thumbnail_img = thumbnail_img.convert("RGB")
        thumbnail_img.save(thumb_path, format="JPEG", quality=85)

        # Step 7: Calculate perceptual hash (dHash)
        phash = calculate_dhash(sanitized_img)

        return {
            "id": unique_id,
            "filename": clean_filename,
            "original_name": original_filename,
            "file_path": file_path,
            "thumbnail_path": thumb_path,
            "mime_type": f"image/{detected_format.lower()}",
            "file_size_bytes": saved_file_size,
            "width": width,
            "height": height,
            "perceptual_hash": phash
        }

    except UnidentifiedImageError:
        raise ImageSanitizationError("Failed to decode image. File is corrupt or not a valid image format.")
    except Exception as e:
        if isinstance(e, ImageSanitizationError):
            raise
        raise ImageSanitizationError(f"Image sanitization failed: {str(e)}")
