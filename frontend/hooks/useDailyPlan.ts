import { useCallback } from "react";

import {
  getDailyPlan,
  type DailyPlanQuery,
  type DailyPlanResponse
} from "../services/apiClient";
import { useApiResource, type ApiResourceState } from "./useApiResource";

export function useDailyPlan(query: DailyPlanQuery): ApiResourceState<DailyPlanResponse> {
  const request = useCallback(
    () => getDailyPlan(query),
    [query.date, query.page, query.pageSize, query.repId, query.territoryId]
  );
  return useApiResource(request);
}
