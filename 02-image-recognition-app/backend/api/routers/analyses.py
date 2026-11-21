import json
from typing import List
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ...core.database import get_db
from ...models.models import (
    User,
    ImageAsset,
    ImageAnalysis,
    ClassificationResult,
    DetectionResult,
    ExplainabilityResult
)
from ..deps import get_current_active_user

router = APIRouter(prefix="/analyses", tags=["Analysis History & Search"])


@router.get("/history")
async def get_analysis_history(
    task_type: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = (
        select(ImageAnalysis)
        .options(
            selectinload(ImageAnalysis.image),
            selectinload(ImageAnalysis.classification),
            selectinload(ImageAnalysis.detection),
            selectinload(ImageAnalysis.explainability)
        )
        .where(ImageAnalysis.user_id == current_user.id)
    )
    if task_type:
        query = query.where(ImageAnalysis.task_type == task_type)

    query = query.order_by(ImageAnalysis.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    analyses = result.scalars().all()

    output = []
    for a in analyses:
        item = {
            "id": a.id,
            "image_id": a.image_id,
            "original_name": a.image.original_name if a.image else "Deleted Image",
            "thumbnail_url": f"/api/v1/images/{a.image_id}/thumbnail" if a.image else None,
            "task_type": a.task_type,
            "model_name": a.model_name,
            "model_version": a.model_version,
            "latency_ms": a.latency_ms,
            "status": a.status,
            "created_at": a.created_at,
            "result_summary": None
        }
        if a.classification:
            item["result_summary"] = {
                "top_label": a.classification.top_label,
                "top_score": a.classification.top_score,
                "is_uncertain": a.classification.is_uncertain
            }
        elif a.detection:
            item["result_summary"] = {
                "total_objects": a.detection.total_objects,
                "class_counts": json.loads(a.detection.class_counts_json)
            }
        elif a.explainability:
            item["result_summary"] = {
                "target_label": a.explainability.target_label,
                "confidence": a.explainability.confidence,
                "disclaimer": a.explainability.disclaimer
            }
        output.append(item)

    return output


@router.get("/{analysis_id}")
async def get_analysis_detail(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = (
        select(ImageAnalysis)
        .options(
            selectinload(ImageAnalysis.image),
            selectinload(ImageAnalysis.classification),
            selectinload(ImageAnalysis.detection),
            selectinload(ImageAnalysis.explainability)
        )
        .where(ImageAnalysis.id == analysis_id, ImageAnalysis.user_id == current_user.id)
    )
    res = await db.execute(query)
    analysis = res.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    detail = {
        "id": analysis.id,
        "image_id": analysis.image_id,
        "task_type": analysis.task_type,
        "model_name": analysis.model_name,
        "latency_ms": analysis.latency_ms,
        "created_at": analysis.created_at,
        "image_url": f"/api/v1/images/{analysis.image_id}/file",
        "thumbnail_url": f"/api/v1/images/{analysis.image_id}/thumbnail",
    }
    if analysis.classification:
        detail["classification"] = {
            "top_label": analysis.classification.top_label,
            "top_score": analysis.classification.top_score,
            "is_uncertain": analysis.classification.is_uncertain,
            "predictions": json.loads(analysis.classification.predictions_json)
        }
    elif analysis.detection:
        detail["detection"] = {
            "total_objects": analysis.detection.total_objects,
            "class_counts": json.loads(analysis.detection.class_counts_json),
            "detections": json.loads(analysis.detection.detections_json)
        }
    elif analysis.explainability:
        detail["explainability"] = {
            "target_label": analysis.explainability.target_label,
            "confidence": analysis.explainability.confidence,
            "disclaimer": analysis.explainability.disclaimer
        }

    return detail


@router.post("/similarity-search/{image_id}")
async def visual_similarity_search(
    image_id: str,
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Computes exact cosine similarity against all stored image embeddings for the user.
    Uses reproducible, genuine mathematical dot-product similarity.
    """
    # 1. Fetch query image classification result
    query_stmt = (
        select(ClassificationResult)
        .join(ImageAnalysis, ClassificationResult.analysis_id == ImageAnalysis.id)
        .where(ImageAnalysis.image_id == image_id, ImageAnalysis.user_id == current_user.id)
        .order_by(ClassificationResult.created_at.desc())
    )
    res = await db.execute(query_stmt)
    query_cls = res.scalars().first()
    if not query_cls or not query_cls.embedding_json:
        raise HTTPException(
            status_code=400,
            detail="Query image has not been classified or has no embedding. Run classification first."
        )

    target_vector = np.array(json.loads(query_cls.embedding_json), dtype=np.float32)
    target_norm = np.linalg.norm(target_vector)
    if target_norm == 0:
        raise HTTPException(status_code=400, detail="Invalid embedding vector.")

    # 2. Fetch all other image classifications for this user
    all_stmt = (
        select(ClassificationResult, ImageAsset)
        .join(ImageAnalysis, ClassificationResult.analysis_id == ImageAnalysis.id)
        .join(ImageAsset, ImageAnalysis.image_id == ImageAsset.id)
        .where(
            ImageAsset.user_id == current_user.id,
            ImageAsset.id != image_id,
            ImageAsset.is_deleted == False
        )
    )
    all_res = await db.execute(all_stmt)
    candidates = all_res.all()

    matches = []
    seen_images = set()

    for cls_row, asset_row in candidates:
        if asset_row.id in seen_images or not cls_row.embedding_json:
            continue
        seen_images.add(asset_row.id)

        candidate_vec = np.array(json.loads(cls_row.embedding_json), dtype=np.float32)
        cand_norm = np.linalg.norm(candidate_vec)
        if cand_norm == 0:
            continue

        # Cosine similarity: (A . B) / (||A|| * ||B||)
        cosine_sim = float(np.dot(target_vector, candidate_vec) / (target_norm * cand_norm))
        # Clip to [-1.0, 1.0] and scale to [0, 1] for presentation
        scaled_sim = round(max(0.0, min(1.0, (cosine_sim + 1.0) / 2.0)), 4)

        matches.append({
            "image_id": asset_row.id,
            "original_name": asset_row.original_name,
            "thumbnail_url": f"/api/v1/images/{asset_row.id}/thumbnail",
            "similarity_score": scaled_sim,
            "top_label": cls_row.top_label
        })

    # Sort descending by similarity score
    matches.sort(key=lambda m: m["similarity_score"], reverse=True)
    top_matches = matches[:top_k]

    return {
        "query_image_id": image_id,
        "total_candidates": len(matches),
        "matches": top_matches
    }
