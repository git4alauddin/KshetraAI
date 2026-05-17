import { useCallback } from "react";

import { getHealth, type HealthResponse } from "../services/apiClient";
import { useApiResource, type ApiResourceState } from "./useApiResource";

export function useHealth(): ApiResourceState<HealthResponse> {
  const request = useCallback(() => getHealth(), []);
  return useApiResource(request);
}
