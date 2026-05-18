import { statusToneClass } from "../utils/statusTone";

export type PriorityCardData = {
  rank: number;
  entityName: string;
  entityId: string;
  priorityScore: number;
  priorityLevel: string;
  mainReason: string;
};

type PriorityCardProps = {
  priority: PriorityCardData;
  onOpenDetails: () => void;
};

export function PriorityCard({ priority, onOpenDetails }: PriorityCardProps) {
  return (
    <article className="priority-card">
      <div className="rank-block">
        <span>#{priority.rank}</span>
      </div>
      <div className="priority-body">
        <div>
          <h3>{priority.entityName}</h3>
          <p>{priority.entityId}</p>
        </div>
        <p>{priority.mainReason}</p>
      </div>
      <div className="priority-action-grid">
        <div className="priority-action-block">
          <span>Score</span>
          <strong>{priority.priorityScore.toFixed(1)}</strong>
        </div>
        <div className="priority-action-block">
          <span>Priority</span>
          <div>
            <span className={statusToneClass(priority.priorityLevel)}>{priority.priorityLevel}</span>
          </div>
        </div>
        <div className="priority-action-block">
          <span>Details</span>
          <button className="secondary-button" onClick={onOpenDetails} type="button">
            Actions
          </button>
        </div>
      </div>
    </article>
  );
}
