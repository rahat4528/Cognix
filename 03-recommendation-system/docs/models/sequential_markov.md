# Model Card: Sequential Markov Session Recommender

## Model Overview
- **Name**: First-Order Markov Chain Session Transition Model
- **Task**: Next-Item Real-Time Session Prediction
- **Version**: 1.0.0
- **License**: MIT

## Mathematical Formulation
Models clickstream transition probabilities across contiguous session events:
$$P(i_{t} = b \mid i_{t-1} = a) = \frac{N(a \to b) + \alpha}{\sum_{c \in I} (N(a \to c) + \alpha)}$$
where $\alpha = 0.01$ is Laplace smoothing parameter.
For multi-item session history $S = [s_1, s_2, \dots, s_L]$, recommendation scores apply exponential temporal decay:
$$S(i \mid S) = \sum_{k=1}^L \lambda^{L-k} P(i \mid s_k)$$
where $\lambda = 0.65$ emphasizes immediate browsing intent.
