import { expect, test } from "@playwright/test";

test("demo learner can open speaking room and receive a realtime reply", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();

  const demoButton = page.getByRole("button", { name: "Демо-вхід" });
  await demoButton.click();

  await expect(page.getByRole("heading", { name: "Головна" })).toBeVisible();
  await page.getByRole("button", { name: "Спікінг" }).last().click();

  await expect(page.getByRole("button", { name: "Lo-fi Coffee Alex · barista with soft sarcasm" })).toBeVisible();
  await page.getByRole("button", { name: "Lo-fi Coffee Alex · barista with soft sarcasm" }).click();
  await page.getByRole("button", { name: /енергійно|more energy|⚡/ }).click();

  const composer = page.getByPlaceholder("Reply to Alex");
  await composer.fill("Could I get an oat latte?");
  await page.getByRole("button", { name: "Send" }).click();

  await expect(page.getByText("Could I get an oat latte?")).toBeVisible();
  await expect(page.getByText(/Nice choice|легкий режим|живіший темп|oat milk/i)).toBeVisible();
});

test("dictionary screen is reachable on desktop and mobile layouts", async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();

  const demoButton = page.getByRole("button", { name: "Демо-вхід" });
  await demoButton.click();

  await page.getByRole("button", { name: "Словник" }).click();
  await expect(page.getByRole("heading", { name: "Словник" })).toBeVisible();
});
