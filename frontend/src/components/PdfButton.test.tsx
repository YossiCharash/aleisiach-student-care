import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PdfButton } from "@/components/PdfButton";
import { downloadAuthedPdf, printAuthedPdf } from "@/lib/api/pdf";

vi.mock("@/lib/api/pdf", () => ({
  downloadAuthedPdf: vi.fn(() => Promise.resolve()),
  printAuthedPdf: vi.fn(() => Promise.resolve()),
}));

const downloadMock = vi.mocked(downloadAuthedPdf);
const printMock = vi.mocked(printAuthedPdf);

describe("PdfButton", () => {
  beforeEach(() => {
    downloadMock.mockClear();
    printMock.mockClear();
  });

  it("downloads the pdf from the download button", async () => {
    render(<PdfButton url="/students/1/pdf" />);

    await userEvent.click(screen.getByRole("button", { name: "הורדה" }));

    expect(downloadMock).toHaveBeenCalledWith("/students/1/pdf");
    expect(printMock).not.toHaveBeenCalled();
  });

  it("prints the pdf from the print button", async () => {
    render(<PdfButton url="/students/1/pdf" />);

    await userEvent.click(screen.getByRole("button", { name: "הדפסה" }));

    expect(printMock).toHaveBeenCalledWith("/students/1/pdf");
    expect(downloadMock).not.toHaveBeenCalled();
  });
});
