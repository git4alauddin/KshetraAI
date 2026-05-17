type LoadingStateProps = {
  label?: string;
};

export function LoadingState({ label = "Loading backend intelligence" }: LoadingStateProps) {
  return (
    <div className="state-panel" role="status">
      <span className="loading-dot" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
