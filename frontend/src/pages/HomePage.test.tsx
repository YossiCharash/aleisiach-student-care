import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { renderWithClient } from "@/test/renderWithClient";
import { HomePage } from "@/pages/HomePage";

describe("HomePage", () => {
  it("redirects to the student list", () => {
    renderWithClient(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/students" element={<div>רשימת התלמידים</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText("רשימת התלמידים")).toBeInTheDocument();
  });
});
