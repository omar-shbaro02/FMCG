import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

import HomePage from "../app/page";

describe("HomePage", () => {
  it("states the product decision and human control line", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: /Forecast-Augmented Growth Quality Diagnostic/i })).toBeInTheDocument();
    expect(screen.getByText("Humans validate and decide.")).toBeInTheDocument();
  });
});
