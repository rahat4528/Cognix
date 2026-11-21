import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import pandas as pd

from ...core.database import get_db
from ...models.models import Item, Interaction
from model_training.train import train_and_evaluate_all

router = APIRouter(prefix="/evaluation", tags=["Offline Evaluation & Benchmarks"])


@router.get("/benchmarks")
async def get_offline_benchmarks(db: AsyncSession = Depends(get_db)):
    """
    Returns authentic offline benchmark evaluation metrics computed across
    strict temporal train/validation/test partitions.
    """
    results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "model_evaluation", "benchmark_results.json"))
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            return json.load(f)

    # If benchmark results file not yet generated, compute from DB
    items = (await db.execute(select(Item))).scalars().all()
    interactions = (await db.execute(select(Interaction))).scalars().all()

    if not items or not interactions:
        return {"status": "no_data", "message": "Catalog and interactions must be seeded first."}

    items_df = pd.DataFrame([{
        'id': i.id, 'title': i.title, 'category': i.category,
        'tags': i.tags, 'description': i.description
    } for i in items])

    interactions_df = pd.DataFrame([{
        'user_id': it.user_id, 'item_id': it.item_id, 'weight': it.weight,
        'session_id': it.session_id or it.user_id, 'timestamp': it.timestamp
    } for it in interactions])

    eval_dir = os.path.dirname(results_path)
    summary = train_and_evaluate_all(items_df, interactions_df, output_dir=eval_dir)
    return summary
