import {
  Item,
  RecommendationItem,
  ABExperimentSummary,
  BenchmarkReport
} from './types';

const API_BASE = '/api/v1';

export async function fetchPersonalizedRecommendations(
  topK: number = 8,
  sessionId?: string
): Promise<RecommendationItem[]> {
  let url = `${API_BASE}/recommendations/personalized?top_k=${topK}`;
  if (sessionId) url += `&session_id=${sessionId}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load personalized recommendations');
  return res.json();
}

export async function fetchCollaborativeRecommendations(topK: number = 6): Promise<RecommendationItem[]> {
  const res = await fetch(`${API_BASE}/recommendations/collaborative?top_k=${topK}`);
  if (!res.ok) throw new Error('Failed to load collaborative recommendations');
  return res.json();
}

export async function fetchContentBasedRecommendations(topK: number = 6): Promise<RecommendationItem[]> {
  const res = await fetch(`${API_BASE}/recommendations/content-based?top_k=${topK}`);
  if (!res.ok) throw new Error('Failed to load content-based recommendations');
  return res.json();
}

export async function fetchSequentialRecommendations(topK: number = 6): Promise<RecommendationItem[]> {
  const res = await fetch(`${API_BASE}/recommendations/sequential?top_k=${topK}`);
  if (!res.ok) throw new Error('Failed to load sequential recommendations');
  return res.json();
}

export async function fetchSimilarItems(itemId: string, topK: number = 4): Promise<RecommendationItem[]> {
  const res = await fetch(`${API_BASE}/recommendations/similar/${itemId}?top_k=${topK}`);
  if (!res.ok) throw new Error('Failed to load similar items');
  return res.json();
}

export async function fetchCatalog(category?: string, search?: string): Promise<Item[]> {
  let url = `${API_BASE}/items/?limit=50`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch catalog items');
  return res.json();
}

export async function recordInteraction(
  itemId: string,
  type: 'click' | 'favorite' | 'add_to_cart' | 'purchase',
  sessionId?: string
) {
  const res = await fetch(`${API_BASE}/interactions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_id: itemId, interaction_type: type, session_id: sessionId })
  });
  if (!res.ok) throw new Error('Failed to record interaction');
  return res.json();
}

export async function submitOnboardQuiz(
  categories: string[],
  priceTier: string = 'mid',
  techAffinity: string = 'high'
) {
  const res = await fetch(`${API_BASE}/recommendations/onboard-quiz`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_categories: categories,
      price_tier: priceTier,
      tech_affinity: techAffinity
    })
  });
  if (!res.ok) throw new Error('Failed to submit onboarding quiz');
  return res.json();
}

export async function fetchExperimentSummary(): Promise<ABExperimentSummary> {
  const res = await fetch(`${API_BASE}/experiments/`);
  if (!res.ok) throw new Error('Failed to fetch experiments');
  return res.json();
}

export async function recordExperimentEvent(
  experimentId: string,
  variantId: string,
  eventType: 'impression' | 'click' | 'conversion',
  itemId?: string
) {
  let url = `${API_BASE}/experiments/record?experiment_id=${experimentId}&variant_id=${variantId}&event_type=${eventType}`;
  if (itemId) url += `&item_id=${itemId}`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to record experiment event');
  return res.json();
}

export async function fetchBenchmarks(): Promise<BenchmarkReport> {
  const res = await fetch(`${API_BASE}/evaluation/benchmarks`);
  if (!res.ok) throw new Error('Failed to fetch benchmarks');
  return res.json();
}
