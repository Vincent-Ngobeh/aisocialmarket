import axios from "axios";
import type { CampaignBrief, CampaignResponse } from "../types/campaign";
import type { ApiKeys } from "../types/auth";

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

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get("/health");
    return response.data.status === "healthy";
  } catch {
    return false;
  }
}
