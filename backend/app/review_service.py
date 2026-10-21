"""Review orchestration and provider interfaces.

Providers receive source as text only. This module never executes or imports it.
"""

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from pydantic import ValidationError

from app.schemas import ReviewRequest, ReviewResponse
from app.static_checks import analyze_source


class ReviewServiceError(Exception):
    """A review could not be completed with a valid structured response."""


class ReviewProviderError(Exception):
    """A provider could not produce a response."""


@runtime_checkable
class ReviewProvider(Protocol):
    """The small interface that any future review adapter must implement."""

    def review(self, request: ReviewRequest) -> ReviewResponse | Mapping[str, object]:
        """Return a response candidate for the submitted request."""


class MockReviewProvider:
    """Return deterministic local static-check results without network access."""

    def review(self, request: ReviewRequest) -> ReviewResponse:
        return ReviewResponse(
            language="python",
            mode=request.mode,
            findings=analyze_source(request.source),
        )


class ReviewService:
    """Select a provider, validate its output, and return a review response."""

    def __init__(self, providers: Mapping[str, ReviewProvider]) -> None:
        self._providers = providers

    def review(self, request: ReviewRequest) -> ReviewResponse:
        provider = self._providers.get(request.mode)
        if provider is None:
            raise ReviewServiceError(
                f"No review provider configured for mode '{request.mode}'."
            )

        try:
            response_candidate = provider.review(request)
        except ReviewProviderError as exc:
            raise ReviewServiceError("Review provider failed.") from exc

        try:
            return ReviewResponse.model_validate(response_candidate)
        except ValidationError as exc:
            raise ReviewServiceError(
                "Review provider returned an invalid response."
            ) from exc
