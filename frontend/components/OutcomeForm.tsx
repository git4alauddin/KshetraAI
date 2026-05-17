import { useState, type FormEvent } from "react";

import type { OutcomeSubmissionRequest } from "../services/apiClient";

type OutcomeFormProps = {
  entityId: string;
  isSubmitting: boolean;
  onSubmit: (payload: OutcomeSubmissionRequest) => Promise<void>;
  repId: string;
  recommendationId: string;
};

type AlertValidatedOption = "unknown" | "true" | "false";

type OutcomeFormState = {
  alertId: string;
  alertValidated: AlertValidatedOption;
  entityId: string;
  feedbackCategory: string;
  orderPlaced: boolean;
  orderValue: string;
  recommendationFollowed: boolean;
  recommendationId: string;
  repFeedback: string;
  repId: string;
  saleMade: boolean;
  visitCompleted: boolean;
};

export function OutcomeForm({
  entityId,
  isSubmitting,
  onSubmit,
  repId,
  recommendationId
}: OutcomeFormProps) {
  const [formState, setFormState] = useState<OutcomeFormState>({
    alertId: "",
    alertValidated: "unknown",
    entityId,
    feedbackCategory: "",
    orderPlaced: false,
    orderValue: "0",
    recommendationFollowed: false,
    recommendationId,
    repFeedback: "",
    repId,
    saleMade: false,
    visitCompleted: true
  });
  const [validationError, setValidationError] = useState<string | null>(null);

  const submitForm = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const orderValue = Number(formState.orderValue || "0");
    if (!formState.recommendationId.trim() || !formState.entityId.trim() || !formState.repId.trim()) {
      setValidationError("Recommendation ID, entity ID, and rep ID are required.");
      return;
    }
    if (Number.isNaN(orderValue) || orderValue < 0) {
      setValidationError("Order value must be zero or a positive number.");
      return;
    }

    setValidationError(null);
    await onSubmit({
      alert_id: optionalText(formState.alertId),
      alert_validated: toAlertValidatedValue(formState.alertValidated),
      entity_id: formState.entityId.trim(),
      feedback_category: optionalText(formState.feedbackCategory),
      order_placed: formState.orderPlaced,
      order_value: orderValue,
      recommendation_followed: formState.recommendationFollowed,
      recommendation_id: formState.recommendationId.trim(),
      rep_feedback: optionalText(formState.repFeedback),
      rep_id: formState.repId.trim(),
      sale_made: formState.saleMade,
      visit_completed: formState.visitCompleted
    });
  };

  return (
    <form className="outcome-form" onSubmit={(event) => void submitForm(event)}>
      <div className="form-grid">
        <label>
          Recommendation ID
          <input
            onChange={(event) =>
              setFormState({ ...formState, recommendationId: event.target.value })
            }
            value={formState.recommendationId}
          />
        </label>
        <label>
          Entity ID
          <input
            onChange={(event) => setFormState({ ...formState, entityId: event.target.value })}
            value={formState.entityId}
          />
        </label>
        <label>
          Rep ID
          <input
            onChange={(event) => setFormState({ ...formState, repId: event.target.value })}
            value={formState.repId}
          />
        </label>
        <label>
          Order Value
          <input
            min="0"
            onChange={(event) => setFormState({ ...formState, orderValue: event.target.value })}
            placeholder="0"
            type="number"
            value={formState.orderValue}
          />
        </label>
        <label>
          Alert ID
          <input
            onChange={(event) => setFormState({ ...formState, alertId: event.target.value })}
            placeholder="Optional alert reference"
            value={formState.alertId}
          />
        </label>
        <label>
          Feedback Category
          <input
            onChange={(event) =>
              setFormState({ ...formState, feedbackCategory: event.target.value })
            }
            placeholder="Optional category"
            value={formState.feedbackCategory}
          />
        </label>
        <label>
          Alert Validated
          <select
            onChange={(event) =>
              setFormState({
                ...formState,
                alertValidated: event.target.value as AlertValidatedOption
              })
            }
            value={formState.alertValidated}
          >
            <option value="unknown">Unknown</option>
            <option value="true">Validated</option>
            <option value="false">Not validated</option>
          </select>
        </label>
      </div>
      <div className="toggle-grid">
        <label>
          <input
            checked={formState.visitCompleted}
            onChange={(event) =>
              setFormState({ ...formState, visitCompleted: event.target.checked })
            }
            type="checkbox"
          />
          Visit completed
        </label>
        <label>
          <input
            checked={formState.recommendationFollowed}
            onChange={(event) =>
              setFormState({ ...formState, recommendationFollowed: event.target.checked })
            }
            type="checkbox"
          />
          Recommendation followed
        </label>
        <label>
          <input
            checked={formState.saleMade}
            onChange={(event) => setFormState({ ...formState, saleMade: event.target.checked })}
            type="checkbox"
          />
          Sale made
        </label>
        <label>
          <input
            checked={formState.orderPlaced}
            onChange={(event) =>
              setFormState({ ...formState, orderPlaced: event.target.checked })
            }
            type="checkbox"
          />
          Order placed
        </label>
      </div>
      <label>
        Rep feedback
        <textarea
          onChange={(event) => setFormState({ ...formState, repFeedback: event.target.value })}
          placeholder="Capture field notes after the visit"
          rows={4}
          value={formState.repFeedback}
        />
      </label>
      {validationError && (
        <div className="inline-error" role="alert">
          {validationError}
        </div>
      )}
      <div className="form-actions">
        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Submitting outcome" : "Submit outcome"}
        </button>
      </div>
    </form>
  );
}

function optionalText(value: string): string | undefined {
  const trimmedValue = value.trim();
  return trimmedValue.length > 0 ? trimmedValue : undefined;
}

function toAlertValidatedValue(value: AlertValidatedOption): boolean | "unknown" {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return "unknown";
}
