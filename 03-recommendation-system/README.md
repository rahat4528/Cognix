# Cognix Recommendation System

A production-grade, multi-paradigm recommendation platform implementing authentic Matrix Factorization Collaborative Filtering, Content-Based TF-IDF matching, Sequential Markov Session Modeling, and a Hybrid Ensemble Ranker.

## Key Architecture & Features
- **Multi-Model Recommendation Suite**:
  - **Collaborative Filtering**: Truncated SVD matrix factorization discovering latent user and item affinities.
  - **Content-Based Filtering**: TF-IDF feature extraction over catalog metadata with cosine similarity.
  - **Sequential Modeling**: First-order Markov chain transition matrices for real-time session intent.
  - **Hybrid Ensemble**: Dynamic weighted ranker with cold-start adaptive re-weighting.
- **Scientific Offline Evaluation**:
  - Temporal train/validation/test splitting to guarantee zero leakage.
  - Authentic ranking metrics: NDCG@K ($K \in \{5, 10\}$), Recall@K, Precision@K, MAP@K, and Catalog Coverage.
- **A/B Testing Framework**:
  - Live variant routing (Control: Popularity, Variant A: Collaborative, Variant B: Hybrid Ensemble) tracking impressions, clicks, conversions, and CTR.
- **Interactive Storefront**:
  - Next.js 14 personal discovery storefront with real-time session feedback.
  - Cold-start preference onboarding quiz.
  - Comprehensive model performance benchmarks dashboard.
  - A/B testing experimentation console.

## Quick Start
```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Seed database and compute model factors
python ../database/seed.py

# 3. Start API gateway
uvicorn backend.api.main:app --port 8002 --reload

# 4. Start frontend storefront
cd ../frontend
npm install
npm run dev
# Visit http://localhost:3002
```
