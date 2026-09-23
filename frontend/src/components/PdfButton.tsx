import { useState, type ReactNode } from "react";
import { FileDown, Download } from "lucide-react";
import { openAuthedPdf, downloadAuthedPdf } from "@/lib/api/pdf";
import { Button } from "@/components/ui/Button";

const DEFAULT_ERROR = "שגיאה בהפקת ה-PDF.";

type PdfAction = "open" | "download";

export function PdfButton({ url, label }: { url: string; label: string }): ReactNode {
  const [pending, setPending] = useState<PdfAction | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(action: PdfAction): Promise<void> {
    setError(null);
    setPending(action);
    try {
      await (action === "open" ? openAuthedPdf(url) : downloadAuthedPdf(url));
    } catch (caught) {
      setError(
        caught instanceof Error && caught.message ? caught.message : DEFAULT_ERROR
      );
    } finally {
      setPending(null);
    }
  }

  const busy = pending !== null;

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <div className="inline-flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => run("open")} disabled={busy}>
          <FileDown className="h-4 w-4" />
          {pending === "open" ? "מפיק…" : label}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => run("download")}
          disabled={busy}
          aria-label="הורדת PDF"
          title="הורדת PDF"
        >
          <Download className="h-4 w-4" />
          {pending === "download" ? "מוריד…" : "הורדה"}
        </Button>
      </div>
      {error && <span className="text-xs text-rating-red">{error}</span>}
    </div>
  );
}
