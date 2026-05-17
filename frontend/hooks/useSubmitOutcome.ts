import { useCallback, useState } from "react";

import {
  submitOutcome,
  type OutcomeSubmissionRequest,
  type OutcomeSubmissionResponse
} from "../services/apiClient";

type SubmitOutcomeState = {
  data: OutcomeSubmissionResponse | null;
  error: string | null;
  isSubmitting: boolean;
  submit: (payload: OutcomeSubmissionRequest) => Promise<OutcomeSubmissionResponse | null>;
};

export function useSubmitOutcome(): SubmitOutcomeState {
  const [data, setData] = useState<OutcomeSubmissionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submit = useCallback(async (payload: OutcomeSubmissionRequest) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await submitOutcome(payload);
      setData(response);
      return response;
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : "Outcome submission failed.";
      setError(message);
      return null;
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  return {
    data,
    error,
    isSubmitting,
    submit
  };
}
