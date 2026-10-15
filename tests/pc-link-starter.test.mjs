import { test } from "node:test";
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";

test("Official 1.3.5 TV app retains the saved PC-link service on restart", () => {
  mkdirSync("build", { recursive: true });
  execFileSync(process.env.CXX || "c++", ["-std=c++17", "-O1", "-Wall", "-Wextra", "-Werror",
    "-ffunction-sections", "-fdata-sections", "-Iapp/src", "app/src/orbit/starter.cpp",
    "tests/pc_link_starter_driver.cpp", "-Wl,--gc-sections", "-o", "build/pc-link-starter-test"],
    { stdio: "pipe" });
  execFileSync("build/pc-link-starter-test", [], { stdio: "pipe", timeout: 10000 });
});
