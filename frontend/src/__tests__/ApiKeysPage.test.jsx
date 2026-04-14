import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ApiKeysPage from "../components/ApiKeysPage";

// Mock auth and firebase
vi.mock("../components/AuthContext", () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => ({ user: { uid: "test-user", email: "test@test.com" } }),
}));

vi.mock("../firebase", () => ({
  auth: {},
}));

function renderPage() {
  return render(
    <MemoryRouter>
      <ApiKeysPage />
    </MemoryRouter>
  );
}

describe("ApiKeysPage", () => {
  it("renders the page heading", () => {
    renderPage();
    // Heading has emoji prefix, use getAllByText to handle multiple matches
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading.textContent).toContain("API Keys");
  });

  it("renders the generate key button", () => {
    renderPage();
    expect(screen.getByText(/Generate New Key/i)).toBeInTheDocument();
  });

  it("shows Quick Start documentation section", () => {
    renderPage();
    expect(screen.getByText(/Quick Start/i)).toBeInTheDocument();
  });

  it("lists the API endpoints", () => {
    renderPage();
    expect(screen.getByText(/Analyze a profile/i)).toBeInTheDocument();
  });

  it("shows empty state initially", () => {
    renderPage();
    expect(screen.getByText(/No API keys yet/i)).toBeInTheDocument();
  });

  it("generates a key when button is clicked", () => {
    renderPage();
    fireEvent.click(screen.getByText(/Generate New Key/i));
    expect(screen.getByText(/Copy/i)).toBeInTheDocument();
  });
});
