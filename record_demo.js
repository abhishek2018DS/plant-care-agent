const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  console.log("Starting demo recording...");
  const outputDir = path.join(__dirname, "demo_output");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    recordVideo: {
      dir: outputDir,
      size: { width: 1280, height: 800 },
    },
  });

  const page = await context.newPage();
  const targetUrl = "https://plant-care-frontend-515384135402.us-east1.run.app";
  console.log(`Navigating to ${targetUrl}...`);
  await page.goto(targetUrl, { waitUntil: "networkidle" });

  // Wait 2 seconds to display header and initial state
  await page.waitForTimeout(2000);

  // 1. First interaction: Click Monstera care schedule prompt chip
  console.log("Clicking Monstera care prompt chip...");
  const firstChip = page.locator('.prompt-chip[data-prompt*="Monstera"]');
  if (await firstChip.count() > 0) {
    await firstChip.click();
  } else {
    await page.fill("#input", "What is the watering schedule for a Monstera Deliciosa?");
    await page.click('button.submit-btn');
  }

  // Wait for response bubble to appear
  console.log("Waiting for first response...");
  await page.waitForSelector('.msg-row.agent .bubble', { timeout: 30000 });
  await page.waitForTimeout(4000);

  // 2. Second interaction: Richer prompt asking for plant catalog and image generation
  console.log("Typing second richer prompt (catalog lookup & image generation)...");
  await page.fill("#input", "Show me the indoor plant catalog and generate an image of a lush Monstera Deliciosa");
  await page.waitForTimeout(500);
  await page.click('button.submit-btn');

  // Wait for second response (typing indicator disappears and second agent msg row appears)
  console.log("Waiting for second agent response...");
  await page.waitForFunction(() => {
    const agentMsgs = document.querySelectorAll('.msg-row.agent');
    return agentMsgs.length >= 2 && !document.querySelector('.typing-indicator');
  }, { timeout: 45000 });

  // Extra pause to show final rich output
  await page.waitForTimeout(6000);

  // Close page and context to finalize video writing
  await page.close();
  const videoPath = await page.video().path();
  await context.close();
  await browser.close();

  console.log("Video recorded at:", videoPath);

  // Copy to root as demo_video.webm
  const finalVideoPath = path.join(__dirname, "demo_video.webm");
  fs.copyFileSync(videoPath, finalVideoPath);
  console.log("Final demo video saved to:", finalVideoPath);
})();
