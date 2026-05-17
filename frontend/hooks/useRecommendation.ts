import { useCallback } from "react";

import { getRecommendation, type RecommendationResponse } from "../services/apiClient";
import { useApiResource, type ApiResourceState } from "./useApiResource";

export function useRecommendation(entityId: string): ApiResourceState<RecommendationResponse> {
  const enabled = entityId.trim().length > 0;
  const request = useCallback(() => getRecommendation(entityId), [entityId]);
  return useApiResource(request, { enabled });
}
