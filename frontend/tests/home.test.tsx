import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "../app/page";

describe("HomePage", () => {
  it("preserves the human-review control line", () => {
    render(<HomePage />);
    expect(screen.getByText(/Humans validate and decide/i)).toBeInTheDocument();
  });
});

