# Model Card: Content-Based TF-IDF Recommender

## Model Overview
- **Name**: TF-IDF & Cosine Feature Recommender
- **Task**: Attribute-driven Content Matching
- **Version**: 1.0.0
- **Framework**: Scikit-learn Feature Extraction
- **License**: BSD-3-Clause

## Architecture
Constructs composite document representations from item titles, categories, tags, and product specifications. Applies Term Frequency-Inverse Document Frequency (TF-IDF) vectorization:
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
User profile vector $v_u$ is aggregated as the interaction-weighted average of item vectors. Recommendation scoring uses exact cosine similarity:
$$\text{sim}(u, i) = \frac{v_u \cdot v_i}{\|v_u\|_2 \|v_i\|_2}$$

## Strengths & Limitations
- **Strengths**: Zero cold-start vulnerability for new items with rich metadata.
- **Limitations**: Prone to filter bubble; lower serendipity without collaborative exploration.
