type OutcomeFormProps = {
  entityId: string;
  repId: string;
  recommendationId: string;
};

export function OutcomeForm({ entityId, repId, recommendationId }: OutcomeFormProps) {
  return (
    <form className="outcome-form">
      <div className="form-grid">
        <label>
          Recommendation ID
          <input readOnly value={recommendationId} />
        </label>
        <label>
          Entity ID
          <input readOnly value={entityId} />
        </label>
        <label>
          Rep ID
          <input readOnly value={repId} />
        </label>
        <label>
          Order Value
          <input min="0" placeholder="0" type="number" />
        </label>
      </div>
      <div className="toggle-grid">
        <label>
          <input defaultChecked type="checkbox" />
          Visit completed
        </label>
        <label>
          <input type="checkbox" />
          Recommendation followed
        </label>
        <label>
          <input type="checkbox" />
          Sale made
        </label>
        <label>
          <input type="checkbox" />
          Alert validated
        </label>
      </div>
      <label>
        Rep feedback
        <textarea placeholder="Capture field notes after the visit" rows={4} />
      </label>
      <button className="primary-button" type="button">
        Save outcome draft
      </button>
    </form>
  );
}
