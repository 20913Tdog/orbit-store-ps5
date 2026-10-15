// Run after installing Playwright and its Chromium browser. This starts an
// isolated local Vite server; all console/provider requests use fixtures.
import assert from "node:assert/strict";
import { mkdirSync } from "node:fs";
import { createServer } from "vite";

const { chromium } = await import(process.env.ORBIT_PLAYWRIGHT_MODULE || "playwright");
const server = await createServer({ server: { host: "127.0.0.1", port: 0, strictPort: false } });
await server.listen();
const origin = `http://127.0.0.1:${server.httpServer.address().port}`;
const browser = await chromium.launch({ headless: true,
  ...(process.env.ORBIT_CHROMIUM ? { executablePath: process.env.ORBIT_CHROMIUM } : {}),
  args: ["--no-sandbox"] });
const directUrl = "https://vikingfile.com/d/Abcd123456/PPSA00001-fixture.ffpfsc";
const providerPage = "https://vikingfile.com/f/Abcd123456";
const release = { id: "pc-fixture", gameId: "pc-fixture", platform: "ps5", titleId: "PPSA00001",
  title: "PC link test", sizeBytes: 4096, provider: "Vikingfile", sourceId: "vikingfile",
  format: "FFPFSC", filename: "PPSA00001-fixture.ffpfsc", browserAvailable: true,
  directAvailable: false, consoleVerified: false, artworkLayout: "ambient", cover: "", hero: "",
  genre: null, tagline: null, description: null, version: null, publisher: null, releaseDate: null };

async function setup(layout = "store", mode = "ok") {
  const context = await browser.newContext({ viewport: { width: 2048, height: 885 }, locale: "de-DE",
    ...(mode === "ps5-ua" ? { userAgent: "Mozilla/5.0 (PlayStation 5)" } : {}) });
  context.setDefaultTimeout(15000);
  const commands = [], errors = [];
  let status = { available: true, active: false, state: "idle", id: "", message: "", title: "", jobId: "" };
  await context.addInitScript(({ layout }) => {
    localStorage.setItem("orbit.interface.v1", JSON.stringify({ name: layout, motion: "reduced" }));
    localStorage.setItem("orbit.language.v1", "de");
    localStorage.setItem("orbit.pairing.v1", "fixture-pairing-token");
  }, { layout });
  await context.route("https://vikingfile.com/**", route => route.fulfill({ contentType: "text/html", body: "Provider fixture" }));
  await context.route("**/api/v1/**", async route => {
    const request = route.request(), url = new URL(request.url());
    const path = url.pathname.slice("/api/v1".length);
    let data;
    let code = 200;
    if (path === "/system") data = { name: "Orbit Store", version: "1.3.1-beta.2", platform: "ps5",
      paired: true, catalogueRevision: 1, stateHealthy: true, preferredStorage: "internal",
      localSessionAvailable: mode === "ps5-session", launcherStatus: "ready", httpPort: 34177 };
    else if (path === "/session") data = { token: "fixture-pairing-token", pairCode: "123456" };
    else if (path === "/sources") data = { enabled: ["vikingfile"], acknowledged: true, noticeVersion: 1,
      options: [{ id: "vikingfile", label: "Vikingfile", releaseCount: 1, downloadReady: true }] };
    else if (path === "/catalog") data = [release];
    else if (path === "/storage") data = [{ id: "internal", label: "PS5", path: "/data/fixture",
      freeBytes: 1e12, totalBytes: 2e12, pendingBytes: 0, projectedFreeBytes: 1e12, external: false }];
    else if (["/downloads", "/favorites"].includes(path)) data = [];
    else if (path === "/browser/page") {
      assert.equal(url.searchParams.get("releaseId"), release.id);
      assert.equal(request.headers().authorization, "Bearer fixture-pairing-token");
      if (mode === "page-error") { code = 400; data = { error: "This option has no supported provider browser page." }; }
      else data = { url: mode === "unsafe-page" ? "http://127.0.0.1/private" : providerPage };
    } else if (path === "/browser") {
      if (request.method() === "POST") {
        commands.push(request.postDataJSON());
        if (mode === "rejected-link") { code = 400; data = { error: "Captured link does not match this download option." }; }
        else { code = 202; data = status = { ...status, active: true, state: "validating", id: "fixture-session", title: release.title }; }
      } else data = status;
    } else if (path === "/library") data = { available: false, games: [], revision: 0, busy: false, roots: [], warnings: [] };
    else if (path === "/debrid") data = { provider: "torbox", available: false, connected: false, busy: false, hosts: [] };
    else data = { available: false, busy: false };
    await route.fulfill({ status: code, contentType: "application/json", body: JSON.stringify(data) });
  });
  const page = await context.newPage();
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(`${origin}/#download?game=pc-fixture&release=pc-fixture&storage=internal`);
  const box = page.locator(".external-download:visible");
  if (!mode.startsWith("ps5-")) await box.locator("input").waitFor({ state: "visible" });
  else await page.locator(".provider-browser-option:visible").waitFor();
  return { context, page, box, commands, errors };
}

