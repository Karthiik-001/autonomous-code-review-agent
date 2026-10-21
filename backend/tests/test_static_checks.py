from app.static_checks import analyze_source


def test_detects_narrowly_defined_risky_calls() -> None:
    findings = analyze_source(
        "eval(user_input)\n"
        "exec(code)\n"
        "os.system(command)\n"
        "subprocess.run(command)\n"
        "subprocess.Popen(command)\n"
        "pickle.load(handle)\n"
        "pickle.loads(payload)\n"
        "try:\n"
        "    work()\n"
        "except:\n"
        "    recover()\n"
    )

    assert len(findings) == 8
    assert [finding.line_start for finding in findings] == [1, 2, 3, 4, 5, 6, 7, 10]
    assert [finding.severity for finding in findings[:7]] == [
        "high",
        "high",
        "high",
        "medium",
        "medium",
        "high",
        "high",
    ]
    assert findings[7].severity == "low"


def test_detects_mutable_default_arguments_with_accurate_lines() -> None:
    findings = analyze_source(
        "def collect(items=[]):\n"
        "    return items\n"
        "\n"
        "def configure(options: dict = {}):\n"
        "    return options\n"
    )

    assert len(findings) == 2
    assert [finding.line_start for finding in findings] == [1, 4]
    assert all(finding.severity == "medium" for finding in findings)


def test_returns_multiple_findings_in_source_order() -> None:
    findings = analyze_source(
        "value = eval(data)\n"
        "def f(values=[]):\n"
        "    excepted = True\n"
        "    return values\n"
    )

    assert [finding.line_start for finding in findings] == [1, 2]


def test_returns_no_findings_for_clean_input() -> None:
    assert analyze_source("def add(left, right):\n    return left + right\n") == []


def test_ignores_comments_and_strings() -> None:
    findings = analyze_source(
        "# eval(value); os.system(command)\n"
        "text = 'exec(code) and pickle.loads(data)'\n"
        'doc = """subprocess.run(command)\\nexcept:"""\n'
    )

    assert findings == []


def test_handles_malformed_source_without_crashing() -> None:
    assert analyze_source("if True:\n    value = 1\n  other = 2\n") == []


def test_handles_unterminated_string_without_crashing() -> None:
    assert analyze_source('value = "unterminated\n') == []


def test_detects_qualified_call_split_by_explicit_line_continuation() -> None:
    findings = analyze_source("subprocess.\\\n    run(command)\n")

    assert len(findings) == 1
    assert findings[0].title == "External command through subprocess.run"
    assert findings[0].line_start == 1


def test_reports_multiline_mutable_default_start_line() -> None:
    findings = analyze_source(
        "def collect(\n"
        "    items=[\n"
        "        1,\n"
        "    ],\n"
        "):\n"
        "    return items\n"
    )

    assert len(findings) == 1
    assert findings[0].line_start == 2


def test_detects_list_default_with_newline_after_equals() -> None:
    findings = analyze_source(
        "def collect(items =\n"
        "    []):\n"
        "    return items\n"
    )

    assert len(findings) == 1
    assert findings[0].title == "Mutable list used as a default argument"
    assert findings[0].line_start == 2


def test_detects_dictionary_default_with_newline_after_equals() -> None:
    findings = analyze_source(
        "def configure(options =\n"
        "    {}):\n"
        "    return options\n"
    )

    assert len(findings) == 1
    assert findings[0].title == "Mutable dictionary used as a default argument"
    assert findings[0].line_start == 2
