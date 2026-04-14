import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PlatformCard from "../components/PlatformCard";

// PlatformCard uses { platform, config, onClick } props
const mockConfig = {
  name: "Instagram",
  icon: "📸",
  color: "#E4405F",
  description: "Detect fake Instagram profiles",
};

describe("PlatformCard", () => {
  it("renders platform name", () => {
    render(<PlatformCard platform="instagram" config={mockConfig} onClick={() => {}} />);
    expect(screen.getByText("Instagram")).toBeInTheDocument();
  });

  it("renders the description", () => {
    render(<PlatformCard platform="instagram" config={mockConfig} onClick={() => {}} />);
    expect(screen.getByText("Detect fake Instagram profiles")).toBeInTheDocument();
  });

  it("calls onClick with platform id when clicked", () => {
    let clickedPlatform = null;
    render(
      <PlatformCard
        platform="instagram"
        config={mockConfig}
        onClick={(p) => (clickedPlatform = p)}
      />
    );
    fireEvent.click(screen.getByText("Instagram"));
    expect(clickedPlatform).toBe("instagram");
  });

  it("applies platform color as CSS variable", () => {
    const { container } = render(
      <PlatformCard platform="instagram" config={mockConfig} onClick={() => {}} />
    );
    const card = container.firstChild;
    expect(card.style.getPropertyValue("--platform-color")).toBe("#E4405F");
  });

  it("has correct id attribute", () => {
    const { container } = render(
      <PlatformCard platform="instagram" config={mockConfig} onClick={() => {}} />
    );
    expect(container.querySelector("#platform-instagram")).toBeInTheDocument();
  });
});
