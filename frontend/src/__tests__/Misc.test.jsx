import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Footer from "../components/Footer";
import ErrorBoundary from "../components/ErrorBoundary";

describe("Footer", () => {
  it("renders footer text", () => {
    render(<Footer />);
    expect(screen.getByText(/SocialGuard/i)).toBeInTheDocument();
  });
});

function BrokenComponent() {
  throw new Error("Test crash");
}

describe("ErrorBoundary", () => {
  // Suppress console.error for expected crashes
  const spy = vi.spyOn(console, "error").mockImplementation(() => {});

  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <div>Safe Content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText("Safe Content")).toBeInTheDocument();
  });

  it("renders fallback on error", () => {
    render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  afterAll(() => spy.mockRestore());
});
