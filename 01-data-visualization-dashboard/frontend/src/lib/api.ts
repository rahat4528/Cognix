const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

let tokenCache: string | null = null;

export function setAuthToken(token: string) {
  tokenCache = token;
  if (typeof window !== "undefined") {
    localStorage.setItem("cognix_token", token);
  }
}

export function getAuthToken(): string | null {
  if (tokenCache) return tokenCache;
  if (typeof window !== "undefined") {
    tokenCache = localStorage.getItem("cognix_token");
  }
  return tokenCache;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorBody.detail || "Request failed");
  }

  return res.json();
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<any>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  getProfile: () => request<any>("/auth/me"),

  // Workspaces
  listWorkspaces: () => request<any[]>("/workspaces"),
  createWorkspace: (name: string, description?: string) =>
    request<any>("/workspaces", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),

  // Datasets
  listDatasets: (workspaceId: string) =>
    request<any[]>(`/workspaces/${workspaceId}/datasets`),
  getDataset: (id: string) => request<any>(`/datasets/${id}`),
  previewDataset: (id: string, page = 1, pageSize = 50) =>
    request<any>(`/datasets/${id}/preview?page=${page}&page_size=${pageSize}`),
  uploadDataset: (workspaceId: string, formData: FormData) =>
    request<any>(`/workspaces/${workspaceId}/datasets/upload`, {
      method: "POST",
      body: formData,
    }),

  // Transformations
  previewTransformation: (datasetId: string, steps: any[]) =>
    request<any>(`/datasets/${datasetId}/transform/preview`, {
      method: "POST",
      body: JSON.stringify({ steps, sample_size: 50 }),
    }),
  applyTransformation: (datasetId: string, steps: any[], description?: string) =>
    request<any>(`/datasets/${datasetId}/transform/apply`, {
      method: "POST",
      body: JSON.stringify({ steps, description }),
    }),

  // Charts
  listCharts: (workspaceId: string) =>
    request<any[]>(`/workspaces/${workspaceId}/charts`),
  createChart: (workspaceId: string, data: any) =>
    request<any>(`/workspaces/${workspaceId}/charts`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getChart: (id: string) => request<any>(`/charts/${id}`),
  queryChart: (id: string, globalFilters?: any[]) =>
    request<any>(`/charts/${id}/query`, {
      method: "POST",
      body: JSON.stringify({ global_filters: globalFilters }),
    }),

  // Dashboards
  listDashboards: (workspaceId: string) =>
    request<any[]>(`/workspaces/${workspaceId}/dashboards`),
  getDashboard: (id: string) => request<any>(`/dashboards/${id}`),
  createDashboard: (workspaceId: string, data: any) =>
    request<any>(`/workspaces/${workspaceId}/dashboards`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateDashboard: (id: string, data: any) =>
    request<any>(`/dashboards/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  shareDashboard: (id: string) =>
    request<any>(`/dashboards/${id}/share`, {
      method: "POST",
      body: JSON.stringify({ allow_export: true }),
    }),
  getPublicDashboard: (token: string) =>
    request<any>(`/public/dashboards/${token}`),

  // SQL Studio
  executeSQL: (workspaceId: string, sqlText: string) =>
    request<any>(`/workspaces/${workspaceId}/sql/execute`, {
      method: "POST",
      body: JSON.stringify({ sql_text: sqlText }),
    }),
  listSavedQueries: (workspaceId: string) =>
    request<any[]>(`/workspaces/${workspaceId}/sql/saved`),

  // ML Analytics
  listMLExperiments: (workspaceId: string) =>
    request<any[]>(`/workspaces/${workspaceId}/ml/experiments`),
  getExperimentCurves: (experimentId: string) =>
    request<any>(`/ml/experiments/${experimentId}/curves`),
  getExperimentEvaluation: (experimentId: string) =>
    request<any[]>(`/ml/experiments/${experimentId}/evaluation`),
};
