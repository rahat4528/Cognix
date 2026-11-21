# Model Card: Matrix Factorization Collaborative Filtering (SVD)

## Model Overview
- **Name**: Truncated SVD Matrix Factorization Recommender
- **Task**: Collaborative Filtering & Latent Factor Rating Prediction
- **Version**: 1.0.0
- **Framework**: Scikit-learn / SciPy Sparse Matrix Linear Algebra
- **License**: BSD-3-Clause

## Mathematical Specification
Given a sparse User-Item interaction matrix $R \in \mathbb{R}^{m \times n}$ where $R_{u, i}$ represents the interaction weight (clicks=1, favorites=2, cart=3, purchases=5), Truncated SVD decomposes the centered matrix into:
$$R \approx U_k \Sigma_k V_k^T$$
where:
- $k = 20$ latent factors.
- $P = U_k \Sigma_k^{1/2}$ represents user latent factors $\in \mathbb{R}^{m \times k}$.
- $Q = V_k \Sigma_k^{1/2}$ represents item latent factors $\in \mathbb{R}^{n \times k}$.

Prediction score $\hat{R}_{u, i} = P_u \cdot Q_i^T + \mu_i + \mu_u$.

## Performance & Benchmarks
- **NDCG@10**: 0.412
- **Recall@10**: 0.384
- **Catalog Coverage**: 84.0%
- **Inference Latency**: 2.4 ms per user query.
