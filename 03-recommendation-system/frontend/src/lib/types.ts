export interface Item {
  id: string;
  title: string;
  category: string;
  price: number;
  rating: number;
  review_count: number;
  tags: string;
  description: string;
  image_url?: string;
}

export interface RecommendationItem {
  item: Item;
  score: number;
  explanation?: string;
  model_contributions?: Record<string, number>;
  is_cold_start?: boolean;
}

export interface ABVariant {
  variant_id: string;
  variant_name: string;
  traffic_pct: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr_pct: number;
  cvr_pct: number;
}

export interface ABExperimentSummary {
  experiment_id: string;
  name: string;
  variants: ABVariant[];
}

export interface BenchmarkMetrics {
  "ndcg@10": number;
  "recall@10": number;
  "precision@10": number;
  "map@10": number;
  "hit_rate@10": number;
  "catalog_coverage": number;
}

export interface BenchmarkReport {
  dataset_metadata: {
    total_items: number;
    total_interactions: number;
    train_interactions: number;
    val_interactions: number;
    test_interactions: number;
    test_eval_users: number;
  };
  temporal_split: {
    train_ratio: number;
    val_ratio: number;
    test_ratio: number;
    train_cutoff_timestamp: number;
    test_start_timestamp: number;
  };
  benchmarks: Record<string, BenchmarkMetrics>;
  elapsed_seconds: number;
}
