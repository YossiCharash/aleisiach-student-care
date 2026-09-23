import { getToken } from "@/lib/auth/tokenStorage";

const PDF_ERROR = "שגיאה בהפקת ה-PDF.";
const FALLBACK_FILENAME = "document.pdf";

async function fetchPdfBlob(url: string): Promise<Response> {
  const token = getToken();
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    throw new Error(PDF_ERROR);
  }
  return response;
}

export function parseContentDispositionFilename(header: string | null): string | null {
  if (!header) {
    return null;
  }
  const encoded = header.match(/filename\*=UTF-8''([^;]+)/i);
  if (encoded) {
    try {
      return decodeURIComponent(encoded[1]);
    } catch {
      return null;
    }
  }
  const plain = header.match(/filename="?([^";]+)"?/i);
  return plain ? plain[1] : null;
}

export async function openAuthedPdf(url: string): Promise<void> {
  const response = await fetchPdfBlob(url);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const opened = window.open(objectUrl, "_blank", "noopener");
  if (opened === null) {
    URL.revokeObjectURL(objectUrl);
    throw new Error("הדפדפן חסם את פתיחת ה-PDF. אפשרו חלונות קופצים ונסו שוב.");
  }
  setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
}

export async function downloadAuthedPdf(url: string): Promise<void> {
  const response = await fetchPdfBlob(url);
  const blob = await response.blob();
  const filename =
    parseContentDispositionFilename(response.headers.get("Content-Disposition")) ??
    FALLBACK_FILENAME;
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
}
