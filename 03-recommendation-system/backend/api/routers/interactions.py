import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...core.database import get_db
from ...models.models import User, Item, Interaction
from ...schemas.schemas import InteractionCreate
from ..deps import get_current_active_user

router = APIRouter(prefix="/interactions", tags=["User Interactions"])

WEIGHT_MAP = {
    "click": 1.0,
    "favorite": 2.0,
    "add_to_cart": 3.0,
    "purchase": 5.0
}


@router.post("/")
async def record_interaction(
    interaction_in: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify item exists
    item_res = await db.execute(select(Item).where(Item.id == interaction_in.item_id))
    if not item_res.scalars().first():
        raise HTTPException(status_code=404, detail="Item not found")

    weight = WEIGHT_MAP.get(interaction_in.interaction_type, 1.0)
    current_timestamp = time.time()

    interaction = Interaction(
        user_id=current_user.id,
        item_id=interaction_in.item_id,
        interaction_type=interaction_in.interaction_type,
        weight=weight,
        session_id=interaction_in.session_id or f"sess_{current_user.id}",
        timestamp=current_timestamp
    )
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)

    return {
        "status": "success",
        "interaction_id": interaction.id,
        "item_id": interaction.item_id,
        "interaction_type": interaction.interaction_type,
        "weight": interaction.weight,
        "timestamp": interaction.timestamp
    }
