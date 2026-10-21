"""Small deterministic checks for common Python review hazards.

These checks inspect source tokens only. They are intentionally narrow and are
not a complete Python security or correctness analysis.
"""

from __future__ import annotations

import io
import tokenize
from collections.abc import Iterable

from app.schemas import ReviewFinding


def analyze_source(source: str) -> list[ReviewFinding]:
    """Return findings for a small set of recognizable source patterns."""
    tokens = _tokenize_source(source)
    findings: list[ReviewFinding] = []

    findings.extend(_find_risky_calls(tokens))
    findings.extend(_find_bare_excepts(tokens))
    findings.extend(_find_mutable_defaults(tokens))
    findings.sort(key=lambda finding: (finding.line_start or 0, finding.title))
    return findings


def _tokenize_source(source: str) -> list[tokenize.TokenInfo]:
    token_stream = tokenize.generate_tokens(io.StringIO(source).readline)
    tokens: list[tokenize.TokenInfo] = []
    try:
        for token in token_stream:
            tokens.append(token)
    except (IndentationError, tokenize.TokenError):
        return tokens
    return tokens


def _find_risky_calls(tokens: list[tokenize.TokenInfo]) -> Iterable[ReviewFinding]:
    patterns = {
        ("eval", "("): "Use of eval(...) can execute input as Python code.",
        ("exec", "("): "Use of exec(...) can execute input as Python code.",
        ("os", ".", "system", "("): "os.system(...) invokes a system shell command.",
        (
            "subprocess",
            ".",
            "run",
            "(",
        ): "subprocess.run(...) can execute an external command.",
        (
            "subprocess",
            ".",
            "Popen",
            "(",
        ): "subprocess.Popen(...) can execute an external command.",
        ("pickle", ".", "load", "("): "pickle.load(...) deserializes untrusted data.",
        (
            "pickle",
            ".",
            "loads",
            "(",
        ): "pickle.loads(...) deserializes untrusted data.",
    }
    metadata = {
        "eval": (
            "Dynamic evaluation with eval",
            "high",
            "Avoid eval; parse input as data or use an explicit allowlist.",
        ),
        "exec": (
            "Dynamic execution with exec",
            "high",
            "Avoid exec; replace it with explicit, non-code execution logic.",
        ),
        "os.system": (
            "Shell command through os.system",
            "high",
            "Avoid os.system; pass a vetted argument list to a safer process API.",
        ),
        "subprocess.run": (
            "External command through subprocess.run",
            "medium",
            "Validate command arguments and prefer a fixed executable with shell=False.",
        ),
        "subprocess.Popen": (
            "External command through subprocess.Popen",
            "medium",
            "Validate command arguments and prefer a fixed executable with shell=False.",
        ),
        "pickle.load": (
            "Unsafe pickle deserialization",
            "high",
            "Do not load untrusted pickle data; use a constrained data format instead.",
        ),
        "pickle.loads": (
            "Unsafe pickle deserialization",
            "high",
            "Do not load untrusted pickle data; use a constrained data format instead.",
        ),
    }
    findings: list[ReviewFinding] = []
    for index, token in enumerate(tokens):
        for pattern, explanation in patterns.items():
            if _matches_pattern(tokens, index, pattern):
                key = ".".join(value for value in pattern if value not in {".", "("})
                title, severity, suggested_fix = metadata[key]
                findings.append(
                    ReviewFinding(
                        severity=severity,
                        title=title,
                        explanation=explanation,
                        line_start=token.start[0],
                        line_end=token.start[0],
                        suggested_fix=suggested_fix,
                        confidence=0.98,
                    )
                )
    return findings


def _find_bare_excepts(tokens: list[tokenize.TokenInfo]) -> Iterable[ReviewFinding]:
    findings: list[ReviewFinding] = []
    for index, token in enumerate(tokens[:-1]):
        if token.type == tokenize.NAME and token.string == "except":
            next_token = tokens[index + 1]
            if next_token.type == tokenize.OP and next_token.string == ":":
                findings.append(
                    ReviewFinding(
                        severity="low",
                        title="Bare except catches every exception",
                        explanation=(
                            "A bare except hides the exception type and also catches "
                            "interrupts such as KeyboardInterrupt."
                        ),
                        line_start=token.start[0],
                        line_end=token.start[0],
                        suggested_fix="Catch the specific exception types the code can handle.",
                        confidence=0.99,
                    )
                )
    return findings


def _find_mutable_defaults(tokens: list[tokenize.TokenInfo]) -> Iterable[ReviewFinding]:
    findings: list[ReviewFinding] = []
    for index, token in enumerate(tokens):
        if token.type != tokenize.NAME or token.string != "def":
            continue
        opening_index = _next_token_index(tokens, index + 1, "(")
        if opening_index is None:
            continue
        closing_index = _matching_delimiter_index(tokens, opening_index, "(", ")")
        if closing_index is None:
            continue
        parameter_depth = 0
        for parameter_index in range(opening_index + 1, closing_index):
            parameter_token = tokens[parameter_index]
            if parameter_token.string in "([{":
                parameter_depth += 1
            elif parameter_token.string in ")]}":
                parameter_depth -= 1
            elif (
                parameter_token.type == tokenize.OP
                and parameter_token.string == "="
                and parameter_depth == 0
            ):
                next_index = parameter_index + 1
                while (
                    next_index < closing_index
                    and _is_explicit_continuation(tokens[next_index])
                ):
                    next_index += 1
                if next_index < closing_index and tokens[next_index].string in "[{":
                    kind = "list" if tokens[next_index].string == "[" else "dictionary"
                    default_line = tokens[next_index].start[0]
                    findings.append(
                        ReviewFinding(
                            severity="medium",
                            title=f"Mutable {kind} used as a default argument",
                            explanation=(
                                f"A mutable {kind} default is shared by every call "
                                "to the function."
                            ),
                            line_start=default_line,
                            line_end=default_line,
                            suggested_fix=(
                                "Use None as the default and create a new mutable "
                                "value inside the function."
                            ),
                            confidence=0.97,
                        )
                    )
    return findings


def _matches_pattern(
    tokens: list[tokenize.TokenInfo], start: int, pattern: tuple[str, ...]
) -> bool:
    token_index = start
    for value in pattern:
        while token_index < len(tokens) and _is_explicit_continuation(tokens[token_index]):
            token_index += 1
        if token_index >= len(tokens) or tokens[token_index].string != value:
            return False
        token_index += 1
    return True


def _is_explicit_continuation(token: tokenize.TokenInfo) -> bool:
    return token.string == "\\" or token.type == tokenize.NL


def _next_token_index(
    tokens: list[tokenize.TokenInfo], start: int, value: str
) -> int | None:
    for index in range(start, len(tokens)):
        if tokens[index].string == value:
            return index
    return None


def _matching_delimiter_index(
    tokens: list[tokenize.TokenInfo], opening_index: int, opening: str, closing: str
) -> int | None:
    depth = 0
    for index in range(opening_index, len(tokens)):
        if tokens[index].string == opening:
            depth += 1
        elif tokens[index].string == closing:
            depth -= 1
            if depth == 0:
                return index
    return None
