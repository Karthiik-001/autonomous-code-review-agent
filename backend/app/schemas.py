"""Validated data shapes shared by the future review route and service."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_SOURCE_BYTES = 50 * 1024


class FindingSeverity(str, Enum):
    """The possible levels of concern for a review finding."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class ReviewMode(str, Enum):
    """The review source selected by the caller."""

    mock = "mock"
    demo = "demo"
    ai = "ai"


class ReviewRequest(BaseModel):
    """The Python source and metadata submitted for a future review."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    source: str = Field(min_length=1)
    filename: str = Field(default="review.py", min_length=1, max_length=255)
    language: Literal["python"] = "python"
    mode: ReviewMode = ReviewMode.mock

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source must contain Python code")
        if len(value.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise ValueError("source must be 50 KB or smaller")
        return value

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        if not value.lower().endswith(".py"):
            raise ValueError("filename must end with .py")
        return value


class ReviewFinding(BaseModel):
    """One possible issue identified in submitted source code."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    severity: FindingSeverity
    title: str = Field(min_length=1, max_length=200)
    explanation: str = Field(min_length=1, max_length=4000)
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    suggested_fix: str | None = Field(default=None, max_length=4000)
    confidence: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def validate_line_range(self) -> "ReviewFinding":
        if (
            self.line_start is not None
            and self.line_end is not None
            and self.line_end < self.line_start
        ):
            raise ValueError("line_end must be greater than or equal to line_start")
        return self


class ReviewResponse(BaseModel):
    """The structured result returned after a review is performed."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    language: Literal["python"]
    mode: ReviewMode
    findings: list[ReviewFinding] = Field(default_factory=list)
