import { expect, type Page } from "@playwright/test";

export const DEMO_PASSWORD = "demo1234";

export async function login(page: Page, username: string): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("שם משתמש").fill(username);
  await page.getByLabel("סיסמה").fill(DEMO_PASSWORD);
  await page.getByRole("button", { name: "כניסה" }).click();
  await expect(page.getByRole("heading", { name: "התלמידים שלי" })).toBeVisible();
}
