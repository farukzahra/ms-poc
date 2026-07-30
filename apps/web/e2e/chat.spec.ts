import { test, expect } from "@playwright/test";

const mockDebugSteps = [
  {
    id: "mcp-0-get_customer",
    kind: "mcp",
    title: "Called MCP tool: get_customer",
    inputSummary: "customer_id=ACME-001",
    outputSummary: "ACME Corporation (Enterprise)",
    durationMs: 11.2,
    raw: {
      arguments: { customer_id: "ACME-001" },
      resultPreview: '{"name":"ACME Corporation","segment":"Enterprise"}',
    },
  },
  {
    id: "mcp-1-get_customer_sales",
    kind: "mcp",
    title: "Called MCP tool: get_customer_sales",
    inputSummary: "customer_id=ACME-001",
    outputSummary: '{"revenue_trend": -12}',
    durationMs: 9.5,
  },
  {
    id: "mcp-2-get_customer_tickets",
    kind: "mcp",
    title: "Called MCP tool: get_customer_tickets",
    inputSummary: "customer_id=ACME-001",
    outputSummary: "3 open ticket(s)",
    durationMs: 8.1,
  },
  {
    id: "llm-synthesis",
    kind: "llm",
    title: "Sent tool results to LLM for synthesis",
    inputSummary: "Model gpt-4o-mini · 900 prompt token(s) (MCP/RAG context + user message)",
    outputSummary: "320 completion token(s) · executive briefing answer",
    raw: {
      model: "gpt-4o-mini",
      promptTokens: 900,
      completionTokens: 320,
    },
  },
];

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
        answer:
          "# ACME Corporation — Executive Briefing\n\n## FACT\n- Open support tickets: 3\n- Customer: ACME Corporation (ACME-001)\n\n## RECOMMENDATION\n1. Schedule a QBR with ACME stakeholders to review the renewal timeline.\n2. Escalate open ticket T-501 to senior support with a 72-hour ETA.",
        sources: [{ title: "Renewal policy", source: "policies/renewal-policy.md" }],
        toolsUsed: ["get_customer", "get_customer_sales", "get_customer_tickets"],
        facts: [
          { label: "Open tickets", value: "3" },
          { label: "Customer", value: "ACME Corporation (ACME-001)" },
        ],
        recommendations: [
          { title: "Schedule QBR", detail: "Review renewal timeline with ACME stakeholders" },
        ],
        debug: {
          steps: mockDebugSteps,
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
  await expect(page.getByTestId("messages")).toContainText("ACME Corporation — Executive Briefing");
  await expect(page.getByTestId("messages")).toContainText("Facts");
  await expect(page.getByTestId("messages")).toContainText("AI Recommendations");
  await expect(page.getByTestId("messages")).toContainText("Schedule a QBR");

  await expect(page.locator(".briefing-sidebar").getByRole("heading", { name: "Briefing" })).toBeVisible();

  const debugToggle = page.getByTestId("debug-toggle");
  await expect(debugToggle).toBeVisible();
  await expect(debugToggle).toContainText("Debug");
  await expect(page.getByTestId("debug-panel")).not.toBeVisible();

  await debugToggle.click();
  const debugPanel = page.getByTestId("debug-panel");
  await expect(debugPanel).toBeVisible();
  await expect(debugPanel).toContainText("Step-by-step reasoning pipeline");
  await expect(debugPanel).toContainText("MCP/RAG steps");
  await expect(page.getByTestId("debug-step-1")).toContainText("Called MCP tool: get_customer");
  await expect(page.getByTestId("debug-step-1")).toContainText("ACME Corporation");
  await expect(page.getByTestId("debug-step-4")).toContainText("LLM");

  await expect(page.locator(".briefing-sidebar").getByRole("heading", { name: "Facts" })).toBeVisible();
  await expect(page.getByText("Open tickets")).toBeVisible();
});
