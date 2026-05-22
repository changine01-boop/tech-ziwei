export class RateLimitError extends Error {
  constructor() {
    super("Too many requests — please wait a moment and try again.");
    this.name = "RateLimitError";
  }
}

export class PaymentRequiredError extends Error {
  constructor() {
    super("payment_required");
    this.name = "PaymentRequiredError";
  }
}

export class NetworkError extends Error {
  constructor() {
    super("Network error — please check your connection.");
    this.name = "NetworkError";
  }
}

export function getErrorMessage(e: unknown): string {
  if (e instanceof RateLimitError) return e.message;
  if (e instanceof NetworkError) return e.message;
  if (e instanceof Error) return e.message;
  return "An unexpected error occurred.";
}
