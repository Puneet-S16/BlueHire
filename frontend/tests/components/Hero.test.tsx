import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Hero from "@/components/Hero";

describe("Hero", () => {
  it("renders the main heading", () => {
    render(<Hero />);
    const heading = screen.getByRole("heading", { name: /find skilled workers/i });
    expect(heading).toBeInTheDocument();
  });

  it("renders the description", () => {
    render(<Hero />);
    const description = screen.getByText(
      /the premium marketplace connecting professional contractors/i
    );
    expect(description).toBeInTheDocument();
  });

  it("renders two call-to-action buttons", () => {
    render(<Hero />);
    const hireTalent = screen.getByRole("link", { name: /hire talent/i });
    const findWork = screen.getByRole("link", { name: /find work/i });
    expect(hireTalent).toBeInTheDocument();
    expect(findWork).toBeInTheDocument();
  });
});
