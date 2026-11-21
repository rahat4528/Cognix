import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...core.config import settings
from ...core.database import get_db
from ...models.models import User, ImageAsset, AuditLog
from ...preprocessing.image_sanitizer import sanitize_and_save_image, ImageSanitizationError
from ..deps import get_current_active_user

router = APIRouter(prefix="/images", tags=["Image Assets"])


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
        )

    try:
        sanitized = sanitize_and_save_image(
            file_bytes=contents,
            original_filename=file.filename or "uploaded_image.jpg",
            upload_dir=settings.UPLOAD_DIR
        )
    except ImageSanitizationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Persist Image Asset in Database
    asset = ImageAsset(
        id=sanitized["id"],
        user_id=current_user.id,
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
    db.add(asset)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="upload_image",
        resource_type="image_asset",
        resource_id=asset.id,
        details_json=f'{{"original_name": "{asset.original_name}", "width": {asset.width}, "height": {asset.height}}}'
    )
    db.add(audit)
    await db.commit()
    await db.refresh(asset)

    return {
        "id": asset.id,
        "filename": asset.filename,
        "original_name": asset.original_name,
        "mime_type": asset.mime_type,
        "file_size_bytes": asset.file_size_bytes,
        "width": asset.width,
        "height": asset.height,
        "perceptual_hash": asset.perceptual_hash,
        "thumbnail_url": f"/api/v1/images/{asset.id}/thumbnail",
        "image_url": f"/api/v1/images/{asset.id}/file",
        "created_at": asset.created_at
    }


@router.get("/")
async def list_images(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = (
        select(ImageAsset)
        .where(ImageAsset.user_id == current_user.id, ImageAsset.is_deleted == False)
        .order_by(ImageAsset.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    assets = result.scalars().all()

    return [
        {
            "id": a.id,
            "filename": a.filename,
            "original_name": a.original_name,
            "mime_type": a.mime_type,
            "file_size_bytes": a.file_size_bytes,
            "width": a.width,
            "height": a.height,
            "perceptual_hash": a.perceptual_hash,
            "thumbnail_url": f"/api/v1/images/{a.id}/thumbnail",
            "image_url": f"/api/v1/images/{a.id}/file",
            "created_at": a.created_at
        }
        for a in assets
    ]


@router.get("/{image_id}")
async def get_image_details(
    image_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(ImageAsset).where(
        ImageAsset.id == image_id,
        ImageAsset.user_id == current_user.id,
        ImageAsset.is_deleted == False
    )
    result = await db.execute(query)
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "id": asset.id,
        "filename": asset.filename,
        "original_name": asset.original_name,
        "mime_type": asset.mime_type,
        "file_size_bytes": asset.file_size_bytes,
        "width": asset.width,
        "height": asset.height,
        "perceptual_hash": asset.perceptual_hash,
        "thumbnail_url": f"/api/v1/images/{asset.id}/thumbnail",
        "image_url": f"/api/v1/images/{asset.id}/file",
        "created_at": asset.created_at
    }


@router.get("/{image_id}/file")
async def get_image_file(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    query = select(ImageAsset).where(ImageAsset.id == image_id, ImageAsset.is_deleted == False)
    result = await db.execute(query)
    asset = result.scalars().first()
    if not asset or not os.path.exists(asset.file_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(asset.file_path, media_type=asset.mime_type)


@router.get("/{image_id}/thumbnail")
async def get_thumbnail_file(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    query = select(ImageAsset).where(ImageAsset.id == image_id, ImageAsset.is_deleted == False)
    result = await db.execute(query)
    asset = result.scalars().first()
    if not asset or not os.path.exists(asset.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(asset.thumbnail_path, media_type="image/jpeg")


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cascading privacy deletion:
    Permanently unlinks database records and destroys raw image file, thumbnail, and derived data.
    """
    query = select(ImageAsset).where(
        ImageAsset.id == image_id,
        ImageAsset.user_id == current_user.id
    )
    result = await db.execute(query)
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Image not found")

    # Clean up physical files from disk
    if os.path.exists(asset.file_path):
        try:
            os.remove(asset.file_path)
        except OSError:
            pass

    if os.path.exists(asset.thumbnail_path):
        try:
            os.remove(asset.thumbnail_path)
        except OSError:
            pass

    # Record privacy audit
    audit = AuditLog(
        user_id=current_user.id,
        action="delete_image_cascade",
        resource_type="image_asset",
        resource_id=asset.id,
        details_json=f'{{"original_name": "{asset.original_name}", "privacy_deleted": true}}'
    )
    db.add(audit)

    # Delete record (cascading deletes child analyses and classification results)
    await db.delete(asset)
    await db.commit()

    return {"message": "Image and all associated records permanently deleted.", "id": image_id}
