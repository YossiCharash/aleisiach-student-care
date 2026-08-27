import { getToken } from "@/lib/auth/tokenStorage";

export async function openAuthedPdf(url: string): Promise<void> {
  const token = getToken();
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    throw new Error("שגיאה בהפקת ה-PDF.");
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const opened = window.open(objectUrl, "_blank", "noopener");
  if (opened === null) {
    URL.revokeObjectURL(objectUrl);
    throw new Error("הדפדפן חסם את פתיחת ה-PDF. אפשרו חלונות קופצים ונסו שוב.");
  }
  setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
}
