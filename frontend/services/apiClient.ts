export type HealthResponse = {
  status: string;
  service: string;
};

export type DailyPlanQuery = {
  repId?: string;
  territoryId?: string;
  date?: string;
  page?: number;
  pageSize?: number;
};

export type RankedEntity = {
  rank: number;
  entity_id: string;
  entity_name: string;
  priority_score: number;
  priority_level: string;
  main_reason: string;
};

export type DailyPlanResponse = {
  rep_id: string | null;
  territory_id: string | null;
  date: string | null;
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  ranked_entities: RankedEntity[];
};

export type RecommendationResponse = {
  entity_id: string;
  risk_or_opportunity: string;
  recommended_actions: string[];
  recommended_product_category: string;
  confidence_level: string;
};

export type AlertResponse = {
  alert_id: string;
  entity_id: string;
  alert_type: string;
  severity_score: number;
  severity_level: string;
  confidence_level: string;
};

export type AlertsResponse = {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  alerts: AlertResponse[];
};

export type ExplanationItemResponse = {
  explanation_type: string;
  summary_text: string;
  evidence_items: string[];
  confidence_level: string;
};

export type ExplanationResponse = {
  entity_id: string;
  explanations: ExplanationItemResponse[];
};

export type OutcomeSubmissionRequest = {
  recommendation_id: string;
  entity_id: string;
  rep_id: string;
  visit_completed: boolean;
  recommendation_followed: boolean;
  sale_made: boolean;
  order_placed: boolean;
  order_value: number;
  alert_validated: boolean | "unknown";
  feedback_category?: string;
  rep_feedback?: string;
  alert_id?: string;
};

export type OutcomeSubmissionResponse = {
  status: string;
  message: string;
  outcome_id: string | null;
};

type ApiErrorPayload = {
  detail?: {
    error?: string;
  };
  error?: string;
};

export class ApiClientError extends Error {
  readonly statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = "ApiClientError";
    this.statusCode = statusCode;
  }
}

const API_BASE_URL =
  import.meta.env.VITE_KSHETRA_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

export async function getDailyPlan(query: DailyPlanQuery = {}): Promise<DailyPlanResponse> {
  const params = new URLSearchParams();
  appendQueryParam(params, "rep_id", query.repId);
  appendQueryParam(params, "territory_id", query.territoryId);
  appendQueryParam(params, "date", query.date);
  appendQueryParam(params, "page", query.page?.toString());
  appendQueryParam(params, "page_size", query.pageSize?.toString());
  const queryString = params.toString();
  return apiFetch<DailyPlanResponse>(`/daily-plan${queryString ? `?${queryString}` : ""}`);
}

export async function getRecommendation(entityId: string): Promise<RecommendationResponse> {
  return apiFetch<RecommendationResponse>(`/recommendations/${encodeURIComponent(entityId)}`);
}

export async function getAlerts(
  options: { territoryId?: string; severity?: string; page?: number; pageSize?: number } = {}
): Promise<AlertsResponse> {
  const params = new URLSearchParams();
  appendQueryParam(params, "territory_id", options.territoryId);
  appendQueryParam(params, "severity", options.severity);
  appendQueryParam(params, "page", options.page?.toString());
  appendQueryParam(params, "page_size", options.pageSize?.toString());
  const queryString = params.toString();
  return apiFetch<AlertsResponse>(`/alerts${queryString ? `?${queryString}` : ""}`);
}

export async function getExplanation(entityId: string): Promise<ExplanationResponse> {
  return apiFetch<ExplanationResponse>(`/explanations/${encodeURIComponent(entityId)}`);
}

export async function submitOutcome(
  payload: OutcomeSubmissionRequest
): Promise<OutcomeSubmissionResponse> {
  return apiFetch<OutcomeSubmissionResponse>("/outcomes", {
    body: JSON.stringify(payload),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  });
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  const payload = await parseResponsePayload(response);
  if (!response.ok) {
    throw new ApiClientError(errorMessage(payload, response.status), response.status);
  }
  return payload as T;
}

async function parseResponsePayload(response: Response): Promise<unknown> {
  const responseText = await response.text();
  if (!responseText) {
    return {};
  }
  try {
    return JSON.parse(responseText);
  } catch {
    return { error: responseText };
  }
}

function errorMessage(payload: unknown, statusCode: number): string {
  const apiError = payload as ApiErrorPayload;
  return apiError.detail?.error ?? apiError.error ?? `API request failed with status ${statusCode}`;
}

function appendQueryParam(params: URLSearchParams, key: string, value?: string): void {
  if (value && value.trim().length > 0) {
    params.set(key, value);
  }
}
