import { expect, test } from "@playwright/test";

test.describe("public auth navigation", () => {
  test("unauthenticated visit redirects to the login screen", async ({ page }) => {
    await page.goto("/settings/personal");
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "כניסה למערכת" })).toBeVisible();
  });

  test("login page renders the Hebrew RTL form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
    await expect(page.getByLabel("שם משתמש")).toBeVisible();
    await expect(page.getByLabel("סיסמה")).toBeVisible();
    await expect(page.getByRole("button", { name: "כניסה" })).toBeVisible();
  });

  test("forgot-password link leads to the reset-request screen", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: "שכחתי סיסמה" }).click();
    await expect(page).toHaveURL(/\/forgot-password$/);
    await expect(page.getByLabel("דוא״ל")).toBeVisible();
  });

  test("unknown route shows the not-found page", async ({ page }) => {
    await page.goto("/no-such-page");
    await expect(page).toHaveURL(/\/404$/);
    await expect(page.getByText("העמוד המבוקש לא נמצא.")).toBeVisible();
  });
});
