// @ts-check
import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
  test("homepage loads with title", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/SocialGuard AI/);
  });

  test("homepage shows hero section", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("text=SocialGuard AI")).toBeVisible();
  });

  test("login page is accessible", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("text=Sign In")).toBeVisible();
  });

  test("signup page is accessible", async ({ page }) => {
    await page.goto("/signup");
    await expect(page.locator("text=Create Account")).toBeVisible();
  });

  test("navbar contains platform links", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("nav")).toBeVisible();
  });

  test("compare page loads", async ({ page }) => {
    await page.goto("/compare");
    await expect(page.locator("text=Profile Comparison")).toBeVisible();
  });

  test("api keys page loads", async ({ page }) => {
    await page.goto("/api-keys");
    await expect(page.locator("text=API Keys")).toBeVisible();
  });
});

test.describe("Theme Toggle", () => {
  test("can switch between dark and light mode", async ({ page }) => {
    await page.goto("/");
    const themeBtn = page.locator(".theme-toggle-btn");
    await expect(themeBtn).toBeVisible();

    // Click to toggle theme
    await themeBtn.click();
    const dataTheme = await page.locator("html").getAttribute("data-theme");
    expect(["light", "dark"]).toContain(dataTheme);
  });
});

test.describe("Health Check", () => {
  test("backend API is healthy", async ({ request }) => {
    const response = await request.get("http://localhost:8000/api/health");
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.status).toBe("healthy");
  });

  test("backend returns model status", async ({ request }) => {
    const response = await request.get("http://localhost:8000/api/health");
    const body = await response.json();
    expect(body.models).toBeDefined();
    expect(Object.keys(body.models).length).toBeGreaterThanOrEqual(4);
  });
});
