export type ApiErrorKind =
  | "invalid-gtin"
  | "not-researched"
  | "validation"
  | "timeout"
  | "network"
  | "server"
  | "invalid-response";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;

  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
  }
}

export function publicErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return "Something went wrong while loading this information.";
  }

  switch (error.kind) {
    case "invalid-gtin":
      return "That barcode is not a valid GTIN.";
    case "not-researched":
      return "We have not researched this product yet.";
    case "validation":
      return "The request could not be processed.";
    case "timeout":
      return "The request took too long. Please try again.";
    case "network":
      return "We could not reach the ownership service. Check your connection and try again.";
    case "server":
      return "The ownership service is temporarily unavailable.";
    case "invalid-response":
      return "The ownership service returned information we could not safely display.";
  }
}
