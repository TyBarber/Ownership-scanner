import type { OwnershipRelationship } from "../api/types";

export function relationshipLabel(
  relationship: OwnershipRelationship["relationship_type"],
): string {
  switch (relationship) {
    case "owned_by":
      return "Owned by";
    case "controlled_by_group":
      return "Controlled by group";
    case "affiliated_with_group":
      return "Affiliated with group";
  }
}

export function entityTypeLabel(
  type: "brand" | "company" | "ownership_group",
  companyType?: string,
): string {
  if (companyType === "cooperative") return "Cooperative";
  if (type === "ownership_group") return "Ownership group";
  if (type === "brand") return "Brand";
  return "Company";
}

export function formatEffectiveDate(
  value: string | null,
  precision: OwnershipRelationship["effective_from_precision"],
): string {
  if (!value) return "Effective date not established";
  if (precision === "year") return `Since ${value}`;
  if (precision === "month") {
    const [year, month] = value.split("-").map(Number);
    return `Since ${new Intl.DateTimeFormat("en-US", {
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    }).format(new Date(Date.UTC(year, month - 1, 1)))}`;
  }
  if (precision === "day") {
    const [year, month, day] = value.split("-").map(Number);
    return `Since ${new Intl.DateTimeFormat("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
      timeZone: "UTC",
    }).format(new Date(Date.UTC(year, month - 1, day)))}`;
  }
  return `Effective ${value}`;
}

export function formatDate(value: string): string {
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) return value;
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, day)));
}
