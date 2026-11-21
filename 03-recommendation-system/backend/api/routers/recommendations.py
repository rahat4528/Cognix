import json
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...core.database import get_db
from ...models.models import User, Item, Interaction, UserPreference
from ...schemas.schemas import ItemResponse, RecommendationItem, ColdStartQuizRequest
from recommendation_engine.collaborative import MatrixFactorizationRecommender
from recommendation_engine.content_based import ContentBasedRecommender
from recommendation_engine.sequential import SequentialSessionRecommender
from recommendation_engine.hybrid import HybridEnsembleRecommender
from recommendation_engine.ab_testing import ab_manager
from ..deps import get_current_active_user

router = APIRouter(prefix="/recommendations", tags=["Personalized Recommendations"])

# In-memory singletons for recommendation models
cf_model = MatrixFactorizationRecommender(n_factors=15, random_state=42)
cb_model = ContentBasedRecommender(max_features=500)
seq_model = SequentialSessionRecommender(decay_factor=0.65)
hybrid_model = HybridEnsembleRecommender(cf_model, cb_model, seq_model)
models_initialized = False


async def ensure_models_trained(db: AsyncSession):
    global models_initialized
    if models_initialized:
        return

    # Load items
    items_res = await db.execute(select(Item))
    items = items_res.scalars().all()
    if not items:
        return

    items_df = pd.DataFrame([{
        'id': i.id,
        'title': i.title,
        'category': i.category,
        'tags': i.tags,
        'description': i.description
    } for i in items])
    cb_model.fit(items_df)

    # Load interactions
    inter_res = await db.execute(select(Interaction))
    interactions = inter_res.scalars().all()
    if interactions:
        inter_df = pd.DataFrame([{
            'user_id': it.user_id,
            'item_id': it.item_id,
            'weight': it.weight,
            'session_id': it.session_id or it.user_id,
            'timestamp': it.timestamp
        } for it in interactions])
        cf_model.fit(inter_df)
        seq_model.fit(inter_df)

    models_initialized = True


@router.get("/personalized", response_model=List[RecommendationItem])
async def get_personalized_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    session_id: Optional[str] = Query(None),
    apply_ab_test: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await ensure_models_trained(db)

    # A/B Testing routing
    assigned_variant = "variant_b"  # Default hybrid
    if apply_ab_test:
        assigned_variant = ab_manager.assign_variant(current_user.id, "exp_homepage_algo")
        ab_manager.record_event("exp_homepage_algo", assigned_variant, "impression")

    # Fetch user past interactions
    int_stmt = select(Interaction).where(Interaction.user_id == current_user.id).order_by(Interaction.timestamp.desc())
    int_res = await db.execute(int_stmt)
    user_ints = int_res.scalars().all()

    interaction_tuples = [(it.item_id, it.weight) for it in user_ints]
    recent_session_items = [it.item_id for it in user_ints if (session_id and it.session_id == session_id)][:5]

    # Cold-start preference check
    pref_stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    pref_res = await db.execute(pref_stmt)
    pref = pref_res.scalars().first()

    # Route based on A/B testing variant
    recommended_raw = []
    if assigned_variant == "control":
        # Popularity baseline
        pop_items = cf_model.item_popularity[:top_k]
        recommended_raw = [
            {"item_id": i, "hybrid_score": s, "model_contributions": {"popularity": 1.0}, "is_cold_start": len(interaction_tuples) < 3}
            for i, s in pop_items
        ]
    elif assigned_variant == "variant_a":
        # Pure Collaborative Filtering
        cf_items = cf_model.recommend_for_user(current_user.id, top_k=top_k)
        recommended_raw = [
            {"item_id": i, "hybrid_score": s, "model_contributions": {"cf": 1.0}, "is_cold_start": len(interaction_tuples) < 3}
            for i, s in cf_items
        ]
    else:
        # Variant B: Dynamic Hybrid Ensemble
        recommended_raw = hybrid_model.recommend(
            user_id=current_user.id,
            user_interactions=interaction_tuples,
            session_items=recent_session_items,
            top_k=top_k
        )

    # Hydrate items from database
    item_ids = [r["item_id"] for r in recommended_raw]
    items_stmt = select(Item).where(Item.id.in_(item_ids))
    items_map = {i.id: i for i in (await db.execute(items_stmt)).scalars().all()}

    output = []
    for r in recommended_raw:
        item_obj = items_map.get(r["item_id"])
        if item_obj:
            output.append({
                "item": item_obj,
                "score": r["hybrid_score"],
                "explanation": f"Matched by {assigned_variant} (Cold-start: {r.get('is_cold_start', False)})",
                "model_contributions": r.get("model_contributions", {}),
                "is_cold_start": r.get("is_cold_start", False)
            })

    return output


