import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Navbar from "@/components/Navbar";

describe("Navbar", () => {
  it("renders the BlueHire brand link", () => {
    render(<Navbar />);
    const brand = screen.getByRole("link", { name: /BlueHire/i });
    expect(brand).toBeInTheDocument();
    expect(brand).toHaveAttribute("href", "/");
  });

  it("renders a Login link", () => {
    render(<Navbar />);
    const login = screen.getByRole("link", { name: /login/i });
    expect(login).toBeInTheDocument();
    expect(login).toHaveAttribute("href", "/login");
  });

  it("renders a Sign Up link", () => {
    render(<Navbar />);
    const signup = screen.getByRole("link", { name: /sign up/i });
    expect(signup).toBeInTheDocument();
    expect(signup).toHaveAttribute("href", "/signup");
  });
});
