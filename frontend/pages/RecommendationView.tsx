import {
  RecommendationPanel,
  type RecommendationPanelData
} from "../components/RecommendationPanel";
import {
  ExplanationPanel,
  type ExplanationPanelData
} from "../components/ExplanationPanel";
import type { WorkflowSelection } from "../state/workflowStore";

type RecommendationViewProps = {
  selection: WorkflowSelection;
  onOpenAlerts: () => void;
};

const shellRecommendation: RecommendationPanelData = {
  entityId: "Awaiting /recommendations/{entity_id}",
  riskOrOpportunity: "Recommendation details will be populated from the backend API client.",
  recommendedActions: ["Connect API client", "Render returned actions", "Keep backend reasoning visible"],
  recommendedProductCategory: "Pending",
  confidenceLevel: "Pending"
};

const shellExplanations: ExplanationPanelData[] = [
  {
    explanationType: "workflow",
    summaryText: "Explanation content will render from /explanations/{entity_id}.",
    evidenceItems: ["Backend-provided summary", "Backend-provided evidence list", "Backend confidence level"],
    confidenceLevel: "Pending"
  }
];

export function RecommendationView({ selection, onOpenAlerts }: RecommendationViewProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Entity Detail</p>
          <h2>{selection.selectedEntityId}</h2>
        </div>
        <button className="secondary-button" onClick={onOpenAlerts} type="button">
          Review alerts
        </button>
      </header>

      <div className="split-grid">
        <RecommendationPanel recommendation={shellRecommendation} />
        <ExplanationPanel explanations={shellExplanations} />
      </div>
    </div>
  );
}