@router.get("/collaborative", response_model=List[RecommendationItem])
async def get_collaborative_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await ensure_models_trained(db)
    recs = cf_model.recommend_for_user(current_user.id, top_k=top_k)
    item_ids = [i for i, _ in recs]
    items_map = {i.id: i for i in (await db.execute(select(Item).where(Item.id.in_(item_ids)))).scalars().all()}

    return [
        {
            "item": items_map[i],
            "score": round(score, 4),
            "explanation": "Latent factor matrix decomposition alignment",
            "model_contributions": {"collaborative": 1.0},
            "is_cold_start": False
        }
        for i, score in recs if i in items_map
    ]


@router.get("/content-based", response_model=List[RecommendationItem])
async def get_content_based_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await ensure_models_trained(db)
    int_stmt = select(Interaction).where(Interaction.user_id == current_user.id)
    user_ints = [(it.item_id, it.weight) for it in (await db.execute(int_stmt)).scalars().all()]

    recs = cb_model.recommend_for_user(user_ints, top_k=top_k)
    item_ids = [i for i, _ in recs]
    items_map = {i.id: i for i in (await db.execute(select(Item).where(Item.id.in_(item_ids)))).scalars().all()}

    return [
        {
            "item": items_map[i],
            "score": round(score, 4),
            "explanation": "TF-IDF textual & categorical attribute cosine affinity",
            "model_contributions": {"content_based": 1.0},
            "is_cold_start": len(user_ints) < 3
        }
        for i, score in recs if i in items_map
    ]


@router.get("/sequential", response_model=List[RecommendationItem])
async def get_sequential_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await ensure_models_trained(db)
    int_stmt = select(Interaction).where(Interaction.user_id == current_user.id).order_by(Interaction.timestamp.desc()).limit(5)
    recent_items = [it.item_id for it in (await db.execute(int_stmt)).scalars().all()]

    recs = seq_model.predict_next_items(recent_items, top_k=top_k)
    item_ids = [i for i, _ in recs]
    items_map = {i.id: i for i in (await db.execute(select(Item).where(Item.id.in_(item_ids)))).scalars().all()}

    return [
        {
            "item": items_map[i],
            "score": round(score, 4),
            "explanation": "First-order Markov transition probability from recent browsing",
            "model_contributions": {"sequential": 1.0},
            "is_cold_start": len(recent_items) == 0
        }
        for i, score in recs if i in items_map
    ]


@router.get("/similar/{item_id}", response_model=List[RecommendationItem])
async def get_similar_items(
    item_id: str,
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    await ensure_models_trained(db)
    recs = cb_model.similar_items(item_id, top_k=top_k)
    item_ids = [i for i, _ in recs]
    items_map = {i.id: i for i in (await db.execute(select(Item).where(Item.id.in_(item_ids)))).scalars().all()}

    return [
        {
            "item": items_map[i],
            "score": round(score, 4),
            "explanation": "Direct item-item TF-IDF cosine similarity",
            "model_contributions": {"content_based": 1.0},
            "is_cold_start": False
        }
        for i, score in recs if i in items_map
    ]


@router.post("/onboard-quiz")
async def submit_cold_start_quiz(
    quiz_data: ColdStartQuizRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Upsert user preference
    pref_stmt = select(UserPreference).where(UserPreference.user_id == current_user.id)
    pref = (await db.execute(pref_stmt)).scalars().first()

    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            selected_categories_json=json.dumps(quiz_data.selected_categories),
            price_tier=quiz_data.price_tier,
            tech_affinity=quiz_data.tech_affinity
        )
        db.add(pref)
    else:
        pref.selected_categories_json = json.dumps(quiz_data.selected_categories)
        pref.price_tier = quiz_data.price_tier
        pref.tech_affinity = quiz_data.tech_affinity

    # Seed artificial warm-up interaction events for selected categories
    # to jumpstart collaborative and content based matching immediately
    cat_items = (await db.execute(
        select(Item).where(Item.category.in_(quiz_data.selected_categories)).limit(3)
    )).scalars().all()

    import time
    for item in cat_items:
        int_obj = Interaction(
            user_id=current_user.id,
            item_id=item.id,
            interaction_type="favorite",
            weight=3.0,
            session_id=f"quiz_{current_user.id}",
            timestamp=time.time()
        )
        db.add(int_obj)

    await db.commit()
    return {
        "status": "success",
        "message": "Preferences successfully recorded. Cold-start profiles initialized.",
        "categories_selected": quiz_data.selected_categories
    }
