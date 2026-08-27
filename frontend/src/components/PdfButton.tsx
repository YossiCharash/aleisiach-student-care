import { useState, type ReactNode } from "react";
import { FileDown } from "lucide-react";
import { openAuthedPdf } from "@/lib/api/pdf";
import { Button } from "@/components/ui/Button";

export function PdfButton({ url, label }: { url: string; label: string }): ReactNode {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  async function handleClick(): Promise<void> {
    setError(false);
    setLoading(true);
    try {
      await openAuthedPdf(url);
    } catch {
      setError(true);
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
      {error && <span className="text-xs text-rating-red">שגיאה בהפקת ה-PDF.</span>}
    </div>
  );
}
