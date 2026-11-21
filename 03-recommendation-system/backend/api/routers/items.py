from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...core.database import get_db
from ...models.models import Item
from ...schemas.schemas import ItemResponse

router = APIRouter(prefix="/items", tags=["Catalog Items"])


@router.get("/", response_model=List[ItemResponse])
async def list_items(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Item)
    if category:
        query = query.where(Item.category == category)
    if search:
        query = query.where(Item.title.ilike(f"%{search}%") | Item.description.ilike(f"%{search}%"))

    query = query.order_by(Item.rating.desc()).offset(offset).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Item.category).distinct())
    return [row[0] for row in res.all()]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Item).where(Item.id == item_id))
    item = res.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
