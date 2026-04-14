import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ShapChart from "../components/ShapChart";

const mockImportances = [
  { feature: "profile_pic", importance: -2.84, direction: "genuine" },
  { feature: "follower_ratio", importance: -1.21, direction: "genuine" },
  { feature: "posts_per_follower", importance: 0.89, direction: "fake" },
  { feature: "bio_present", importance: -0.51, direction: "genuine" },
];

describe("ShapChart", () => {
  it("renders nothing when no importances provided", () => {
    const { container } = render(<ShapChart importances={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing for empty array", () => {
    const { container } = render(<ShapChart importances={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders the SHAP section with heading", () => {
    render(<ShapChart importances={mockImportances} />);
    // Actual heading text
    expect(screen.getByText(/Why This Prediction/i)).toBeInTheDocument();
  });

  it("renders the SHAP subtitle", () => {
    render(<ShapChart importances={mockImportances} />);
    expect(screen.getByText(/SHAP analysis/i)).toBeInTheDocument();
  });

  it("renders the legend items", () => {
    render(<ShapChart importances={mockImportances} />);
    expect(screen.getByText(/Increases Risk/i)).toBeInTheDocument();
    expect(screen.getByText(/Decreases Risk/i)).toBeInTheDocument();
  });

  it("renders the shap-section container", () => {
    const { container } = render(<ShapChart importances={mockImportances} />);
    expect(container.querySelector(".shap-section")).toBeInTheDocument();
  });

  it("renders a recharts container", () => {
    const { container } = render(<ShapChart importances={mockImportances} />);
    expect(container.querySelector(".recharts-responsive-container")).toBeInTheDocument();
  });
});
