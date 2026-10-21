"""The FastAPI entry point for the local code review application."""

from fastapi import FastAPI, HTTPException, status

from app.review_service import MockReviewProvider, ReviewService, ReviewServiceError
from app.schemas import ReviewRequest, ReviewResponse

app = FastAPI(
    title="Autonomous Code Review Agent",
    description="A local API for reviewing small Python source files.",
)

review_service = ReviewService(
    {
        "mock": MockReviewProvider(),
        "demo": MockReviewProvider(),
    }
)


@app.get("/health")
def health() -> dict[str, str]:
    """Report whether the backend process is available."""
    return {"status": "ok"}


@app.post("/api/reviews", response_model=ReviewResponse)
def create_review(request: ReviewRequest) -> ReviewResponse:
    """Validate a request and return the selected provider's structured result."""
    try:
        return review_service.review(request)
    except ReviewServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
