import { useCallback, useEffect, useState } from "react";

export type ApiResourceState<T> = {
  data: T | null;
  error: string | null;
  isLoading: boolean;
  reload: () => Promise<void>;
};

type ApiResourceOptions = {
  enabled?: boolean;
};

export function useApiResource<T>(
  request: () => Promise<T>,
  options: ApiResourceOptions = {}
): ApiResourceState<T> {
  const { enabled = true } = options;
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(enabled);

  const reload = useCallback(async () => {
    if (!enabled) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await request();
      setData(response);
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : "API request failed.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [enabled, request]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return {
    data,
    error,
    isLoading,
    reload
  };
}
