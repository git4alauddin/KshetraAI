export function statusToneClass(value: string): string {
  const normalizedValue = value.trim().toLowerCase();
  if (["critical", "high"].includes(normalizedValue)) {
    return "status-badge status-badge-high";
  }
  if (["medium", "moderate"].includes(normalizedValue)) {
    return "status-badge status-badge-medium";
  }
  if (normalizedValue === "low") {
    return "status-badge status-badge-low";
  }
  return "status-badge";
}
