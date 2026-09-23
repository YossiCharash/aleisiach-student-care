import { describe, expect, it } from "vitest";
import { parseContentDispositionFilename } from "@/lib/api/pdf";

describe("parseContentDispositionFilename", () => {
  it("decodes an RFC 5987 UTF-8 filename", () => {
    const encoded = encodeURIComponent("ישראל ישראלי - דוח תפקודי.pdf");
    const header = `inline; filename="document.pdf"; filename*=UTF-8''${encoded}`;

    expect(parseContentDispositionFilename(header)).toBe("ישראל ישראלי - דוח תפקודי.pdf");
  });

  it("falls back to a quoted ascii filename", () => {
    expect(parseContentDispositionFilename('inline; filename="document.pdf"')).toBe("document.pdf");
  });

  it("returns null when the header is missing", () => {
    expect(parseContentDispositionFilename(null)).toBeNull();
  });
});
