from fastapi.testclient import TestClient

import app.main as main
from app.review_service import ReviewProviderError, ReviewService
from app.schemas import MAX_SOURCE_BYTES


client = TestClient(main.app)


def test_review_endpoint_returns_mock_findings() -> None:
    response = client.post(
        "/api/reviews",
        json={"source": "value = eval(user_input)", "mode": "mock"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "python"
    assert body["mode"] == "mock"
    assert len(body["findings"]) == 1
    assert body["findings"][0]["title"] == "Dynamic evaluation with eval"


def test_review_endpoint_returns_demo_findings() -> None:
    response = client.post(
        "/api/reviews",
        json={"source": "value = 1", "mode": "demo"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "demo"
    assert response.json()["findings"] == []


def test_review_endpoint_rejects_invalid_request() -> None:
    response = client.post(
        "/api/reviews",
        json={"source": "print('hello')", "language": "javascript"},
    )

    assert response.status_code == 422


def test_review_endpoint_rejects_oversized_source() -> None:
    response = client.post(
        "/api/reviews",
        json={"source": "x" * (MAX_SOURCE_BYTES + 1)},
    )

    assert response.status_code == 422


def test_review_endpoint_reports_unavailable_provider() -> None:
    original_service = main.review_service
    main.review_service = ReviewService({})
    try:
        response = client.post(
            "/api/reviews",
            json={"source": "print('hello')", "mode": "ai"},
        )
    finally:
        main.review_service = original_service

    assert response.status_code == 503
    assert response.json() == {
        "detail": "No review provider configured for mode 'ai'."
    }


class FailingProvider:
    def review(self, request: object) -> object:
        raise ReviewProviderError("provider is unavailable")


def test_review_endpoint_reports_provider_failure() -> None:
    original_service = main.review_service
    main.review_service = ReviewService({"mock": FailingProvider()})
    try:
        response = client.post(
            "/api/reviews",
            json={"source": "print('hello')", "mode": "mock"},
        )
    finally:
        main.review_service = original_service

    assert response.status_code == 503
    assert response.json() == {"detail": "Review provider failed."}
