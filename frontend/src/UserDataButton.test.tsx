// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import UserDataButton from "./UserDataButton";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("UserDataButton", () => {
  it("fetches user data when clicked and displays the user's name", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ name: "Ada Lovelace" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<UserDataButton />);

    fireEvent.click(screen.getByRole("button", { name: "Load user" }));

    expect(globalThis.fetch).toHaveBeenCalledWith("/api/user");
    expect(await screen.findByText("Ada Lovelace")).toBeTruthy();
  });

  it("shows a loading state while the request is pending", async () => {
    let resolveResponse: (response: Response) => void = () => undefined;
    vi.spyOn(globalThis, "fetch").mockReturnValue(
      new Promise((resolve) => {
        resolveResponse = resolve;
      }),
    );

    render(<UserDataButton />);
    fireEvent.click(screen.getByRole("button", { name: "Load user" }));

    expect(screen.getByRole("button", { name: "Loading..." })).toBeTruthy();
    resolveResponse(
      new Response(JSON.stringify({ name: "Grace Hopper" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    expect(await screen.findByText("Grace Hopper")).toBeTruthy();
  });

  it("shows an error when the request fails", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("offline"));

    render(<UserDataButton />);
    fireEvent.click(screen.getByRole("button", { name: "Load user" }));

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Could not load user data. Please try again.",
    );
  });
});
