# Recommendation System: Architecture Blueprint

```mermaid
flowchart TD
    subgraph Data Layer
        DB[(cognix_recommendation_db)]
        Catalog[Item Catalog: 100 Products]
        Interactions[2,500+ Interaction Events]
    end

    subgraph Recommendation Engines
        CF[Collaborative Filtering: Matrix Factorization SVD]
        CB[Content-Based: TF-IDF + Cosine Distance]
        SEQ[Sequential: Markov Chain Session Transition]
        HYB[Hybrid Ensemble Blended Ranker]
    end

    subgraph Evaluation & Experimentation
        Splitter[Temporal Splitter: Train / Val / Test]
        Eval[Offline Metrics: NDCG@K, Recall@K, MAP@K, Coverage]
        AB[A/B Testing Engine: Multi-Variant Routing & CTR Tracking]
        MLflow[MLflow Model Registry & Artifact Store]
    end

    subgraph Application & Interface
        API[FastAPI Enterprise Gateway: Port 8002]
        Storefront[Next.js 14 Discovery Storefront: Port 3002]
    end

    DB --> CF & CB & SEQ
    Catalog --> CB
    Interactions --> Splitter
    Splitter --> Eval
    Eval --> MLflow
    CF & CB & SEQ --> HYB
    HYB --> AB
    AB --> API
    API --> Storefront
```

## 1. Engine Separation & Decoupling
- **Collaborative Filtering**: Computes a sparse User-Item interaction matrix $R \in \mathbb{R}^{|U| \times |I|}$. Decomposes $R \approx P \cdot Q^T$ using truncated singular value decomposition into $k$ latent factors.
- **Content-Based Engine**: Constructs item feature vectors $v_i$ using TF-IDF over categories, tags, and product specifications. Builds user preference vectors $u_u = \sum_{i \in I_u} w_{u,i} v_i$.
- **Sequential Session Engine**: Models first-order Markov transition probabilities $P(i_t \mid i_{t-1}) = \frac{C(i_{t-1}, i_t)}{\sum_j C(i_{t-1}, j)}$ across session clickstreams.
- **Hybrid Ensemble**: Blends scores:
  $$S_{hybrid}(u, i) = \alpha S_{cf}(u, i) + \beta S_{cb}(u, i) + \gamma S_{seq}(s, i)$$
  with automatic fallback for zero-history users.
