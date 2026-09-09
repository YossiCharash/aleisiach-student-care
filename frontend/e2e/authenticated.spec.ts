import { expect, test } from "@playwright/test";
import { login } from "./helpers/auth";

test.describe("manager (mor) authenticated flows", () => {
  test("lands on the students list grouped by class", async ({ page }) => {
    await login(page, "mor");

    await expect(page).toHaveURL(/\/students$/);
    await expect(page.getByRole("heading", { name: /^סדנה א׳/ })).toBeVisible();
    await expect(page.getByRole("heading", { name: /^סדנה ב׳/ })).toBeVisible();
    await expect(page.getByText("נועה כהן")).toBeVisible();
    await expect(page.getByText("איתי לוי")).toBeVisible();
    await expect(page.getByText("מאיה ברק")).toBeVisible();
  });

  test("opens a student and sees the five tabs", async ({ page }) => {
    await login(page, "mor");
    await page.goto("/students");
    await page.getByRole("link", { name: "נועה כהן" }).click();
    await expect(page).toHaveURL(/\/students\/.+/);
    await expect(page.getByRole("tab", { name: "פרטים אישיים" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "תוכנית קידום" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "ישיבות צוות" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "סיכום עו״ס" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "דוח תפקודי" })).toBeVisible();
  });

  test("reaches settings with users and taxonomy areas", async ({ page }) => {
    await login(page, "mor");
    await page.goto("/settings");
    await expect(page.getByRole("heading", { name: "הגדרות" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "משתמשים" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "כישורים-מיומנויות" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "אבחונים" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "עריכת פרטי תלמיד" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "סדנאות" })).toBeVisible();
  });

  test("reaches the archived-students view", async ({ page }) => {
    await login(page, "mor");
    await page.goto("/students/archived");
    await expect(page.getByRole("heading", { name: "תלמידים בארכיון" })).toBeVisible();
  });

  test("settings account tab shows the change-password form", async ({ page }) => {
    await login(page, "mor");
    await page.goto("/settings");
    await page.getByRole("tab", { name: "החשבון שלי" }).click();
    await expect(page.getByLabel("סיסמה נוכחית")).toBeVisible();
    await expect(page.getByLabel("סיסמה חדשה", { exact: true })).toBeVisible();
    await expect(page.getByLabel("אימות סיסמה חדשה")).toBeVisible();
  });

  test("logs out back to the login screen", async ({ page }) => {
    await login(page, "mor");
    await page.getByRole("button", { name: "יציאה" }).click();
    await expect(page).toHaveURL(/\/login$/);
  });
});

test.describe("role-based access in the UI", () => {
  test("instructor (dana) sees only her class and account-only settings", async ({
    page,
  }) => {
    await login(page, "dana");

    await page.goto("/students");
    await expect(page.getByText("נועה כהן")).toBeVisible();
    await expect(page.getByText("איתי לוי")).toBeVisible();
    await expect(page.getByText("מאיה ברק")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "תלמיד חדש" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "סדנה חדשה" })).toHaveCount(0);

    await page.getByRole("link", { name: "הגדרות", exact: true }).click();
    await expect(page.getByRole("tab", { name: "החשבון שלי" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "משתמשים" })).toHaveCount(0);
  });

  test("professional teacher (yoav) is read-only, no social-note tab", async ({
    page,
  }) => {
    await login(page, "yoav");
    await page.goto("/students");
    await expect(page.getByText("מאיה ברק")).toBeVisible();
    await expect(page.getByRole("button", { name: "תלמיד חדש" })).toHaveCount(0);

    await page.getByRole("link", { name: "נועה כהן" }).click();
    await expect(page.getByRole("tab", { name: "פרטים אישיים" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "סיכום עו״ס" })).toHaveCount(0);
  });
});