try {
  for (const layout of ["store", "crossbar", "cinema", "panorama"]) {
    const { context, page, box, commands, errors } = await setup(layout);
    assert.equal(await box.locator("input").isEnabled(), true);
    assert.match(await box.textContent(), /PPSA00001-fixture\.ffpfsc/);
    const popupEvent = page.waitForEvent("popup");
    await page.locator(".source-file-button:visible").click();
    const popup = await popupEvent;
    await popup.waitForURL(providerPage);
    assert.equal(await popup.evaluate(() => window.opener === null), true);
    await popup.close();
    await box.locator("input").fill(`  ${directUrl}  `);
    mkdirSync("build/ui", { recursive: true });
    await page.screenshot({ path: `build/ui/pc-link-${layout}.png` });
    if (layout === "store") {
      assert.ok(await box.locator("h3").evaluate(el => parseFloat(getComputedStyle(el).fontSize)) >= 20);
      assert.equal(await box.locator("details").count(), 0);
      const action = await page.locator(".source-file-button:visible").boundingBox();
      assert.ok(action && action.y >= 0 && action.y + action.height <= 885);
    }
    await page.getByRole("button", { name: "Auf PS5 herunterladen", exact: true }).last().click();
    await page.waitForFunction(() => !!document.querySelector(".provider-browser-notice"));
    assert.equal(commands.length, 1);
    assert.deepEqual(commands[0], { action: "start", returnToOrbit: true,
      releaseId: "pc-fixture", storageId: "internal", directUrl });
    assert.equal(new URL(page.url()).hash, "");
    assert.deepEqual(errors, []);
    console.log(`PASS ${layout}: provider tab and PS5 link handoff`);
    await context.close();
  }
  for (const layout of ["store", "crossbar", "cinema", "panorama"]) {
    const { context, page, box, commands, errors } = await setup(layout);
    await box.locator("input").fill("   ");
    await page.getByRole("button", { name: "Auf PS5 herunterladen", exact: true }).last().click();
    await page.waitForFunction(() => !!document.querySelector(".provider-browser-notice"));
    assert.deepEqual(commands, [{ action: "start", returnToOrbit: true,
      releaseId: "pc-fixture", storageId: "internal" }]);
    assert.deepEqual(errors, []);
    console.log(`PASS ${layout}: empty link retains PS5 browser flow`);
    await context.close();
  }
  for (const mode of ["ps5-session", "ps5-ua"]) {
    const { context, page, commands, errors } = await setup("store", mode);
    assert.equal(await page.locator(".external-download").count(), 0);
    assert.equal(await page.locator(".source-file-button").count(), 0);
    await page.getByRole("button", { name: "Download-Seite auf PS5 öffnen", exact: true }).last().click();
    await page.waitForFunction(() => !!document.querySelector(".provider-browser-notice"));
    assert.equal(commands.length, 1);
    assert.equal(commands[0].directUrl, undefined);
    assert.deepEqual(errors, []);
    console.log(`PASS ${mode}: console UI unchanged`);
    await context.close();
  }
  for (const mode of ["blocked-popup", "page-error", "unsafe-page", "rejected-link"]) {
    const { context, page, box, commands, errors } = await setup("store", mode);
    if (mode === "rejected-link") {
      await box.locator("input").fill(directUrl);
      await page.getByRole("button", { name: "Auf PS5 herunterladen", exact: true }).last().click();
      await page.getByRole("alert").filter({ hasText: /Link|Download/ }).first().waitFor();
      assert.equal(commands.length, 1);
      assert.equal(await box.locator("input").inputValue(), directUrl);
    } else {
      if (mode === "blocked-popup") await page.evaluate(() => { window.open = () => null; });
      await page.locator(".source-file-button:visible").click();
      await page.locator(".source-file-actions:visible").getByRole("alert").waitFor();
      await page.waitForFunction(() => !document.querySelector(".source-file-button").disabled);
      assert.equal(commands.length, 0);
      assert.equal(context.pages().length, 1);
    }
    assert.deepEqual(errors, []);
    console.log(`PASS ${mode}: recoverable error`);
    await context.close();
  }
} finally {
  await browser.close();
  await server.close();
}
