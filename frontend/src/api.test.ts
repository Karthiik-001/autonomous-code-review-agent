import { afterEach, describe, expect, it, vi } from "vitest";
import { ReviewApiError, submitReview } from "./api";

afterEach(() => {
  vi.restoreAllMocks();
});

const responseBody = {
  language: "python",
  mode: "mock",
  findings: [
    {
      severity: "info",
      title: "Demo finding",
      explanation: "This came from the backend.",
      line_start: null,
      line_end: null,
      suggested_fix: null,
      confidence: null,
    },
  ],
};

describe("submitReview", () => {
  it("sends the documented request and returns the backend response", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(responseBody), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const response = await submitReview({
      source: "print('hello')",
      filename: "example.py",
      language: "python",
      mode: "mock",
    });

    expect(fetchMock).toHaveBeenCalledWith("/api/reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: "print('hello')",
        filename: "example.py",
        language: "python",
        mode: "mock",
      }),
    });
    expect(response).toEqual(responseBody);
  });

  it("turns backend validation errors into a useful message", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "source must contain Python code" }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(submitReview({
      source: " ",
      filename: "example.py",
      language: "python",
      mode: "mock",
    })).rejects.toEqual(
      new ReviewApiError("The backend rejected the request: source must contain Python code."),
    );
  });

  it("reports unavailable services and network failures clearly", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Review provider failed." }), {
        status: 503,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await expect(submitReview({
      source: "print('hello')",
      filename: "example.py",
      language: "python",
      mode: "mock",
    })).rejects.toEqual(
      new ReviewApiError("The review service is unavailable. Try again shortly."),
    );

    vi.restoreAllMocks();
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("offline"));

    await expect(submitReview({
      source: "print('hello')",
      filename: "example.py",
      language: "python",
      mode: "mock",
    })).rejects.toEqual(
      new ReviewApiError("Could not reach the review service. Check that the backend is running."),
    );
  });

  it("explains when the frontend proxy returns a non-JSON page", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("<!doctype html><html></html>", {
        status: 200,
        headers: { "Content-Type": "text/html" },
      }),
    );

    await expect(submitReview({
      source: "print('hello')",
      filename: "example.py",
      language: "python",
      mode: "mock",
    })).rejects.toEqual(
      new ReviewApiError(
        "The frontend proxy returned a web page instead of review JSON. Restart the Vite server and try again.",
      ),
    );
  });
});
