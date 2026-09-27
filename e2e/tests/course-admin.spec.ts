import { expect, test, type Page } from "@playwright/test";

const adminEmail = process.env.ADMIN_EMAIL || "phase2-admin@example.com";
const adminPassword = process.env.ADMIN_PASSWORD || "Phase2Admin!2026";
const courseSlug = process.env.TEST_COURSE_SLUG || "enterprise-network-automation-sdwan";

async function login(page: Page) {
  await page.goto("/login");
  await page.locator('input[type="email"]').fill(adminEmail);
  await page.locator('input[type="password"]').fill(adminPassword);
  await page.getByRole("button", { name: /login/i }).click();
  await expect(page).toHaveURL(/dashboard/);
}

test.describe("Course administration", () => {
  test("platform admin can open and inspect the course editor", async ({ page }) => {
    await login(page);

    await page.goto("/admin/courses");
    await expect(page.getByRole("heading", { name: "Manage courses" })).toBeVisible();
    await expect(page.getByText("Enterprise Network Automation with SD-WAN")).toBeVisible();

    const courseRow = page.locator(".list-item").filter({
      hasText: "Enterprise Network Automation with SD-WAN",
    });
    await expect(courseRow).toContainText("draft");

    await courseRow.getByRole("link", { name: "Edit" }).click();

    await expect(page).toHaveURL(/\/admin\/courses\/\d+$/);
    await expect(page.getByRole("heading", { name: "Course details" })).toBeVisible();
    await expect(page.getByLabel("Title")).toHaveValue("Enterprise Network Automation with SD-WAN");
    await expect(page.getByLabel("Slug")).toHaveValue(courseSlug);
    await expect(page.getByLabel("Estimated hours")).toHaveValue("40");
    await expect(page.getByText("Enterprise Networking Foundations")).toBeVisible();
    await expect(page.getByText("Network Automation")).toBeVisible();
  });

  test("course editor preserves draft metadata through the UI", async ({ page }) => {
    await login(page);

    await page.goto("/admin/courses");
    const courseRow = page.locator(".list-item").filter({
      hasText: "Enterprise Network Automation with SD-WAN",
    });
    await courseRow.getByRole("link", { name: "Edit" }).click();

    const description = page.getByLabel("Description");
    const original = await description.inputValue();

    await description.fill(original);
    await page.getByRole("button", { name: "Save course metadata" }).click();
    await expect(page.getByText("Course metadata saved.")).toBeVisible();

    await page.reload();
    await expect(page.getByLabel("Description")).toHaveValue(original);
    await expect(page.getByText("draft")).toBeVisible();
  });
});
