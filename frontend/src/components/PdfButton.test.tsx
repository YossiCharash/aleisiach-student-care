import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PdfButton } from "@/components/PdfButton";
import { openAuthedPdf, downloadAuthedPdf } from "@/lib/api/pdf";

vi.mock("@/lib/api/pdf", () => ({
  openAuthedPdf: vi.fn(() => Promise.resolve()),
  downloadAuthedPdf: vi.fn(() => Promise.resolve()),
}));

const openMock = vi.mocked(openAuthedPdf);
const downloadMock = vi.mocked(downloadAuthedPdf);

describe("PdfButton", () => {
  beforeEach(() => {
    openMock.mockClear();
    downloadMock.mockClear();
  });

  it("opens the pdf in a new tab from the labelled button", async () => {
    render(<PdfButton url="/students/1/pdf" label="דוח תפקודי" />);

    await userEvent.click(screen.getByRole("button", { name: "דוח תפקודי" }));

    expect(openMock).toHaveBeenCalledWith("/students/1/pdf");
    expect(downloadMock).not.toHaveBeenCalled();
  });

  it("downloads the pdf from the download button", async () => {
    render(<PdfButton url="/students/1/pdf" label="דוח תפקודי" />);

    await userEvent.click(screen.getByRole("button", { name: "הורדת PDF" }));

    expect(downloadMock).toHaveBeenCalledWith("/students/1/pdf");
    expect(openMock).not.toHaveBeenCalled();
  });
});
