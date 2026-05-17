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
      <div className="score-block">
        <strong>{priority.priorityScore.toFixed(1)}</strong>
        <span>{priority.priorityLevel}</span>
      </div>
      <button className="secondary-button" onClick={onOpenDetails} type="button">
        Open details
      </button>
    </article>
  );
}
