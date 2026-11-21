# REST API Specification: Data Visualization Dashboard

All endpoints return JSON responses and require Bearer token authentication unless otherwise noted.

## 1. Authentication & Workspaces
- `POST /api/v1/auth/register` — Register a new user account.
- `POST /api/v1/auth/login` — Authenticate and obtain JWT access & refresh tokens.
- `GET /api/v1/auth/me` — Retrieve current user profile.
- `GET /api/v1/workspaces` — List workspaces accessible to user.
- `POST /api/v1/workspaces` — Create a new workspace.
- `GET /api/v1/workspaces/{id}/members` — List workspace members and roles.
- `POST /api/v1/workspaces/{id}/members` — Invite/add member to workspace.

## 2. Datasets & Ingestion
- `GET /api/v1/workspaces/{id}/datasets` — List workspace datasets.
- `POST /api/v1/workspaces/{id}/datasets/upload` — Upload raw dataset (multipart/form-data).
- `GET /api/v1/datasets/{id}` — Get dataset details and latest schema.
- `GET /api/v1/datasets/{id}/versions` — List historical dataset versions.
- `GET /api/v1/datasets/{id}/preview` — Retrieve paginated preview of data rows.
- `GET /api/v1/datasets/{id}/profile` — Retrieve comprehensive data profiling and quality report.
- `DELETE /api/v1/datasets/{id}` — Delete dataset and associated versions.

## 3. Data Transformations
- `POST /api/v1/datasets/{id}/transform/preview` — Test a set of transformation steps on a sample.
- `POST /api/v1/datasets/{id}/transform/apply` — Apply transformation pipeline, producing a new `DatasetVersion`.

## 4. Visualization & Charts
- `GET /api/v1/workspaces/{id}/charts` — List charts in workspace.
- `POST /api/v1/workspaces/{id}/charts` — Create a chart configuration.
- `GET /api/v1/charts/{id}` — Get chart details.
- `PUT /api/v1/charts/{id}` — Update chart configuration.
- `POST /api/v1/charts/{id}/query` — Execute server-side aggregation for the chart.
- `DELETE /api/v1/charts/{id}` — Remove a chart.

## 5. Dashboards
- `GET /api/v1/workspaces/{id}/dashboards` — List dashboards.
- `POST /api/v1/workspaces/{id}/dashboards` — Create a dashboard.
- `GET /api/v1/dashboards/{id}` — Get dashboard and embedded chart layouts.
- `PUT /api/v1/dashboards/{id}` — Update dashboard layout and global filters.
- `POST /api/v1/dashboards/{id}/duplicate` — Duplicate an existing dashboard.
- `POST /api/v1/dashboards/{id}/share` — Generate revocable public share link.
- `GET /api/v1/public/dashboards/{token}` — Retrieve public dashboard (read-only aggregated data).
- `POST /api/v1/dashboards/{id}/export/pdf` — Trigger server-side PDF export job.

## 6. Sandboxed SQL Workspace
- `POST /api/v1/workspaces/{id}/sql/execute` — Execute a validated read-only SQL query in DuckDB.
- `GET /api/v1/workspaces/{id}/sql/saved` — List saved queries.
- `POST /api/v1/workspaces/{id}/sql/saved` — Save a query.
- `GET /api/v1/workspaces/{id}/sql/history` — Get query execution history.

## 7. Machine Learning Analytics
- `POST /api/v1/workspaces/{id}/ml/experiments/import-metrics` — Ingest training/validation metrics.
- `POST /api/v1/workspaces/{id}/ml/experiments/import-predictions` — Ingest prediction outputs (true labels, predicted scores).
- `GET /api/v1/workspaces/{id}/ml/experiments` — List ML experiments.
- `GET /api/v1/ml/experiments/{id}/curves` — Retrieve loss/accuracy curves.
- `GET /api/v1/ml/experiments/{id}/evaluation` — Compute confusion matrix, ROC curve, and PR curve.
