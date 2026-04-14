import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ThemeToggle from "../components/ThemeToggle";

describe("ThemeToggle", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
  });

  it("renders the toggle button", () => {
    render(<ThemeToggle />);
    const btn = screen.getByRole("button");
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveClass("theme-toggle-btn");
  });

  it("defaults to dark theme (shows sun icon to switch)", () => {
    render(<ThemeToggle />);
    // In dark mode, shows ☀️ icon (to switch to light)
    expect(screen.getByText("☀️")).toBeInTheDocument();
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("toggles to light theme on click", () => {
    render(<ThemeToggle />);
    fireEvent.click(screen.getByRole("button"));
    // In light mode, shows 🌙 (to switch to dark)
    expect(screen.getByText("🌙")).toBeInTheDocument();
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("persists theme to localStorage", () => {
    render(<ThemeToggle />);
    fireEvent.click(screen.getByRole("button"));
    expect(localStorage.getItem("sg-theme")).toBe("light");
  });

  it("loads saved light theme from localStorage", () => {
    localStorage.setItem("sg-theme", "light");
    render(<ThemeToggle />);
    // When light is saved, icon should be 🌙
    expect(screen.getByText("🌙")).toBeInTheDocument();
  });

  it("toggles back to dark on double-click", () => {
    render(<ThemeToggle />);
    const btn = screen.getByRole("button");
    fireEvent.click(btn); // dark -> light
    fireEvent.click(btn); // light -> dark
    expect(screen.getByText("☀️")).toBeInTheDocument();
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("has correct aria-label", () => {
    render(<ThemeToggle />);
    expect(screen.getByLabelText("Toggle theme")).toBeInTheDocument();
  });
});
