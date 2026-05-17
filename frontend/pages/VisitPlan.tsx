import { LoadingState } from "../components/LoadingState";
import { PriorityCard, type PriorityCardData } from "../components/PriorityCard";
import { useDailyPlan } from "../hooks/useDailyPlan";
import type { RankedEntity } from "../services/apiClient";
import type { WorkflowSelection } from "../state/workflowStore";

type VisitPlanProps = {
  selection: WorkflowSelection;
  onOpenRecommendation: (entityId: string) => void;
};

export function VisitPlan({ selection, onOpenRecommendation }: VisitPlanProps) {
  const { data, error, isLoading, reload } = useDailyPlan({
    date: selection.planDate,
    repId: selection.repId,
    territoryId: selection.territoryId
  });
  const rankedEntities = data?.ranked_entities ?? [];

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Daily Plan</p>
          <h2>{selection.territoryId}</h2>
        </div>
        <span className="meta-pill">{selection.planDate}</span>
      </header>

      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">Plan Request</p>
          <h3>Backend API filters</h3>
        </div>
        <div className="detail-grid">
          <div>
            <span>Rep</span>
            <strong>{selection.repId}</strong>
          </div>
          <div>
            <span>Territory</span>
            <strong>{selection.territoryId}</strong>
          </div>
          <div>
            <span>Endpoint</span>
            <strong>GET /daily-plan</strong>
          </div>
        </div>
      </section>

      {isLoading && <LoadingState label="Loading daily plan from backend API" />}

      {!isLoading && error && (
        <section className="state-panel state-panel-error" role="alert">
          <div>
            <strong>Unable to load daily plan</strong>
            <span>{error}</span>
          </div>
          <button className="secondary-button" onClick={() => void reload()} type="button">
            Retry
          </button>
        </section>
      )}

      {!isLoading && !error && rankedEntities.length === 0 && (
        <section className="state-panel">
          <div>
            <strong>No ranked visits returned</strong>
            <span>The API returned an empty daily plan for the selected filters.</span>
          </div>
          <button className="secondary-button" onClick={() => void reload()} type="button">
            Refresh
          </button>
        </section>
      )}

      {!isLoading && !error && rankedEntities.length > 0 && (
        <section className="visit-plan-list" aria-label="Ranked daily visit plan">
          {rankedEntities.map((entity) => (
            <PriorityCard
              key={`${entity.rank}-${entity.entity_id}`}
              priority={toPriorityCardData(entity)}
              onOpenDetails={() => onOpenRecommendation(entity.entity_id)}
            />
          ))}
        </section>
      )}
    </div>
  );
}

function toPriorityCardData(entity: RankedEntity): PriorityCardData {
  return {
    entityId: entity.entity_id,
    entityName: entity.entity_name || entity.entity_id,
    mainReason: entity.main_reason,
    priorityLevel: entity.priority_level,
    priorityScore: entity.priority_score,
    rank: entity.rank
  };
}
