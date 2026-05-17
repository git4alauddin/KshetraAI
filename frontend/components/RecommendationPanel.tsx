export type RecommendationPanelData = {
  entityId: string;
  riskOrOpportunity: string;
  recommendedActions: string[];
  recommendedProductCategory: string;
  confidenceLevel: string;
};

type RecommendationPanelProps = {
  recommendation: RecommendationPanelData;
};

export function RecommendationPanel({ recommendation }: RecommendationPanelProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Next Best Action</p>
        <h2>Recommendation</h2>
      </div>
      <div className="detail-grid">
        <div>
          <span>Entity</span>
          <strong>{recommendation.entityId}</strong>
        </div>
        <div>
          <span>Product Category</span>
          <strong>{recommendation.recommendedProductCategory}</strong>
        </div>
        <div>
          <span>Confidence</span>
          <strong>{recommendation.confidenceLevel}</strong>
        </div>
      </div>
      <p className="context-text">{recommendation.riskOrOpportunity}</p>
      <ul className="check-list">
        {recommendation.recommendedActions.map((action) => (
          <li key={action}>{action}</li>
        ))}
      </ul>
    </section>
  );
}
