import type { ReactNode } from "react";

import type { WorkflowStep } from "../state/workflowStore";
import { workflowSteps } from "../state/workflowStore";

type DashboardLayoutProps = {
  activeStep: WorkflowStep;
  onStepChange: (step: WorkflowStep) => void;
  children: ReactNode;
};

export function DashboardLayout({ activeStep, onStepChange, children }: DashboardLayoutProps) {
  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Workflow navigation">
        <div className="brand-block">
          <span className="brand-mark" aria-hidden="true">
            K
          </span>
          <div>
            <p className="eyebrow">KshetraAI</p>
            <h1>Field Intelligence</h1>
          </div>
        </div>

        <nav className="workflow-nav">
          {workflowSteps.map((step) => (
            <button
              className={step.id === activeStep ? "nav-item nav-item-active" : "nav-item"}
              key={step.id}
              onClick={() => onStepChange(step.id)}
              type="button"
            >
              <span>{step.label}</span>
              <small>{step.description}</small>
            </button>
          ))}
        </nav>
      </aside>

      <section className="workspace">{children}</section>
    </main>
  );
}
