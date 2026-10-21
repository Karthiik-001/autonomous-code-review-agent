import { useRef, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { submitReview, ReviewApiError } from "./api";
import type { ReviewFinding, ReviewResponse } from "./types";
import { validateFile, validateSource } from "./validation";

type ReviewStatus = "idle" | "loading" | "success" | "error";

function formatConfidence(confidence?: number | null): string {
  return confidence == null ? "" : `${Math.round(confidence * 100)}% confidence`;
}

function FindingCard({ finding }: { finding: ReviewFinding }) {
  const lineLabel =
    finding.line_start == null
      ? "Location not identified"
      : finding.line_end != null && finding.line_end !== finding.line_start
        ? `Lines ${finding.line_start}-${finding.line_end}`
        : `Line ${finding.line_start}`;

  return (
    <article className="finding-card">
      <div className="finding-heading">
        <span className={`severity severity-${finding.severity}`}>{finding.severity}</span>
        <span className="finding-location">{lineLabel}</span>
      </div>
      <h3>{finding.title}</h3>
      <p>{finding.explanation}</p>
      {finding.suggested_fix && (
        <p className="suggested-fix">
          <strong>Suggested next step:</strong> {finding.suggested_fix}
        </p>
      )}
      {finding.confidence != null && (
        <p className="confidence">{formatConfidence(finding.confidence)}</p>
      )}
    </article>
  );
}

function App() {
  const [source, setSource] = useState("");
  const [filename, setFilename] = useState("review.py");
  const [status, setStatus] = useState<ReviewStatus>("idle");
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState<ReviewResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileValidation = validateFile(file.name, file.size);
    if (!fileValidation.valid) {
      setSource("");
      setFilename("review.py");
      setStatus("error");
      setMessage(fileValidation.message ?? "Please choose a valid Python file.");
      setResponse(null);
      event.target.value = "";
      return;
    }

    setSource(await file.text());
    setFilename(file.name);
    setStatus("idle");
    setMessage("");
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const validation = validateSource(source, filename);

    if (!validation.valid) {
      setStatus("error");
      setMessage(validation.message ?? "Please check the submitted source.");
      return;
    }

    setStatus("loading");
    setMessage("");
    setResponse(null);

    try {
      const reviewResponse = await submitReview({
        source,
        filename,
        language: "python",
        mode: "mock",
      });
      setResponse(reviewResponse);
      setStatus("success");
    } catch (error) {
      setStatus("error");
      setMessage(
        error instanceof ReviewApiError
          ? error.message
          : "The review could not be completed. Please try again.",
      );
    }
  };

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">PORTFOLIO PROJECT</p>
        <h1>Python Review Assistant</h1>
        <p className="intro">
          Submit Python code or a <code>.py</code> file to receive structured code-review feedback.
          This tool performs deterministic, rule-based static analysis and never executes your code.
        </p>
      </section>

      <section className="mode-banner" aria-label="Review mode">
        <span className="mode-dot" aria-hidden="true" />
        <div>
          <strong>Static Python Analysis</strong>
          <p>Deterministic, token-based checks for common security and code-quality hazards.</p>
        </div>
      </section>

      <form className="review-form" onSubmit={handleSubmit}>
        <div className="form-heading">
          <div>
            <label htmlFor="source">Python source</label>
            <p>Paste code below or load one small <code>.py</code> file.</p>
          </div>
          <span className="limit-note">Maximum 50 KB</span>
        </div>
        <textarea
          id="source"
          value={source}
          onChange={(event) => setSource(event.target.value)}
          placeholder={"def greet(name):\n    return f\"Hello, {name}!\""}
          aria-describedby="source-help"
          disabled={status === "loading"}
        />
        <div className="input-actions">
          <input
            ref={fileInputRef}
            id="file"
            type="file"
            accept=".py,text/x-python"
            onChange={handleFileChange}
            hidden
          />
          <button
            className="secondary-button"
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={status === "loading"}
          >
            Choose .py file
          </button>
          <span id="source-help" className="filename">
            {filename}
          </span>
          <button className="primary-button" type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Reviewing..." : "Review source"}
          </button>
        </div>
      </form>

      {status === "error" && (
        <div className="status-message error-message" role="alert">
          <strong>We could not review that yet.</strong>
          <span>{message}</span>
        </div>
      )}
      {status === "loading" && (
        <div className="status-message loading-message" role="status">
          Analyzing source with local static checks...
        </div>
      )}

      {status === "success" && response && (
        <section className="results" aria-live="polite">
          <div className="results-heading">
            <div>
              <p className="eyebrow">REVIEW RESULTS</p>
              <h2>Possible issues to think about</h2>
            </div>
            <span className="result-mode">
              Static Analysis · {response.language}
            </span>
          </div>
          <p className="results-note">
            Identified via static token analysis. These rule-based findings highlight common security and quality hazards.
          </p>
          <div className="finding-list">
            {response.findings.length > 0 ? (
              response.findings.map((finding, index) => (
                <FindingCard key={`${finding.title}-${index}`} finding={finding} />
              ))
            ) : (
              <p className="empty-results">No issues detected by static rules. That does not prove the code is safe.</p>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
