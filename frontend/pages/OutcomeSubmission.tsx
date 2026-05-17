import { OutcomeForm } from "../components/OutcomeForm";
import type { WorkflowSelection } from "../state/workflowStore";

type OutcomeSubmissionProps = {
  selection: WorkflowSelection;
};

export function OutcomeSubmission({ selection }: OutcomeSubmissionProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Outcome Capture</p>
          <h2>Visit feedback</h2>
        </div>
        <span className="meta-pill">Draft only</span>
      </header>

      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">POST /outcomes</p>
          <h3>Outcome submission shell</h3>
        </div>
        <OutcomeForm
          entityId={selection.selectedEntityId}
          recommendationId="RECOMMENDATION_FROM_API"
          repId={selection.repId}
        />
      </section>
    </div>
  );
}
