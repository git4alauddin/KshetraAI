export type AlertPanelData = {
  alertId: string;
  entityId: string;
  alertType: string;
  severityScore: number;
  severityLevel: string;
  confidenceLevel: string;
};

type AlertPanelProps = {
  alerts: AlertPanelData[];
};

export function AlertPanel({ alerts }: AlertPanelProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Active Signals</p>
        <h2>Alerts</h2>
      </div>
      <div className="alert-list">
        {alerts.map((alert) => (
          <article className="alert-row" key={alert.alertId}>
            <div>
              <h3>{alert.alertType}</h3>
              <p>{alert.entityId}</p>
            </div>
            <div className="score-block">
              <strong>{alert.severityScore.toFixed(1)}</strong>
              <span>{alert.severityLevel}</span>
            </div>
            <span className="confidence-pill">{alert.confidenceLevel}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
