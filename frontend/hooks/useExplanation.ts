import { useCallback } from "react";

import { getExplanation, type ExplanationResponse } from "../services/apiClient";
import { useApiResource, type ApiResourceState } from "./useApiResource";

export function useExplanation(entityId: string): ApiResourceState<ExplanationResponse> {
  const enabled = entityId.trim().length > 0;
  const request = useCallback(() => getExplanation(entityId), [entityId]);
  return useApiResource(request, { enabled });
}
