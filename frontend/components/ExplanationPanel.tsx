export type ExplanationPanelData = {
  explanationType: string;
  summaryText: string;
  evidenceItems: string[];
  confidenceLevel: string;
};

type ExplanationPanelProps = {
  explanations: ExplanationPanelData[];
};

export function ExplanationPanel({ explanations }: ExplanationPanelProps) {
  const story = buildExplanationStory(explanations);

  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Why this matters</p>
        <h2>Explanation</h2>
      </div>
      <div className="explanation-summary">
        <div>
          <p className="eyebrow">Primary reason</p>
          <h3>{story.primarySummary}</h3>
        </div>
        <span className="confidence-pill">{story.primaryConfidence}</span>
      </div>

      <div className="evidence-chip-list" aria-label="Key evidence">
        {story.keyEvidence.map((item) => (
          <span className="evidence-chip" key={item}>
            {formatEvidenceLabel(item)}
          </span>
        ))}
      </div>

      <div className="signal-grid" aria-label="Supporting signals">
        {story.signalGroups.map((group) => (
          <div className="signal-card" key={group.label}>
            <strong>{group.count}</strong>
            <span>{group.label}</span>
          </div>
        ))}
      </div>

      <details className="trace-details">
        <summary>Trace details</summary>
      <div className="explanation-stack">
        {explanations.map((explanation) => (
          <article className="explanation-item" key={`${explanation.explanationType}-${explanation.summaryText}`}>
            <div className="explanation-title">
              <strong>{explanation.explanationType}</strong>
              <span className="confidence-pill">{explanation.confidenceLevel}</span>
            </div>
            <p>{explanation.summaryText}</p>
            <ul className="evidence-list">
              {explanation.evidenceItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
      </details>
    </section>
  );
}

type ExplanationStory = {
  primarySummary: string;
  primaryConfidence: string;
  keyEvidence: string[];
  signalGroups: Array<{ label: string; count: number }>;
};

function buildExplanationStory(explanations: ExplanationPanelData[]): ExplanationStory {
  const primaryExplanation =
    explanations.find((explanation) => explanation.explanationType === "recommendation") ??
    explanations.find((explanation) => explanation.explanationType === "priority") ??
    explanations[0];
  const keyEvidence = dedupeEvidence(explanations.flatMap((explanation) => explanation.evidenceItems));
  const signalGroups = [
    { label: "Recommendation rules matched", count: countType(explanations, "recommendation") },
    { label: "Operational alerts", count: countType(explanations, "anomaly") },
    { label: "Priority signal", count: countType(explanations, "priority") }
  ].filter((group) => group.count > 0);

  return {
    primarySummary: primaryExplanation?.summaryText ?? "No explanation evidence returned yet.",
    primaryConfidence: primaryExplanation?.confidenceLevel ?? "Low",
    keyEvidence: keyEvidence.slice(0, 6),
    signalGroups
  };
}

function dedupeEvidence(evidenceItems: string[]): string[] {
  const seen = new Set<string>();
  const rankedEvidence = [...evidenceItems].sort(evidenceSortOrder);
  return rankedEvidence.filter((item) => {
    const key = canonicalEvidenceKey(item.split(":")[0].trim());
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function evidenceSortOrder(left: string, right: string): number {
  return evidenceWeight(left) - evidenceWeight(right);
}

function evidenceWeight(item: string): number {
  const key = canonicalEvidenceKey(item.split(":")[0].trim());
  const weights: Record<string, number> = {
    inventory_need: 1,
    stockout_risk_score: 2,
    sales_velocity_score: 3,
    sales_opportunity: 4,
    seasonal_product_relevance: 5,
    priority_score: 6,
    relationship_need: 7,
    competitive_pressure: 8,
    agronomic_urgency: 9
  };
  return weights[key] ?? 99;
}

function canonicalEvidenceKey(key: string): string {
  const canonicalKeys: Record<string, string> = {
    inventory_need_score: "inventory_need",
    sales_opportunity_score: "sales_opportunity",
    relationship_need_score: "relationship_need",
    competitive_pressure_score: "competitive_pressure",
    weather_risk_score: "agronomic_urgency",
    crop_stage_risk_score: "agronomic_urgency",
    pest_disease_risk_score: "agronomic_urgency",
    ndvi_stress_score: "agronomic_urgency"
  };
  return canonicalKeys[key] ?? key;
}

function countType(explanations: ExplanationPanelData[], explanationType: string): number {
  return explanations.filter((explanation) => explanation.explanationType === explanationType).length;
}

function formatEvidenceLabel(item: string): string {
  const [rawLabel, ...rest] = item.split(":");
  const label = rawLabel.trim().replaceAll("_", " ");
  const value = rest.join(":").trim();
  return value ? `${label}: ${value}` : label;
}
