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

export async function printAuthedPdf(url: string): Promise<void> {
  const response = await fetchPdfBlob(url);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.right = "0";
  iframe.style.bottom = "0";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "0";
  iframe.src = objectUrl;

  const cleanup = (): void => {
    iframe.remove();
    URL.revokeObjectURL(objectUrl);
  };

  iframe.onload = () => {
    const printWindow = iframe.contentWindow;
    printWindow?.addEventListener("afterprint", cleanup, { once: true });
    printWindow?.focus();
    printWindow?.print();
  };
  document.body.appendChild(iframe);
  setTimeout(cleanup, 60_000);
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
