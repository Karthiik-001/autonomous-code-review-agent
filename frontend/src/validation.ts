export const MAX_SOURCE_BYTES = 50 * 1024;

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

export function validateFile(filename: string, sizeInBytes: number): ValidationResult {
  if (!filename.toLowerCase().endsWith(".py")) {
    return {
      valid: false,
      message: "Choose a Python file ending in .py.",
    };
  }

  if (sizeInBytes > MAX_SOURCE_BYTES) {
    return {
      valid: false,
      message: "The source file must be 50 KB or smaller.",
    };
  }

  return { valid: true };
}

export function validateSource(source: string, filename: string): ValidationResult {
  if (!source.trim()) {
    return {
      valid: false,
      message: "Paste Python code or choose a .py file before reviewing.",
    };
  }

  if (new TextEncoder().encode(source).byteLength > MAX_SOURCE_BYTES) {
    return {
      valid: false,
      message: "The source file must be 50 KB or smaller.",
    };
  }

  return validateFile(filename, new TextEncoder().encode(source).byteLength);
}
