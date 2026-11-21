# Model Card: Hybrid Ensemble Recommender

## Model Overview
- **Name**: Dynamic Multi-Signal Hybrid Ranker
- **Task**: Unified Storefront Personalization
- **Version**: 1.0.0
- **License**: MIT

## Blending Architecture
Integrates normalized signals from Collaborative Filtering ($S_{CF}$), Content-Based Matching ($S_{CB}$), and Sequential Intent ($S_{SEQ}$):
$$S_{Hybrid}(u, i) = w_{CF} S_{CF}(u, i) + w_{CB} S_{CB}(u, i) + w_{SEQ} S_{SEQ}(s_u, i)$$
- **Default Weights**: $w_{CF} = 0.45$, $w_{CB} = 0.35$, $w_{SEQ} = 0.20$.
- **Cold-Start Adaptation**: When interaction count $|I_u| < 3$, dynamically switches weights to $w_{CB} = 0.70$, $w_{SEQ} = 0.30$, $w_{CF} = 0.00$.

## Benchmark Summary
- **NDCG@10**: 0.468 (Outperforms pure CF by +13.5% and CB by +19.2%).
- **Recall@10**: 0.441.
- **MAP@10**: 0.389.
- **Catalog Coverage**: 92.5%.
