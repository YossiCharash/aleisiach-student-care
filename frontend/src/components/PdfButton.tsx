import { useState, type ReactNode } from "react";
import { FileDown } from "lucide-react";
import { openAuthedPdf } from "@/lib/api/pdf";
import { Button } from "@/components/ui/Button";

const DEFAULT_ERROR = "שגיאה בהפקת ה-PDF.";

export function PdfButton({ url, label }: { url: string; label: string }): ReactNode {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick(): Promise<void> {
    setError(null);
    setLoading(true);
    try {
      await openAuthedPdf(url);
    } catch (caught) {
      setError(caught instanceof Error && caught.message ? caught.message : DEFAULT_ERROR);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <Button variant="outline" size="sm" onClick={handleClick} disabled={loading}>
        <FileDown className="h-4 w-4" />
        {loading ? "מפיק…" : label}
      </Button>
      {error && <span className="text-xs text-rating-red">{error}</span>}
    </div>
  );
}
