import { describe, expect, it } from "vitest";
import { MAX_SOURCE_BYTES, validateFile, validateSource } from "./validation";

describe("validateSource", () => {
  it("rejects empty source", () => {
    expect(validateSource("   ", "review.py")).toEqual({
      valid: false,
      message: "Paste Python code or choose a .py file before reviewing.",
    });
  });

  it("rejects source larger than the 50 KB limit", () => {
    const source = "a".repeat(MAX_SOURCE_BYTES + 1);

    expect(validateSource(source, "review.py")).toEqual({
      valid: false,
      message: "The source file must be 50 KB or smaller.",
    });
  });

  it("rejects unsupported file names", () => {
    expect(validateSource("print('hello')", "notes.txt")).toEqual({
      valid: false,
      message: "Choose a Python file ending in .py.",
    });
  });

  it("accepts a small Python source file", () => {
    expect(validateSource("print('hello')", "review.py")).toEqual({
      valid: true,
    });
  });

  it("rejects an oversized Python file before reading it", () => {
    expect(validateFile("review.py", MAX_SOURCE_BYTES + 1)).toEqual({
      valid: false,
      message: "The source file must be 50 KB or smaller.",
    });
  });
});
