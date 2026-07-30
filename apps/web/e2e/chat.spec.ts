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
        facts: [
          { label: "Open tickets", value: "3" },
          { label: "Customer", value: "ACME Corporation (ACME-001)" },
        ],
        recommendations: [],
        debug: {
          pipeline: [
            "mcp:get_customer",
            "mcp:get_customer_sales",
            "mcp:get_customer_tickets",
            "llm:synthesis",
          ],
          mcpCalls: [
            {
              tool: "get_customer",
              source: "mcp",
              arguments: { customer_id: "ACME-001" },
              resultPreview: '{"name":"ACME Corporation","segment":"Enterprise"}',
              durationMs: 11.2,
            },
          ],
          ragCalls: [],
          llm: {
            model: "gpt-4o-mini",
            role: "synthesis",
            promptTokens: 900,
            completionTokens: 320,
            note: "FACT bullets grounded in MCP/RAG tool results; RECOMMENDATION section is LLM-generated guidance.",
          },
        },
      }),
    });
  });

  await page.goto("/");
  await page.getByTestId("chat-input").fill("Prepare me for my meeting with ACME");
  await page.getByTestId("chat-send").click();
  await expect(page.getByTestId("messages")).toContainText("ACME Executive Briefing");
  await expect(page.getByTestId("provenance")).toBeVisible();
  await expect(page.getByTestId("provenance").getByText("MCP", { exact: true })).toBeVisible();
  await expect(page.getByTestId("provenance").getByText("get_customer", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Facts" })).toBeVisible();
  await expect(page.getByText("Open tickets")).toBeVisible();
});
