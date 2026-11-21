from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from models.models import (
    MLExperiment, ModelMetric, MLPrediction, WorkspaceMember, Role
)
from schemas.schemas import (
    MetricsImportRequest, PredictionsImportRequest, MLExperimentResponse,
    EvaluationMetricsResponse
)
from api.deps import get_current_user, get_current_workspace_member, require_role
from ml_analytics.engine import compute_ml_evaluation_metrics

router = APIRouter(tags=["ML Analytics"])

@router.get("/workspaces/{workspace_id}/ml/experiments", response_model=List[MLExperimentResponse])
async def list_ml_experiments(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MLExperiment).where(MLExperiment.workspace_id == workspace_id).order_by(desc(MLExperiment.created_at))
    experiments = (await db.execute(stmt)).scalars().all()
    
    resp_list = []
    for exp in experiments:
        resp = MLExperimentResponse.model_validate(exp)
        # count distinct runs
        runs_stmt = select(ModelMetric.run_id).where(ModelMetric.experiment_id == exp.id).distinct()
        runs = (await db.execute(runs_stmt)).scalars().all()
        resp.runs_count = len(runs)
        resp_list.append(resp)
    return resp_list

@router.post("/workspaces/{workspace_id}/ml/experiments/import-metrics", response_model=MLExperimentResponse, status_code=status.HTTP_201_CREATED)
async def import_experiment_metrics(
    workspace_id: str,
    req: MetricsImportRequest,
    member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN, Role.EDITOR])),
    db: AsyncSession = Depends(get_db)
):
    # Find or create experiment
    stmt = select(MLExperiment).where(
        MLExperiment.workspace_id == workspace_id,
        MLExperiment.name == req.experiment_name
    )
    exp = (await db.execute(stmt)).scalar_one_or_none()
    if not exp:
        exp = MLExperiment(
            workspace_id=workspace_id,
            created_by_id=member.user_id,
            name=req.experiment_name,
            framework=req.framework or "PyTorch"
        )
        db.add(exp)
        await db.flush()

    for m in req.metrics:
        metric = ModelMetric(
            experiment_id=exp.id,
            run_id=m.run_id,
            metric_name=m.metric_name,
            step=m.step,
            epoch=m.epoch,
            value=m.value
        )
        db.add(metric)

    await db.commit()
    await db.refresh(exp)
    return MLExperimentResponse.model_validate(exp)

@router.post("/workspaces/{workspace_id}/ml/experiments/import-predictions", response_model=EvaluationMetricsResponse, status_code=status.HTTP_201_CREATED)
async def import_experiment_predictions(
    workspace_id: str,
    req: PredictionsImportRequest,
    member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN, Role.EDITOR])),
    db: AsyncSession = Depends(get_db)
):
    # Find or create experiment
    stmt = select(MLExperiment).where(
        MLExperiment.workspace_id == workspace_id,
        MLExperiment.name == req.experiment_name
    )
    exp = (await db.execute(stmt)).scalar_one_or_none()
    if not exp:
        exp = MLExperiment(
            workspace_id=workspace_id,
            created_by_id=member.user_id,
            name=req.experiment_name,
            framework="PyTorch"
        )
        db.add(exp)
        await db.flush()

    # Compute genuine evaluation metrics with scikit-learn
    try:
        metrics = compute_ml_evaluation_metrics(
            true_labels=req.true_labels,
            predicted_labels=req.predicted_labels,
            predicted_scores=req.predicted_scores
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to calculate ML evaluation metrics: {str(e)}")

    prediction_record = MLPrediction(
        experiment_id=exp.id,
        run_id=req.run_id,
        split_name=req.split_name,
        true_labels=req.true_labels,
        predicted_labels=req.predicted_labels,
        predicted_scores=req.predicted_scores
    )
    db.add(prediction_record)
    await db.commit()

    return EvaluationMetricsResponse(
        experiment_id=exp.id,
        run_id=req.run_id,
        split_name=req.split_name,
        accuracy=metrics["accuracy"],
        precision_macro=metrics["precision_macro"],
        recall_macro=metrics["recall_macro"],
        f1_macro=metrics["f1_macro"],
        confusion_matrix=metrics["confusion_matrix"],
        roc_curve=metrics.get("roc_curve"),
        pr_curve=metrics.get("pr_curve"),
        provenance_note=metrics["provenance_note"]
    )

@router.get("/ml/experiments/{experiment_id}/curves")
async def get_experiment_curves(experiment_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ModelMetric).where(ModelMetric.experiment_id == experiment_id).order_by(ModelMetric.step)
    metrics = (await db.execute(stmt)).scalars().all()
    
    # Organize by run_id -> metric_name -> list of {step, value}
    curves: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for m in metrics:
        if m.run_id not in curves:
            curves[m.run_id] = {}
        if m.metric_name not in curves[m.run_id]:
            curves[m.run_id][m.metric_name] = []
        curves[m.run_id][m.metric_name].append({
            "step": m.step,
            "epoch": m.epoch,
            "value": m.value
        })

    return {
        "experiment_id": experiment_id,
        "curves": curves,
        "label": "imported metrics"
    }

@router.get("/ml/experiments/{experiment_id}/evaluation", response_model=List[EvaluationMetricsResponse])
async def get_experiment_evaluations(experiment_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(MLPrediction).where(MLPrediction.experiment_id == experiment_id).order_by(desc(MLPrediction.created_at))
    predictions = (await db.execute(stmt)).scalars().all()

    eval_list = []
    for p in predictions:
        metrics = compute_ml_evaluation_metrics(
            true_labels=p.true_labels,
            predicted_labels=p.predicted_labels,
            predicted_scores=p.predicted_scores
        )
        eval_list.append(EvaluationMetricsResponse(
            experiment_id=p.experiment_id,
            run_id=p.run_id,
            split_name=p.split_name,
            accuracy=metrics["accuracy"],
            precision_macro=metrics["precision_macro"],
            recall_macro=metrics["recall_macro"],
            f1_macro=metrics["f1_macro"],
            confusion_matrix=metrics["confusion_matrix"],
            roc_curve=metrics.get("roc_curve"),
            pr_curve=metrics.get("pr_curve"),
            provenance_note=metrics["provenance_note"]
        ))
    return eval_list
