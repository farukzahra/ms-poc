import { test, expect } from "@playwright/test";

test("chat page loads and shows title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Enterprise AI Sales Intelligence/);
  await expect(page.getByRole("heading", { name: "Enterprise AI Sales Intelligence" })).toBeVisible();
});

test("user can send ACME briefing prompt", async ({ page }) => {
  await page.route("**/api/v1/chat", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        conversationId: "test",
        answer: "# ACME Executive Briefing\n\n## FACT\n- Open support tickets: 3",
        sources: [{ title: "Renewal policy", source: "policies/renewal-policy.md" }],
        toolsUsed: ["get_customer", "get_customer_sales", "get_customer_tickets"],
        recommendations: [],
      }),
    });
  });

  await page.goto("/");
  await page.getByTestId("chat-input").fill("Prepare me for my meeting with ACME");
  await page.getByTestId("chat-send").click();
  await expect(page.getByTestId("messages")).toContainText("ACME Executive Briefing");
  await expect(page.getByText("get_customer", { exact: true })).toBeVisible();
});
