import asyncio
import io
import json
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

# Ensure path resolution
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from backend.core.config import settings
from backend.core.database import AsyncSessionLocal, engine, Base
from backend.core.security import get_password_hash
from backend.models.models import (
    User,
    ImageAsset,
    ImageAnalysis,
    ClassificationResult,
    DetectionResult,
    AuditLog
)
from backend.preprocessing.image_sanitizer import sanitize_and_save_image
from inference.models.classifier import MobileNetClassifier
from inference.models.detector import SSDLiteDetector


def create_demo_image(name: str, color: tuple, shape: str) -> bytes:
    """Generates an authentic synthetic test image with crisp geometric content."""
    img = Image.new("RGB", (400, 400), color=color)
    draw = ImageDraw.Draw(img)

    if shape == "circle":
        draw.ellipse([80, 80, 320, 320], fill=(220, 60, 60), outline=(255, 255, 255), width=4)
    elif shape == "rectangle":
        draw.rectangle([100, 120, 300, 280], fill=(40, 160, 220), outline=(255, 255, 255), width=4)
    elif shape == "cross":
        draw.rectangle([170, 60, 230, 340], fill=(255, 200, 50))
        draw.rectangle([60, 170, 340, 230], fill=(255, 200, 50))
    else:
        # Complex multi-box composition
        draw.rectangle([50, 50, 180, 220], fill=(50, 180, 100))
        draw.ellipse([220, 180, 350, 310], fill=(180, 50, 180))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


async def seed():
    print("Initializing Cognix CV database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy.future import select
        res = await session.execute(select(User).where(User.email == "admin@cognix.local"))
        admin_user = res.scalars().first()

        if not admin_user:
            print("Creating default admin and researcher accounts...")
            admin_user = User(
                email="admin@cognix.local",
                hashed_password=get_password_hash("AdminPass123!"),
                role="admin"
            )
            researcher_user = User(
                email="researcher@cognix.local",
                hashed_password=get_password_hash("ResearcherPass123!"),
                role="researcher"
            )
            session.add_all([admin_user, researcher_user])
            await session.commit()
            await session.refresh(admin_user)
            print("Users created: admin@cognix.local, researcher@cognix.local")

        # Check existing images
        img_res = await session.execute(select(ImageAsset).where(ImageAsset.user_id == admin_user.id))
        existing_imgs = img_res.scalars().all()

        if len(existing_imgs) == 0:
            print("Generating and seeding synthetic CV benchmark image assets...")
            classifier = MobileNetClassifier()
            detector = SSDLiteDetector()

            demo_samples = [
                ("red_circle_target.jpg", (30, 30, 35), "circle"),
                ("cyan_rectangle_card.jpg", (25, 35, 45), "rectangle"),
                ("golden_cross_symbol.jpg", (45, 25, 35), "cross"),
                ("multi_object_canvas.jpg", (20, 20, 20), "multi")
            ]

            for original_name, bg_color, shape in demo_samples:
                img_bytes = create_demo_image(original_name, bg_color, shape)
                sanitized = sanitize_and_save_image(
                    file_bytes=img_bytes,
                    original_filename=original_name,
                    upload_dir=settings.UPLOAD_DIR
                )

                asset = ImageAsset(
                    id=sanitized["id"],
                    user_id=admin_user.id,
                    filename=sanitized["filename"],
                    original_name=sanitized["original_name"],
                    file_path=sanitized["file_path"],
                    thumbnail_path=sanitized["thumbnail_path"],
                    mime_type=sanitized["mime_type"],
                    file_size_bytes=sanitized["file_size_bytes"],
                    width=sanitized["width"],
                    height=sanitized["height"],
                    perceptual_hash=sanitized["perceptual_hash"]
                )
                session.add(asset)
                await session.flush()

                # Run authentic inference for classification
                pil_img = Image.open(io.BytesIO(img_bytes))
                cls_data = classifier.predict(pil_img, top_k=5)

                cls_analysis = ImageAnalysis(
                    image_id=asset.id,
                    user_id=admin_user.id,
                    task_type="classification",
                    model_name=cls_data["model_name"],
                    model_version=cls_data["model_version"],
                    latency_ms=cls_data["latency_ms"],
                    status="completed"
                )
                session.add(cls_analysis)
                await session.flush()

                cls_res = ClassificationResult(
                    analysis_id=cls_analysis.id,
                    top_label=cls_data["top_label"],
                    top_score=cls_data["top_score"],
                    is_uncertain=cls_data["is_uncertain"],
                    predictions_json=json.dumps(cls_data["top_predictions"]),
                    embedding_json=json.dumps(cls_data["embedding"])
                )
                session.add(cls_res)

                # Run authentic inference for object detection
                det_data = detector.detect(pil_img, score_threshold=0.20)
                det_analysis = ImageAnalysis(
                    image_id=asset.id,
                    user_id=admin_user.id,
                    task_type="detection",
                    model_name=det_data["model_name"],
                    model_version=det_data["model_version"],
                    latency_ms=det_data["latency_ms"],
                    status="completed"
                )
                session.add(det_analysis)
                await session.flush()

                det_res = DetectionResult(
                    analysis_id=det_analysis.id,
                    total_objects=det_data["total_objects_count"],
                    class_counts_json=json.dumps(det_data["class_counts"]),
                    detections_json=json.dumps(det_data["detected_objects"])
                )
                session.add(det_res)

            await session.commit()
            print("Successfully seeded 4 demo images with authentic predictions, embeddings, and detections!")
        else:
            print(f"Database already contains {len(existing_imgs)} images. Skipping demo generation.")


if __name__ == "__main__":
    asyncio.run(seed())
