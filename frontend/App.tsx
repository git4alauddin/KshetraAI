import { useState } from "react";

import { DashboardLayout } from "./layouts/DashboardLayout";
import { AlertsView } from "./pages/AlertsView";
import { Dashboard } from "./pages/Dashboard";
import { OutcomeSubmission } from "./pages/OutcomeSubmission";
import { RecommendationView } from "./pages/RecommendationView";
import { VisitPlan } from "./pages/VisitPlan";
import {
  defaultWorkflowSelection,
  type WorkflowSelection,
  type WorkflowStep
} from "./state/workflowStore";

export function App() {
  const [activeStep, setActiveStep] = useState<WorkflowStep>("dashboard");
  const [selection, setSelection] = useState<WorkflowSelection>(defaultWorkflowSelection);

  return (
    <DashboardLayout activeStep={activeStep} onStepChange={setActiveStep}>
      {activeStep === "dashboard" && (
        <Dashboard selection={selection} onSelectionChange={setSelection} onOpenPlan={() => setActiveStep("visit-plan")} />
      )}
      {activeStep === "visit-plan" && (
        <VisitPlan
          selection={selection}
          onOpenRecommendation={(entityId) => {
            setSelection({ ...selection, selectedEntityId: entityId });
            setActiveStep("recommendation");
          }}
        />
      )}
      {activeStep === "recommendation" && (
        <RecommendationView selection={selection} onOpenAlerts={() => setActiveStep("alerts")} />
      )}
      {activeStep === "alerts" && <AlertsView selection={selection} onOpenOutcome={() => setActiveStep("outcome")} />}
      {activeStep === "outcome" && <OutcomeSubmission selection={selection} />}
    </DashboardLayout>
  );
}
