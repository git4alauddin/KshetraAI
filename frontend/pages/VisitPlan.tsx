import { LoadingState } from "../components/LoadingState";
import { PriorityCard, type PriorityCardData } from "../components/PriorityCard";
import type { WorkflowSelection } from "../state/workflowStore";

type VisitPlanProps = {
  selection: WorkflowSelection;
  onOpenRecommendation: () => void;
};

const shellPriority: PriorityCardData = {
  rank: 1,
  entityName: "Backend daily plan",
  entityId: "Awaiting /daily-plan",
  priorityScore: 0,
  priorityLevel: "Pending",
  mainReason: "API client wiring arrives in the next Build 09 slice."
};

export function VisitPlan({ selection, onOpenRecommendation }: VisitPlanProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Daily Plan</p>
          <h2>{selection.territoryId}</h2>
        </div>
        <span className="meta-pill">{selection.planDate}</span>
      </header>

      <LoadingState label="Daily plan endpoint ready for API client wiring" />
      <PriorityCard priority={shellPriority} onOpenDetails={onOpenRecommendation} />
    </div>
  );
}
