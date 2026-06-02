import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

const apiUrl = process.env.PLAYWRIGHT_API_URL || process.env.VITE_API_URL || "http://127.0.0.1:8001";

async function openFreshLearner(page: Page, request: APIRequestContext) {
  const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const response = await request.post(`${apiUrl}/auth/register`, {
    data: {
      email: `e2e-${id}@pajamatalk.dev`,
      password: "pajama-dev-secret",
      display_name: "E2E Dreamer"
    }
  });
  expect(response.ok()).toBeTruthy();
  const body = await response.json();

  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.evaluate((token) => localStorage.setItem("pajama-token", token), body.access_token);
  await page.reload();
  await expect(page.getByTestId("nav-speak")).toBeVisible();
}

async function enterCoffeeRoom(page: Page) {
  await page.getByTestId("nav-speak").click();
  await page.getByTestId("room-coffee-alex").click();
  await page.getByTestId("mood-charged").click();
  await expect(page.getByTestId("speaking-mode-text")).toBeVisible();
}

test("speaking text mode streams a realtime answer", async ({ page, request }) => {
  await openFreshLearner(page, request);
  await enterCoffeeRoom(page);

  await page.getByTestId("speaking-composer").fill("Could I get an oat latte?");
  await page.getByTestId("speaking-send").click();

  await expect(page.getByText("Could I get an oat latte?")).toBeVisible();
  await expect(page.getByText(/Nice choice|oat milk|teacher mode|Quiero un caf/i)).toBeVisible();
});

test("speaking room restores backend history after local session is cleared", async ({ page, request }) => {
  await openFreshLearner(page, request);
  await enterCoffeeRoom(page);

  await page.getByTestId("speaking-composer").fill("Please remember this server history.");
  await page.getByTestId("speaking-send").click();
  await expect(page.getByText("Please remember this server history.")).toBeVisible();
  await expect(page.getByText(/Nice choice|teacher mode|server history/i)).toBeVisible();

  await page.evaluate(() => localStorage.removeItem("pajamatalk.speakingSession.v1"));
  await page.reload();
  await enterCoffeeRoom(page);

  await expect(page.getByText("Please remember this server history.")).toBeVisible();
});

test("call mode fallback uses the voice websocket and keeps the transcript", async ({ page, request }) => {
  await openFreshLearner(page, request);
  await enterCoffeeRoom(page);

  await page.getByTestId("speaking-mode-call").click();
  await page.getByTestId("call-fallback-input").fill("Could I get a latte?");
  await page.getByTestId("call-fallback-send").click();
  await expect(page.getByText("Could I get a latte?")).toBeVisible();

  await page.getByTestId("speaking-mode-text").click();
  await expect(page.getByText("Could I get a latte?").first()).toBeVisible();
  await expect(page.getByText(/Nice choice|oat milk|teacher mode|Quiero un caf/i)).toBeVisible();
});

test("context buddy can add analyzed words into storage", async ({ page, request }) => {
  await openFreshLearner(page, request);

  await page.getByTestId("context-input").fill("This deadline is awkward but the vibe is cozy.");
  await page.getByTestId("context-analyze").click();
  await expect(page.getByTestId("context-add-words")).toBeVisible();
  await page.getByTestId("context-add-words").click();

  await page.getByTestId("nav-storage").click();
  await expect(page.getByText(/deadline|awkward|cozy|vibe/i).first()).toBeVisible();
});

test("storage can enrich a new word and expose it for review", async ({ page, request }) => {
  await openFreshLearner(page, request);
  await page.getByTestId("nav-storage").click();

  await page.getByTestId("word-input").fill("exam");
  await page.getByTestId("word-add").click();
  await expect(page.getByTestId("word-result")).toContainText("exam");
  await page.getByTestId("storage-review-tab").click();
  await expect(page.getByTestId("review-remember")).toBeVisible();
});

test("profile choices refresh the learning path", async ({ page, request }) => {
  await openFreshLearner(page, request);
  await page.getByTestId("nav-vibe").click();

  await page.getByTestId("profile-learning-language-trigger").click();
  await page.getByTestId("profile-learning-language-option-pl").click();
  await page.getByTestId("profile-current-level-B1").click();
  await page.getByTestId("profile-target-level-C1").click();
  await page.getByTestId("profile-effort-Intense").click();

  await page.getByTestId("nav-aura").click();
  await expect(page.getByText(/B1 -> C1/)).toBeVisible();
});

test("grammar lab checks an exercise answer", async ({ page, request }) => {
  await openFreshLearner(page, request);

  await page.getByTestId("grammar-option").first().click();
  await page.getByTestId("grammar-check").click();
  await expect(page.getByTestId("grammar-feedback")).toBeVisible();
});
