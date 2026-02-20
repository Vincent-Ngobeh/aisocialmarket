import axios from "axios";
import type { CampaignBrief, CampaignResponse } from "../types/campaign";
import type { ApiKeys, FreeTierStatus } from "../types/auth";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

function getAuthHeaders(keys: ApiKeys) {
  return {
    "X-Anthropic-Key": keys.anthropicKey,
    "X-OpenAI-Key": keys.openaiKey,
  };
}

export interface ApiErrorDetail {
  success: boolean;
  error: string;
  detail: string;
  service?: string;
  remaining?: number;
  limit?: number;
  retry_after?: number;
}

/**
 * Normalize the response data from an API error.
 * FastAPI's HTTPException wraps dict details under a "detail" key,
 * so we unwrap {detail: {success, error, detail}} to the inner object.
 */
function normalizeErrorData(raw: unknown): ApiErrorDetail | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const obj = raw as Record<string, unknown>;

  // Already flat: {success, error, detail, ...}
  if (typeof obj.error === "string" && typeof obj.detail === "string") {
    return obj as unknown as ApiErrorDetail;
  }

  // Nested: {detail: {success, error, detail, ...}} (FastAPI HTTPException format)
  if (obj.detail && typeof obj.detail === "object") {
    const inner = obj.detail as Record<string, unknown>;
    if (typeof inner.error === "string") {
      return inner as unknown as ApiErrorDetail;
    }
  }

  // detail is a plain string: {detail: "some message"}
  if (typeof obj.detail === "string") {
    return { success: false, error: "error", detail: obj.detail };
  }

  return undefined;
}

export function parseApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const data = normalizeErrorData(err.response?.data);

    if (!err.response) {
      return "Cannot connect to server. Please check your internet connection and try again.";
    }

    if (status === 401) {
      if (data?.error === "invalid_api_key") {
        const service = data.service === "anthropic" ? "Anthropic" : "OpenAI";
        return `Your ${service} API key is invalid or has been revoked. Please update your key and try again.`;
      }
      return data?.detail || "Invalid API key. Please check your keys and try again.";
    }

    if (status === 429) {
      if (data?.error === "free_tier_limit_reached") {
        return `You've used all ${data.limit} free generations for today. Try again tomorrow or enter your own API keys to continue.`;
      }
      return "Too many requests. Please wait a moment before trying again.";
    }

    if (status === 502) {
      return data?.detail || "AI service is temporarily unavailable. Please try again in a moment.";
    }

    if (status === 503) {
      return data?.detail || "Free tier is currently unavailable. Please use your own API keys.";
    }

    return data?.detail || "Something went wrong. Please try again.";
  }

  if (err instanceof Error) {
    return err.message;
  }

  return "Something went wrong. Please try again.";
}

export async function generateFullCampaign(
  brief: CampaignBrief,
  keys: ApiKeys
): Promise<CampaignResponse> {
  const response = await apiClient.post<CampaignResponse>(
    "/api/v1/campaigns/generate-full",
    brief,
    { headers: getAuthHeaders(keys) }
  );
  return response.data;
}

export async function generateCopyOnly(
  brief: CampaignBrief,
  keys: ApiKeys
): Promise<CampaignResponse> {
  const response = await apiClient.post<CampaignResponse>(
    "/api/v1/campaigns/generate-copy",
    brief,
    { headers: { "X-Anthropic-Key": keys.anthropicKey } }
  );
  return response.data;
}

export async function generateFreeCampaign(
  brief: CampaignBrief,
  generateImage: boolean = false
): Promise<CampaignResponse> {
  const response = await apiClient.post<CampaignResponse>(
    "/api/v1/campaigns/generate-free",
    brief,
    { params: { generate_image: generateImage } }
  );
  return response.data;
}

export async function getFreeTierStatus(): Promise<FreeTierStatus> {
  const response = await apiClient.get<FreeTierStatus>(
    "/api/v1/campaigns/free-tier-status"
  );
  return response.data;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get("/health");
    return response.data.status === "healthy";
  } catch {
    return false;
  }
}
