# Dataset Card: E-Commerce Temporal Interactions Benchmark

## Dataset Description
- **Dataset Name**: Cognix E-Commerce Temporal Interaction Benchmark
- **Domain**: Consumer Electronics, Computing, Audio, Wearables, and Smart Office
- **Scale**:
  - Distinct Items: 100
  - Registered Users: 50
  - Total Interaction Events: 2,500+
  - Interaction Types: `click` (weight 1), `favorite` (weight 2), `add_to_cart` (weight 3), `purchase` (weight 5)
  - Time Span: Sequential temporal progression spanning 90 days.

## Temporal Split Methodology
To rigorously prevent data leakage, splits are partitioned along chronological timestamps:
- **Train Set (60%)**: Earliest $t < T_1$ events.
- **Validation Set (20%)**: $T_1 \le t < T_2$ events for hyperparameter tuning.
- **Test Set (20%)**: Final $t \ge T_2$ holdout events for offline evaluation.

No user interactions from the future are permitted to inform past model parameters.
