import {
  RecommendationPanel,
  type RecommendationPanelData
} from "../components/RecommendationPanel";
import {
  ExplanationPanel,
  type ExplanationPanelData
} from "../components/ExplanationPanel";
import { LoadingState } from "../components/LoadingState";
import { useExplanation } from "../hooks/useExplanation";
import { useRecommendation } from "../hooks/useRecommendation";
import type {
  ExplanationItemResponse,
  RecommendationResponse
} from "../services/apiClient";
import type { WorkflowSelection } from "../state/workflowStore";

type RecommendationViewProps = {
  selection: WorkflowSelection;
  onOpenAlerts: () => void;
};

export function RecommendationView({ selection, onOpenAlerts }: RecommendationViewProps) {
  const recommendation = useRecommendation(selection.selectedEntityId);
  const explanation = useExplanation(selection.selectedEntityId);
  const recommendationData = recommendation.data
    ? toRecommendationPanelData(recommendation.data)
    : null;
  const explanationData = explanation.data?.explanations.map(toExplanationPanelData) ?? [];
  const showRecommendationEmpty =
    !recommendation.isLoading && !recommendation.error && recommendationData === null;
  const showExplanationEmpty =
    !explanation.isLoading && !explanation.error && explanationData.length === 0;

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

      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">Backend Detail Request</p>
          <h3>{selection.selectedEntityId}</h3>
        </div>
        <div className="detail-grid">
          <div>
            <span>Recommendation</span>
            <strong>GET /recommendations/{selection.selectedEntityId}</strong>
          </div>
          <div>
            <span>Explanation</span>
            <strong>GET /explanations/{selection.selectedEntityId}</strong>
          </div>
          <div>
            <span>Source</span>
            <strong>Backend API</strong>
          </div>
        </div>
      </section>

      {(recommendation.isLoading || explanation.isLoading) && (
        <LoadingState label="Loading recommendation and explanation from backend API" />
      )}

      {recommendation.error && (
        <section className="state-panel state-panel-error" role="alert">
          <div>
            <strong>Unable to load recommendation</strong>
            <span>{recommendation.error}</span>
          </div>
          <button className="secondary-button" onClick={() => void recommendation.reload()} type="button">
            Retry
          </button>
        </section>
      )}

      {explanation.error && (
        <section className="state-panel state-panel-error" role="alert">
          <div>
            <strong>Unable to load explanation</strong>
            <span>{explanation.error}</span>
          </div>
          <button className="secondary-button" onClick={() => void explanation.reload()} type="button">
            Retry
          </button>
        </section>
      )}

      <div className="split-grid">
        {recommendationData ? (
          <RecommendationPanel recommendation={recommendationData} />
        ) : showRecommendationEmpty ? (
          <section className="state-panel">
            <div>
              <strong>No recommendation loaded</strong>
              <span>The backend has not returned a recommendation for this entity yet.</span>
            </div>
          </section>
        ) : (
          <section className="state-panel">
            <div>
              <strong>Recommendation pending</strong>
              <span>Waiting for backend response.</span>
            </div>
          </section>
        )}

        {explanationData.length > 0 ? (
          <ExplanationPanel explanations={explanationData} />
        ) : showExplanationEmpty ? (
          <section className="state-panel">
            <div>
              <strong>No explanation loaded</strong>
              <span>The backend has not returned explanation evidence for this entity yet.</span>
            </div>
          </section>
        ) : (
          <section className="state-panel">
            <div>
              <strong>Explanation pending</strong>
              <span>Waiting for backend response.</span>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

function toRecommendationPanelData(
  recommendation: RecommendationResponse
): RecommendationPanelData {
  return {
    confidenceLevel: recommendation.confidence_level,
    entityId: recommendation.entity_id,
    recommendedActions: recommendation.recommended_actions,
    recommendedProductCategory: recommendation.recommended_product_category,
    riskOrOpportunity: recommendation.risk_or_opportunity
  };
}

function toExplanationPanelData(explanation: ExplanationItemResponse): ExplanationPanelData {
  return {
    confidenceLevel: explanation.confidence_level,
    evidenceItems: explanation.evidence_items,
    explanationType: explanation.explanation_type,
    summaryText: explanation.summary_text
  };
}
