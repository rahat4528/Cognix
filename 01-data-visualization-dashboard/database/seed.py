import os
import sys
import asyncio
import json
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.database import AsyncSessionLocal, init_db
from core.security import hash_password
from core.config import settings
from models.models import (
    User, Workspace, WorkspaceMember, Role, Dataset, DatasetVersion,
    DatasetColumn, Chart, ChartType, Dashboard, DashboardChart,
    MLExperiment, ModelMetric, MLPrediction, SavedQuery
)
from data_processing.ingestion import save_dataframe_as_parquet, compute_sha256
from data_processing.profiling import profile_dataframe
from ml_analytics.engine import compute_ml_evaluation_metrics

async def seed():
    print("Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as db:
        print("Creating demo users...")
        # 1. Admin User
        admin_pass = hash_password("AdminPass123!")
        admin = User(
            email="admin@cognix.local",
            hashed_password=admin_pass,
            full_name="Cognix System Administrator",
            is_active=True,
            is_superuser=True
        )
        db.add(admin)

        # 2. Analyst User
        analyst_pass = hash_password("AnalystPass123!")
        analyst = User(
            email="analyst@cognix.local",
            hashed_password=analyst_pass,
            full_name="Sarah Chen (Lead Analyst)",
            is_active=True,
            is_superuser=False
        )
        db.add(analyst)
        await db.flush()

        print("Creating workspaces...")
        workspace = Workspace(
            name="Enterprise Analytics & ML",
            slug="enterprise-analytics-ml",
            description="Production analytics workspace for global metrics and model monitoring",
            owner_id=admin.id
        )
        db.add(workspace)
        await db.flush()

        # Add members
        db.add(WorkspaceMember(workspace_id=workspace.id, user_id=admin.id, role=Role.OWNER))
        db.add(WorkspaceMember(workspace_id=workspace.id, user_id=analyst.id, role=Role.ADMIN))
        await db.flush()

        print("Generating realistic demo dataset: Global Sales & Profitability...")
        # Generate 1,000 realistic sales transaction records
        np.random.seed(42)
        n_rows = 1000
        regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"]
        categories = ["Cloud Infrastructure", "Enterprise AI Tools", "Consulting & Support", "Hardware Appliances"]
        segments = ["Corporate", "Enterprise", "SMB", "Government"]
        
        start_date = pd.Timestamp("2025-01-01")
        dates = [start_date + pd.Timedelta(days=int(d)) for d in np.random.randint(0, 365, size=n_rows)]
        chosen_regions = np.random.choice(regions, size=n_rows, p=[0.35, 0.25, 0.20, 0.12, 0.08])
        chosen_categories = np.random.choice(categories, size=n_rows, p=[0.40, 0.30, 0.18, 0.12])
        chosen_segments = np.random.choice(segments, size=n_rows, p=[0.45, 0.30, 0.15, 0.10])
        units = np.random.randint(1, 50, size=n_rows)
        base_unit_price = np.random.uniform(500, 5000, size=n_rows)
        revenue = np.round(units * base_unit_price, 2)
        cost = np.round(revenue * np.random.uniform(0.35, 0.65, size=n_rows), 2)
        profit = np.round(revenue - cost, 2)
        margin = np.round((profit / revenue) * 100, 2)

        sales_df = pd.DataFrame({
            "order_id": [f"ORD-{2025000 + i}" for i in range(n_rows)],
            "transaction_date": [d.strftime("%Y-%m-%d") for d in dates],
            "region": chosen_regions,
            "product_category": chosen_categories,
            "customer_segment": chosen_segments,
            "units_sold": units,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "profit_margin_pct": margin
        })

        # Save sales dataset
        sales_ds = Dataset(
            workspace_id=workspace.id,
            created_by_id=admin.id,
            name="Global Enterprise Sales 2025",
            description="Annual worldwide sales transactions with segmented profit margins."
        )
        db.add(sales_ds)
        await db.flush()

        sales_cols_prof, sales_report, sales_score = profile_dataframe(sales_df)
        sales_v_id = f"ds_{sales_ds.id[:8]}_v1"
        sales_path, sales_bytes = save_dataframe_as_parquet(sales_df, settings.STORAGE_LOCAL_PATH, sales_v_id)
        with open(sales_path, "rb") as f:
            sales_hash = compute_sha256(f.read())

        sales_ver = DatasetVersion(
            id=sales_v_id,
            dataset_id=sales_ds.id,
            version_number=1,
            file_path=sales_path,
            original_filename="global_enterprise_sales_2025.csv",
            file_format="csv",
            file_size_bytes=sales_bytes,
            row_count=n_rows,
            column_count=len(sales_df.columns),
            checksum_sha256=sales_hash,
            quality_score=sales_score,
            quality_report=sales_report,
            created_by_id=admin.id
        )
        db.add(sales_ver)
        await db.flush()

        for cp in sales_cols_prof:
            db.add(DatasetColumn(
                dataset_version_id=sales_ver.id,
                name=cp["name"],
                data_type=cp["data_type"],
                is_nullable=cp["is_nullable"],
                null_count=cp["null_count"],
                null_percentage=cp["null_percentage"],
                unique_count=cp["unique_count"],
                sample_values=cp["sample_values"],
                statistics=cp["statistics"]
            ))

        print("Creating prebuilt analytical charts...")
        # Chart 1: Revenue by Region (Bar)
        chart_bar = Chart(
            workspace_id=workspace.id,
            dataset_id=sales_ds.id,
            dataset_version_id=sales_ver.id,
            created_by_id=admin.id,
            name="Total Revenue by Geographic Region",
            description="Aggregated revenue by major global sales regions.",
            chart_type=ChartType.BAR,
            config={
                "x_axis": "region",
                "y_axis": "revenue",
                "aggregation": "sum",
                "sort_order": "desc",
                "limit": 10
            }
        )
        db.add(chart_bar)

        # Chart 2: Revenue vs Profit (Scatter)
        chart_scatter = Chart(
            workspace_id=workspace.id,
            dataset_id=sales_ds.id,
            dataset_version_id=sales_ver.id,
            created_by_id=admin.id,
            name="Revenue vs Profit Distribution",
            description="Correlation analysis between transaction revenue and net profit.",
            chart_type=ChartType.SCATTER,
            config={
                "x_axis": "revenue",
                "y_axis": "profit",
                "limit": 1000
            }
        )
        db.add(chart_scatter)

        # Chart 3: Product Category Breakdown (Donut)
        chart_donut = Chart(
            workspace_id=workspace.id,
            dataset_id=sales_ds.id,
            dataset_version_id=sales_ver.id,
            created_by_id=admin.id,
            name="Revenue Share by Product Category",
            description="Proportion of total gross revenue by offering.",
            chart_type=ChartType.DONUT,
            config={
                "x_axis": "product_category",
                "y_axis": "revenue",
                "aggregation": "sum"
            }
        )
        db.add(chart_donut)

        # Chart 4: Profit Margin Box Plot (Box Plot)
        chart_box = Chart(
            workspace_id=workspace.id,
            dataset_id=sales_ds.id,
            dataset_version_id=sales_ver.id,
            created_by_id=admin.id,
            name="Profit Margin Distribution by Customer Segment",
            description="Quartiles and median margins per customer tier.",
            chart_type=ChartType.BOX_PLOT,
            config={
                "x_axis": "customer_segment",
                "y_axis": "profit_margin_pct"
            }
        )
        db.add(chart_box)
        await db.flush()

        print("Creating dashboard...")
        dashboard = Dashboard(
            workspace_id=workspace.id,
            created_by_id=admin.id,
            title="Executive Revenue & Margin Dashboard",
            description="High-level financial performance and category contribution overview.",
            version=1,
            is_public=True,
            global_filters=[
                {"column": "region", "operator": "in", "value": []}
            ]
        )
        db.add(dashboard)
        await db.flush()

        # Add charts to dashboard in a 2x2 grid
        db.add(DashboardChart(dashboard_id=dashboard.id, chart_id=chart_bar.id, position_x=0, position_y=0, width=6, height=4))
        db.add(DashboardChart(dashboard_id=dashboard.id, chart_id=chart_donut.id, position_x=6, position_y=0, width=6, height=4))
        db.add(DashboardChart(dashboard_id=dashboard.id, chart_id=chart_scatter.id, position_x=0, position_y=4, width=6, height=4))
        db.add(DashboardChart(dashboard_id=dashboard.id, chart_id=chart_box.id, position_x=6, position_y=4, width=6, height=4))

        print("Seeding saved analytical SQL queries...")
        saved_q = SavedQuery(
            workspace_id=workspace.id,
            created_by_id=admin.id,
            name="Top Margin Deals",
            description="High-profit transactions with margin exceeding 50%",
            sql_text="SELECT order_id, region, product_category, revenue, profit, profit_margin_pct FROM ds_global_enterprise_sales_2025 WHERE profit_margin_pct > 50.0 ORDER BY profit DESC LIMIT 100;"
        )
        db.add(saved_q)

        print("Seeding Machine Learning Experiment Analytics...")
        ml_exp = MLExperiment(
            workspace_id=workspace.id,
            created_by_id=analyst.id,
            name="Customer Churn Prediction Neural Net",
            description="Deep MLP benchmark comparing AdamW vs SGD optimizer performance.",
            framework="PyTorch"
        )
        db.add(ml_exp)
        await db.flush()

        # Metrics for Run-1 (AdamW)
        for ep in range(1, 21):
            train_loss = float(0.85 * np.exp(-0.15 * ep) + 0.08 + np.random.normal(0, 0.01))
            val_loss = float(0.88 * np.exp(-0.13 * ep) + 0.12 + np.random.normal(0, 0.012))
            train_acc = float(0.55 + 0.40 * (1 - np.exp(-0.18 * ep)))
            val_acc = float(0.53 + 0.38 * (1 - np.exp(-0.15 * ep)))

            db.add(ModelMetric(experiment_id=ml_exp.id, run_id="run_adamw_opt", metric_name="train_loss", step=ep, epoch=ep, value=round(train_loss, 4)))
            db.add(ModelMetric(experiment_id=ml_exp.id, run_id="run_adamw_opt", metric_name="val_loss", step=ep, epoch=ep, value=round(val_loss, 4)))
            db.add(ModelMetric(experiment_id=ml_exp.id, run_id="run_adamw_opt", metric_name="train_accuracy", step=ep, epoch=ep, value=round(train_acc, 4)))
            db.add(ModelMetric(experiment_id=ml_exp.id, run_id="run_adamw_opt", metric_name="val_accuracy", step=ep, epoch=ep, value=round(val_acc, 4)))

        # Predictions for Run-1 test set (300 test samples)
        y_true_sim = np.random.choice([0, 1], size=300, p=[0.75, 0.25]).tolist()
        # Simulated scores correlated with true label
        y_scores_sim = []
        y_pred_sim = []
        for yt in y_true_sim:
            score = float(np.clip(np.random.normal(0.78 if yt == 1 else 0.22, 0.18), 0.01, 0.99))
            y_scores_sim.append(round(score, 4))
            y_pred_sim.append(1 if score >= 0.5 else 0)

        db.add(MLPrediction(
            experiment_id=ml_exp.id,
            run_id="run_adamw_opt",
            split_name="test_holdout",
            true_labels=y_true_sim,
            predicted_labels=y_pred_sim,
            predicted_scores=y_scores_sim
        ))

        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
