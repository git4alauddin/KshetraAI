import { useCallback } from "react";

import { getAlerts, type AlertsResponse } from "../services/apiClient";
import { useApiResource, type ApiResourceState } from "./useApiResource";

type AlertQuery = {
  territoryId?: string;
  severity?: string;
  page?: number;
  pageSize?: number;
};

export function useAlerts(query: AlertQuery = {}): ApiResourceState<AlertsResponse> {
  const request = useCallback(
    () => getAlerts(query),
    [query.page, query.pageSize, query.severity, query.territoryId]
  );
  return useApiResource(request);
}
