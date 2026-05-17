import { OutcomeForm } from "../components/OutcomeForm";
import { useSubmitOutcome } from "../hooks/useSubmitOutcome";
import type { OutcomeSubmissionRequest } from "../services/apiClient";
import type { WorkflowSelection } from "../state/workflowStore";

type OutcomeSubmissionProps = {
  selection: WorkflowSelection;
};

export function OutcomeSubmission({ selection }: OutcomeSubmissionProps) {
  const outcomeSubmission = useSubmitOutcome();

  const submitOutcome = async (payload: OutcomeSubmissionRequest) => {
    await outcomeSubmission.submit(payload);
  };

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Outcome Capture</p>
          <h2>Visit feedback</h2>
        </div>
        <span className="meta-pill">POST /outcomes</span>
      </header>

      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">POST /outcomes</p>
          <h3>Outcome submission</h3>
        </div>
        <div className="detail-grid">
          <div>
            <span>Entity</span>
            <strong>{selection.selectedEntityId}</strong>
          </div>
          <div>
            <span>Rep</span>
            <strong>{selection.repId}</strong>
          </div>
          <div>
            <span>Source</span>
            <strong>Backend API</strong>
          </div>
        </div>
        <OutcomeForm
          entityId={selection.selectedEntityId}
          isSubmitting={outcomeSubmission.isSubmitting}
          onSubmit={submitOutcome}
          recommendationId="RECOMMENDATION_FROM_API"
          repId={selection.repId}
        />
      </section>

      {outcomeSubmission.error && (
        <section className="state-panel state-panel-error" role="alert">
          <div>
            <strong>Unable to submit outcome</strong>
            <span>{outcomeSubmission.error}</span>
          </div>
        </section>
      )}

      {outcomeSubmission.data && !outcomeSubmission.error && (
        <section className="state-panel state-panel-success" role="status">
          <div>
            <strong>{outcomeSubmission.data.message}</strong>
            <span>
              {outcomeSubmission.data.outcome_id
                ? `Outcome ID: ${outcomeSubmission.data.outcome_id}`
                : outcomeSubmission.data.status}
            </span>
          </div>
        </section>
      )}
    </div>
  );
}
