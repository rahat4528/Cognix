# Recommendation System: REST API Reference

All endpoints are hosted under `/api/v1` on port 8002.

## Authentication & Profiles
- `POST /api/v1/auth/register`: Create user account.
- `POST /api/v1/auth/token`: OAuth2 password token exchange.
- `GET /api/v1/auth/me`: Current user session and role.

## Catalog & Interactions
- `GET /api/v1/items/`: List catalog items with category filters and pagination.
- `GET /api/v1/items/{item_id}`: Get item metadata, specifications, and related items.
- `POST /api/v1/interactions/`: Log user events (`click`, `favorite`, `add_to_cart`, `purchase`).

## Recommendation Endpoints
- `GET /api/v1/recommendations/personalized`: Hybrid recommendations for authenticated user.
- `GET /api/v1/recommendations/collaborative`: Pure matrix factorization recommendations.
- `GET /api/v1/recommendations/content-based`: Content similarity recommendations based on profile.
- `GET /api/v1/recommendations/sequential`: Next-item session transition recommendations based on recent sequence.
- `POST /api/v1/recommendations/onboard-quiz`: Cold-start onboarding quiz submission to initialize preferences.

## Evaluation & A/B Testing
- `GET /api/v1/evaluation/benchmarks`: Offline evaluation metrics (NDCG@K, Recall@K, MAP@K, Coverage).
- `GET /api/v1/experiments/`: List active A/B test experiments, variants, and CTR metrics.
- `POST /api/v1/experiments/{experiment_id}/event`: Record impression or conversion event.
