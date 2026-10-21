import type { ReviewRequest, ReviewResponse } from "./types";

export class ReviewApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ReviewApiError";
  }
}

function backendDetail(body: unknown): string | null {
  if (!body || typeof body !== "object" || !("detail" in body)) {
    return null;
  }

  const detail = body.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return "Please check the submitted fields.";
  return null;
}

export async function submitReview(request: ReviewRequest): Promise<ReviewResponse> {
  let response: Response;
  try {
    response = await fetch("/api/reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    throw new ReviewApiError(
      "Could not reach the review service. Check that the backend is running.",
    );
  }

  const contentType = response.headers.get("Content-Type") ?? "";
  if (!contentType.toLowerCase().includes("application/json")) {
    throw new ReviewApiError(
      "The frontend proxy returned a web page instead of review JSON. Restart the Vite server and try again.",
    );
  }

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    throw new ReviewApiError("The review service returned an unreadable response.");
  }

  if (!response.ok) {
    if (response.status === 422) {
      const detail = backendDetail(body);
      throw new ReviewApiError(
        detail
          ? `The backend rejected the request: ${detail}.`
          : "The backend rejected the request. Check the submitted fields.",
      );
    }
    if (response.status === 503) {
      throw new ReviewApiError("The review service is unavailable. Try again shortly.");
    }
    throw new ReviewApiError("The review service returned an unexpected error.");
  }

  return body as ReviewResponse;
}
