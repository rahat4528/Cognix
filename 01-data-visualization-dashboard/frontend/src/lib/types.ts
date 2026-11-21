export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string;
  role?: string;
}

export interface DatasetColumn {
  id: string;
  name: string;
  data_type: string;
  is_nullable: boolean;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values?: any[];
  statistics?: Record<string, any>;
}

export interface DatasetVersion {
  id: string;
  version_number: number;
  original_filename: string;
  file_format: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  checksum_sha256: string;
  quality_score?: number;
  quality_report?: Record<string, any>;
  created_at: string;
}

export interface Dataset {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  source_type: string;
  created_at: string;
  latest_version?: DatasetVersion;
  columns?: DatasetColumn[];
}

export interface ChartConfig {
  x_axis?: string;
  y_axis?: string;
  series?: string;
  aggregation?: string;
  filters?: any[];
  limit?: number;
  time_interval?: string;
  color_palette?: string;
  display_options?: Record<string, any>;
}

export interface Chart {
  id: string;
  workspace_id: string;
  dataset_id: string;
  dataset_version_id?: string;
  name: string;
  description?: string;
  chart_type: string;
  config: ChartConfig;
  created_at: string;
}

export interface DashboardChartLayout {
  chart_id: string;
  chart_name?: string;
  chart_type?: string;
  config?: ChartConfig;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
}

export interface Dashboard {
  id: string;
  workspace_id: string;
  title: string;
  description?: string;
  version: number;
  is_public: boolean;
  global_filters: any[];
  charts: DashboardChartLayout[];
  created_at: string;
}

export interface SQLExecuteResponse {
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  duration_ms: float;
  error?: string;
}

export interface MLExperiment {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  framework: string;
  runs_count: number;
  created_at: string;
}

export interface EvaluationMetrics {
  experiment_id: string;
  run_id: string;
  split_name: string;
  accuracy: number;
  precision_macro: number;
  recall_macro: number;
  f1_macro: number;
  confusion_matrix: {
    labels: string[];
    matrix: number[][];
  };
  roc_curve?: {
    fpr: number[];
    tpr: number[];
    auc: number;
  };
  pr_curve?: {
    precision: number[];
    recall: number[];
    average_precision: number;
  };
  provenance_note: string;
}
