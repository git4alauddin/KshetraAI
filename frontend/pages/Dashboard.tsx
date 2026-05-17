import type { WorkflowSelection } from "../state/workflowStore";

type DashboardProps = {
  selection: WorkflowSelection;
  onSelectionChange: (selection: WorkflowSelection) => void;
  onOpenPlan: () => void;
};

export function Dashboard({ selection, onSelectionChange, onOpenPlan }: DashboardProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Workflow Shell</p>
          <h2>Daily Field Command Center</h2>
        </div>
        <button className="primary-button" onClick={onOpenPlan} type="button">
          Open daily plan
        </button>
      </header>

      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">Territory Selection</p>
          <h3>Plan context</h3>
        </div>
        <div className="form-grid">
          <label>
            Rep ID
            <input
              onChange={(event) => onSelectionChange({ ...selection, repId: event.target.value })}
              value={selection.repId}
            />
          </label>
          <label>
            Territory ID
            <input
              onChange={(event) => onSelectionChange({ ...selection, territoryId: event.target.value })}
              value={selection.territoryId}
            />
          </label>
          <label>
            Plan Date
            <input
              onChange={(event) => onSelectionChange({ ...selection, planDate: event.target.value })}
              type="date"
              value={selection.planDate}
            />
          </label>
          <label>
            Selected Entity
            <input
              onChange={(event) => onSelectionChange({ ...selection, selectedEntityId: event.target.value })}
              value={selection.selectedEntityId}
            />
          </label>
        </div>
      </section>

      <section className="workflow-band">
        <div>
          <strong>Signal</strong>
          <span>Backend intelligence outputs</span>
        </div>
        <div>
          <strong>Priority</strong>
          <span>Ranked field visit plan</span>
        </div>
        <div>
          <strong>Action</strong>
          <span>Recommendation and alert review</span>
        </div>
        <div>
          <strong>Outcome</strong>
          <span>Visit feedback submission</span>
        </div>
      </section>
    </div>
  );
}
