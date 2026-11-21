import json
import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...core.database import get_db
from ...core.config import settings
from ...models.models import (
    User,
    ImageAsset,
    ImageAnalysis,
    ClassificationResult,
    DetectionResult,
    ExplainabilityResult,
    AuditLog
)
from ...services.inference_client import inference_client
from ..deps import get_current_active_user

router = APIRouter(prefix="/inference", tags=["Inference Operations"])


@router.post("/classify/{image_id}")
async def run_classification(
    image_id: str,
    top_k: int = Query(5, ge=1, le=20),
    uncertainty_threshold: float = Query(0.20, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Retrieve image
    query = select(ImageAsset).where(
        ImageAsset.id == image_id,
        ImageAsset.user_id == current_user.id,
        ImageAsset.is_deleted == False
    )
    res = await db.execute(query)
    asset = res.scalars().first()
    if not asset or not os.path.exists(asset.file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    async with aiofiles.open(asset.file_path, "rb") as f:
        image_bytes = await f.read()

    # Call inference microservice (or in-process fallback)
    inf_res = await inference_client.classify_image(
        image_bytes=image_bytes,
        filename=asset.filename,
        top_k=top_k,
        uncertainty_threshold=uncertainty_threshold
    )

    # Persist Analysis and Results
    analysis = ImageAnalysis(
        image_id=asset.id,
        user_id=current_user.id,
        task_type="classification",
        model_name=inf_res.get("model_name", "MobileNetV3-Small"),
        model_version=inf_res.get("model_version", "1.0.0"),
        latency_ms=inf_res.get("latency_ms", 0.0),
        status="completed"
    )
    db.add(analysis)
    await db.flush()

    cls_result = ClassificationResult(
        analysis_id=analysis.id,
        top_label=inf_res["top_label"],
        top_score=inf_res["top_score"],
        is_uncertain=inf_res["is_uncertain"],
        predictions_json=json.dumps(inf_res["top_predictions"]),
        embedding_json=json.dumps(inf_res.get("embedding", []))
    )
    db.add(cls_result)

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="run_classification",
        resource_type="image_analysis",
        resource_id=analysis.id,
        details_json=json.dumps({"top_label": inf_res["top_label"], "score": inf_res["top_score"]})
    )
    db.add(audit)
    await db.commit()

    return {
        "analysis_id": analysis.id,
        "image_id": asset.id,
        "model_name": analysis.model_name,
        "model_version": analysis.model_version,
        "top_label": cls_result.top_label,
        "top_score": cls_result.top_score,
        "is_uncertain": cls_result.is_uncertain,
        "predictions": inf_res["top_predictions"],
        "embedding": inf_res.get("embedding", []),
        "latency_ms": analysis.latency_ms
    }


@router.post("/detect/{image_id}")
async def run_detection(
    image_id: str,
    score_threshold: float = Query(0.30, ge=0.05, le=0.99),
    nms_threshold: float = Query(0.45, ge=0.05, le=0.99),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(ImageAsset).where(
        ImageAsset.id == image_id,
        ImageAsset.user_id == current_user.id,
        ImageAsset.is_deleted == False
    )
    res = await db.execute(query)
    asset = res.scalars().first()
    if not asset or not os.path.exists(asset.file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    async with aiofiles.open(asset.file_path, "rb") as f:
        image_bytes = await f.read()

    inf_res = await inference_client.detect_objects(
        image_bytes=image_bytes,
        filename=asset.filename,
        score_threshold=score_threshold,
        nms_threshold=nms_threshold
    )

    analysis = ImageAnalysis(
        image_id=asset.id,
        user_id=current_user.id,
        task_type="detection",
        model_name=inf_res.get("model_name", "SSDLite320-MobileNetV3-Large"),
        model_version=inf_res.get("model_version", "1.0.0"),
        latency_ms=inf_res.get("latency_ms", 0.0),
        status="completed"
    )
    db.add(analysis)
    await db.flush()

    det_result = DetectionResult(
        analysis_id=analysis.id,
        total_objects=inf_res["total_objects_count"],
        class_counts_json=json.dumps(inf_res["class_counts"]),
        detections_json=json.dumps(inf_res["detected_objects"])
    )
    db.add(det_result)

    audit = AuditLog(
        user_id=current_user.id,
        action="run_detection",
        resource_type="image_analysis",
        resource_id=analysis.id,
        details_json=json.dumps({"total_objects": inf_res["total_objects_count"]})
    )
    db.add(audit)
    await db.commit()

    return {
        "analysis_id": analysis.id,
        "image_id": asset.id,
        "model_name": analysis.model_name,
        "model_version": analysis.model_version,
        "total_objects": det_result.total_objects,
        "class_counts": inf_res["class_counts"],
        "detections": inf_res["detected_objects"],
        "latency_ms": analysis.latency_ms
    }


@router.post("/explain/{image_id}")
async def run_explainability(
    image_id: str,
    target_class_id: int = Query(None),
    alpha: float = Query(0.5, ge=0.1, le=0.9),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(ImageAsset).where(
        ImageAsset.id == image_id,
        ImageAsset.user_id == current_user.id,
        ImageAsset.is_deleted == False
    )
    res = await db.execute(query)
    asset = res.scalars().first()
    if not asset or not os.path.exists(asset.file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    async with aiofiles.open(asset.file_path, "rb") as f:
        image_bytes = await f.read()

    inf_res = await inference_client.explain_classification(
        image_bytes=image_bytes,
        filename=asset.filename,
        target_class_id=target_class_id,
        alpha=alpha
    )

    analysis = ImageAnalysis(
        image_id=asset.id,
        user_id=current_user.id,
        task_type="explainability",
        model_name=inf_res.get("model_name", "MobileNetV3-Small-GradCAM"),
        model_version="1.0.0",
        latency_ms=inf_res.get("latency_ms", 0.0),
        status="completed"
    )
    db.add(analysis)
    await db.flush()

    # Save heatmap overlay to disk
    heatmap_filename = f"cam_{analysis.id}.jpg"
    heatmap_path = os.path.join(settings.UPLOAD_DIR, "heatmaps", heatmap_filename)
    # The returned data is a data URL: data:image/jpeg;base64,...
    header, encoded = inf_res["heatmap_base64"].split(",", 1)
    import base64
    heatmap_bytes = base64.b64decode(encoded)
    async with aiofiles.open(heatmap_path, "wb") as f_out:
        await f_out.write(heatmap_bytes)

    exp_result = ExplainabilityResult(
        analysis_id=analysis.id,
        target_class_id=inf_res["target_class_id"],
        target_label=inf_res["target_label"],
        confidence=inf_res["confidence"],
        heatmap_path=heatmap_path,
        disclaimer=inf_res.get("disclaimer", "approximate explanation")
    )
    db.add(exp_result)
    await db.commit()

    return {
        "analysis_id": analysis.id,
        "image_id": asset.id,
        "model_name": analysis.model_name,
        "target_class_id": exp_result.target_class_id,
        "target_label": exp_result.target_label,
        "confidence": exp_result.confidence,
        "heatmap_data_url": inf_res["heatmap_base64"],
        "disclaimer": exp_result.disclaimer,
        "latency_ms": analysis.latency_ms
    }


@router.post("/live-frame")
async def process_live_frame(
    file: UploadFile = File(...),
    score_threshold: float = Query(0.35, ge=0.1, le=0.95),
    _user: User = Depends(get_current_active_user)
):
    """
    Real-time lightweight frame processing for webcam feeds.
    Does not write frames to disk or record persistent assets to protect privacy.
    """
    contents = await file.read()
    return await inference_client.live_frame(contents, score_threshold=score_threshold)
