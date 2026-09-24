import { useState, type ReactNode } from "react";
import { Download, Printer } from "lucide-react";
import { downloadAuthedPdf, printAuthedPdf } from "@/lib/api/pdf";
import { Button } from "@/components/ui/Button";

const DEFAULT_ERROR = "שגיאה בהפקת ה-PDF.";

type PdfAction = "download" | "print";

export function PdfButton({ url, label }: { url: string; label?: string }): ReactNode {
  const [pending, setPending] = useState<PdfAction | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(action: PdfAction): Promise<void> {
    setError(null);
    setPending(action);
    try {
      await (action === "download" ? downloadAuthedPdf(url) : printAuthedPdf(url));
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
        {label && <span className="text-sm font-medium text-ink-muted">{label}</span>}
        <Button
          variant="outline"
          size="sm"
          onClick={() => run("download")}
          disabled={busy}
        >
          <Download className="h-4 w-4" />
          {pending === "download" ? "מוריד…" : "הורדה"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => run("print")} disabled={busy}>
          <Printer className="h-4 w-4" />
          {pending === "print" ? "מכין להדפסה…" : "הדפסה"}
        </Button>
      </div>
      {error && <span className="text-xs text-rating-red">{error}</span>}
    </div>
  );
}
