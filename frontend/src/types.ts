export type FindingSeverity = "critical" | "high" | "medium" | "low" | "info";

export type ReviewMode = "mock" | "demo" | "ai";

export interface ReviewRequest {
  source: string;
  filename: string;
  language: "python";
  mode: ReviewMode;
}

export interface ReviewFinding {
  severity: FindingSeverity;
  title: string;
  explanation: string;
  line_start?: number | null;
  line_end?: number | null;
  suggested_fix?: string | null;
  confidence?: number | null;
}

export interface ReviewResponse {
  language: "python";
  mode: ReviewMode;
  findings: ReviewFinding[];
}
