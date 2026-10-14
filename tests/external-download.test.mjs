import { test } from "node:test";
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";

mkdirSync("build", { recursive: true });
execFileSync("python3", ["tools/embed-launcher.py"], { stdio: "pipe" });
const cc = process.env.CC || "cc";
const flags = ["-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror", "-DORBIT_DESKTOP",
  "-Ibackend", "-I.deps/cjson", "-Ibuild/generated", "-fsanitize=undefined", "-fno-sanitize-recover=all"];
// The worker's platform simulator is useful for checking the legacy path, but
// links must be checked against the production allowlist, not localhost fixtures.
execFileSync(cc, [...flags, "-c", "backend/providers.c", "-o", "build/external-providers.o"], { stdio: "pipe" });
execFileSync(cc, [...flags, "-DORBIT_TEST", "backend/browser.c", ".deps/cjson/cJSON.c",
  "tests/external_download_driver.c", "build/external-providers.o", "-lpthread", "-lm", "-o", "build/external-download-test"], { stdio: "pipe" });

for (const scenario of ["rejects", "direct", "legacy", "busy", "cancel", "source-change",
  "catalog-change", "identity-mismatch", "refresh", "refresh-change"]) {
  test(`PC link handoff: ${scenario}`, () => {
    execFileSync("build/external-download-test", [scenario], { stdio: "pipe", timeout: 15000 });
  });
}
