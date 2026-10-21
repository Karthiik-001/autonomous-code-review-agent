import pytest
from pydantic import ValidationError

from app.schemas import (
    MAX_SOURCE_BYTES,
    FindingSeverity,
    ReviewFinding,
    ReviewMode,
    ReviewRequest,
    ReviewResponse,
)


def test_valid_review_request_and_response_can_be_created() -> None:
    request = ReviewRequest(
        source="print('hello')",
        filename="example.py",
        language="python",
        mode="mock",
    )
    finding = ReviewFinding(
        severity="medium",
        title="Check input handling",
        explanation="Input should be validated before it is used.",
        line_start=1,
        line_end=2,
        suggested_fix="Validate the input before using it.",
        confidence=0.8,
    )
    response = ReviewResponse(
        language=request.language,
        mode=request.mode,
        findings=[finding],
    )

    assert request.source == "print('hello')"
    assert response.findings[0].severity == FindingSeverity.medium
    assert response.mode == ReviewMode.mock


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "   "),
        ("filename", "notes.txt"),
        ("language", "javascript"),
        ("mode", "unknown"),
    ],
)
def test_review_request_rejects_invalid_field_values(
    field: str, value: str
) -> None:
    with pytest.raises(ValidationError):
        payload = {"source": "print('hello')"}
        payload[field] = value
        ReviewRequest(**payload)


def test_review_request_rejects_oversized_utf8_source() -> None:
    source = "é" * (MAX_SOURCE_BYTES // len("é".encode("utf-8")) + 1)

    with pytest.raises(ValidationError):
        ReviewRequest(source=source)


def test_review_models_reject_invalid_finding_values() -> None:
    with pytest.raises(ValidationError):
        ReviewFinding(
            severity="urgent",
            title="A title",
            explanation="An explanation",
        )

    with pytest.raises(ValidationError):
        ReviewFinding(
            severity="low",
            title="A title",
            explanation="An explanation",
            line_start=4,
            line_end=2,
        )

    with pytest.raises(ValidationError):
        ReviewFinding(
            severity="low",
            title="A title",
            explanation="An explanation",
            confidence=1.1,
        )


def test_review_models_serialize_to_documented_field_names() -> None:
    request = ReviewRequest(source="print('hello')")
    response = ReviewResponse(
        language="python",
        mode="demo",
        findings=[
            ReviewFinding(
                severity="info",
                title="No issue identified",
                explanation="This is an example finding.",
            )
        ],
    )

    assert request.model_dump() == {
        "source": "print('hello')",
        "filename": "review.py",
        "language": "python",
        "mode": "mock",
    }
    assert response.model_dump() == {
        "language": "python",
        "mode": "demo",
        "findings": [
            {
                "severity": "info",
                "title": "No issue identified",
                "explanation": "This is an example finding.",
                "line_start": None,
                "line_end": None,
                "suggested_fix": None,
                "confidence": None,
            }
        ],
    }
