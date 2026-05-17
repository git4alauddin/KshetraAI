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
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Why this matters</p>
        <h2>Explanation</h2>
      </div>
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
    </section>
  );
}
