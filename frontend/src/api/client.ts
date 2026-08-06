import type { ZodType } from "zod";
import { ApiError } from "./errors";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "/api"
).replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 8_000;

type RequestOptions = {
  signal?: AbortSignal;
};

async function fetchOnce(
  path: string,
  signal?: AbortSignal,
): Promise<Response> {
  const timeoutController = new AbortController();
  const timeoutId = window.setTimeout(
    () => timeoutController.abort("timeout"),
    REQUEST_TIMEOUT_MS,
  );
  const combinedSignal = signal
    ? AbortSignal.any([signal, timeoutController.signal])
    : timeoutController.signal;

  try {
    return await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: "application/json" },
      signal: combinedSignal,
    });
  } catch (error) {
    if (signal?.aborted) {
      throw error;
    }
    if (timeoutController.signal.aborted) {
      throw new ApiError("timeout", "Request timed out");
    }
    throw new ApiError("network", "Network request failed");
  } finally {
    window.clearTimeout(timeoutId);
  }
}

async function responseDetail(response: Response): Promise<string | undefined> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    return typeof payload.detail === "string" ? payload.detail : undefined;
  } catch {
    return undefined;
  }
}

export async function requestJson<T>(
  path: string,
  schema: ZodType<T>,
  options: RequestOptions = {},
): Promise<T> {
  let response: Response | undefined;
  let lastError: unknown;

  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      response = await fetchOnce(path, options.signal);
    } catch (error) {
      if (options.signal?.aborted) {
        throw error;
      }
      lastError = error;
      if (attempt === 0) continue;
      throw error;
    }

    if (response.ok) break;
    if (response.status >= 500 && attempt === 0) continue;
    break;
  }

  if (!response) {
    throw lastError ?? new ApiError("network", "Network request failed");
  }

  if (!response.ok) {
    const detail = await responseDetail(response);
    if (response.status === 400) {
      throw new ApiError("invalid-gtin", detail ?? "Invalid GTIN", 400);
    }
    if (response.status === 404) {
      throw new ApiError("not-researched", detail ?? "Product not found", 404);
    }
    if (response.status === 422) {
      throw new ApiError("validation", "Request validation failed", 422);
    }
    throw new ApiError("server", "Server request failed", response.status);
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new ApiError("invalid-response", "Response was not valid JSON");
  }

  const parsed = schema.safeParse(payload);
  if (!parsed.success) {
    throw new ApiError("invalid-response", "Response did not match its schema");
  }
  return parsed.data;
}
