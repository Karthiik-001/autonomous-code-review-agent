import pytest

from app.review_service import (
    MockReviewProvider,
    ReviewProvider,
    ReviewProviderError,
    ReviewService,
    ReviewServiceError,
)
from app.schemas import ReviewRequest


def test_mock_provider_returns_deterministic_demo_findings() -> None:
    service = ReviewService({ReviewRequest(source="print('hello')").mode: MockReviewProvider()})

    first_response = service.review(ReviewRequest(source="print('hello')"))
    second_response = service.review(ReviewRequest(source="different = True"))

    assert first_response == second_response
    assert first_response.mode == "mock"
    assert len(first_response.findings) == 1
    assert first_response.findings[0].severity == "info"


class RecordingProvider:
    def __init__(self) -> None:
        self.received_request: ReviewRequest | None = None

    def review(self, request: ReviewRequest) -> dict[str, object]:
        self.received_request = request
        return {
            "language": "python",
            "mode": "demo",
            "findings": [],
        }


def test_service_injects_request_into_selected_provider() -> None:
    provider = RecordingProvider()
    service = ReviewService({"demo": provider})
    request = ReviewRequest(source="value = 1", mode="demo")

    response = service.review(request)

    assert provider.received_request is request
    assert response.language == "python"
    assert response.mode == "demo"
    assert response.findings == []


class MalformedProvider:
    def review(self, request: ReviewRequest) -> dict[str, object]:
        return {
            "language": "python",
            "mode": "mock",
            "findings": [{"severity": "not-a-severity"}],
        }


def test_service_rejects_malformed_provider_output() -> None:
    service = ReviewService({"mock": MalformedProvider()})

    with pytest.raises(ReviewServiceError, match="invalid response"):
        service.review(ReviewRequest(source="value = 1"))


def test_service_reports_when_no_provider_is_configured() -> None:
    service = ReviewService({})

    with pytest.raises(ReviewServiceError, match="No review provider configured"):
        service.review(ReviewRequest(source="value = 1", mode="ai"))


class FailingProvider:
    def review(self, request: ReviewRequest) -> object:
        raise ReviewProviderError("provider is unavailable")


def test_service_reports_provider_failures() -> None:
    service = ReviewService({"mock": FailingProvider()})

    with pytest.raises(ReviewServiceError, match="Review provider failed"):
        service.review(ReviewRequest(source="value = 1"))


def test_provider_protocol_describes_the_adapter_boundary() -> None:
    assert isinstance(MockReviewProvider(), ReviewProvider)
