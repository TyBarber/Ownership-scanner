import { beforeEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";
import { requestJson } from "./client";
import { ApiError } from "./errors";

const schema = z.object({ ok: z.literal(true) });

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("API client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("validates successful JSON", async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse({ ok: true }));
    await expect(requestJson("/test", schema)).resolves.toEqual({ ok: true });
  });

  it("maps 400, 404, and 422 without retrying", async () => {
    for (const [status, kind] of [
      [400, "invalid-gtin"],
      [404, "not-researched"],
      [422, "validation"],
    ] as const) {
      vi.mocked(fetch).mockReset();
      vi.mocked(fetch).mockResolvedValue(
        jsonResponse({ detail: "Public detail" }, status),
      );
      await expect(requestJson("/test", schema)).rejects.toMatchObject({
        kind,
        status,
      });
      expect(fetch).toHaveBeenCalledTimes(1);
    }
  });

  it("retries one server failure and then succeeds", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ detail: "failure" }, 500))
      .mockResolvedValueOnce(jsonResponse({ ok: true }));
    await expect(requestJson("/test", schema)).resolves.toEqual({ ok: true });
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("maps a repeated server failure after one retry", async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse({}, 500));
    await expect(requestJson("/test", schema)).rejects.toMatchObject({
      kind: "server",
    });
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("retries one network failure and returns a public network error", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("private network detail"));
    await expect(requestJson("/test", schema)).rejects.toMatchObject({
      kind: "network",
    });
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("times out stalled requests after one controlled retry", async () => {
    vi.useFakeTimers();
    vi.mocked(fetch).mockImplementation((_input, init) => {
      return new Promise((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () => {
          reject(new DOMException("aborted", "AbortError"));
        });
      });
    });

    const request = requestJson("/test", schema);
    const rejection = expect(request).rejects.toMatchObject({ kind: "timeout" });
    await vi.advanceTimersByTimeAsync(16_000);
    await rejection;
    expect(fetch).toHaveBeenCalledTimes(2);
    vi.useRealTimers();
  });

  it("rejects invalid JSON and schema mismatches", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response("not-json", { status: 200 }),
    );
    await expect(requestJson("/test", schema)).rejects.toMatchObject({
      kind: "invalid-response",
    });

    vi.mocked(fetch).mockResolvedValueOnce(jsonResponse({ ok: false }));
    await expect(requestJson("/test", schema)).rejects.toBeInstanceOf(ApiError);
  });
});
