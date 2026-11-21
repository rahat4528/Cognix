from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from recommendation_engine.ab_testing import ab_manager
from ...models.models import ABEvent
from ..deps import get_current_active_user
from ...models.models import User

router = APIRouter(prefix="/experiments", tags=["A/B Testing Experiments"])


@router.get("/")
def get_experiments():
    """Returns active A/B testing trials, assigned variants, and measured conversion metrics."""
    return ab_manager.get_experiment_summary("exp_homepage_algo")


@router.post("/record")
async def record_experiment_event(
    experiment_id: str = Query(...),
    variant_id: str = Query(...),
    event_type: str = Query(...),  # impression, click, conversion
    item_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ab_manager.record_event(experiment_id, variant_id, event_type)

    event = ABEvent(
        experiment_id=experiment_id,
        variant_id=variant_id,
        user_id=current_user.id,
        event_type=event_type,
        item_id=item_id
    )
    db.add(event)
    await db.commit()

    return {"status": "recorded", "experiment_id": experiment_id, "variant_id": variant_id, "event_type": event_type}
