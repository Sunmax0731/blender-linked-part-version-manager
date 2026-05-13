import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const dist = path.join(root, "dist");
fs.mkdirSync(dist, { recursive: true });

const tempAppData = fs.mkdtempSync(path.join(os.tmpdir(), "blpvm-appdata-"));
const env = { ...process.env, APPDATA: tempAppData };
const launcher = path.join(root, "windows", "blpvm-companion.cmd");
const installer = path.join(root, "windows", "install-alpha.cmd");
const registry = path.join(root, "samples", "representative-suite.json");

const version = run(launcher, ["--version"], env);
const settings = run(launcher, ["init-settings", "--registry", registry], env);
const installerDryRun = run(installer, ["--dry-run"], env);
const settingsPath = path.join(tempAppData, "BlenderLinkedPartVersionManager", "settings.json");
const settingsSaved = fs.existsSync(settingsPath);
const blenderCommand = spawnSync("cmd.exe", ["/d", "/s", "/c", "where blender"], {
  text: true,
  encoding: "utf8",
  stdio: "pipe",
});
const blenderFound = blenderCommand.status === 0;

const result = {
  schemaVersion: 1,
  product: "blender-linked-part-version-manager",
  platform: "windows",
  gate: "local-executable-or-installer-launch",
  passed: version.status === 0 && settings.status === 0 && installerDryRun.status === 0 && settingsSaved,
  checks: {
    companionVersionLaunch: summarize(version),
    settingsSaveLaunch: summarize(settings),
    installerDryRunLaunch: summarize(installerDryRun),
    settingsSaved,
    settingsPath,
  },
  blenderHostGate: {
    status: blenderFound ? "available-not-run-by-npm" : "not-run-blender-cli-not-found",
    manualTestRequired: true,
  },
};

fs.writeFileSync(path.join(dist, "runtime-gate.json"), JSON.stringify(result, null, 2) + "\n", "utf8");
if (!result.passed) {
  console.error(JSON.stringify(result, null, 2));
  process.exit(1);
}
console.log("Platform runtime gate passed.");

function run(file, args, env) {
  return spawnSync("cmd.exe", ["/d", "/c", "call", file, ...args], {
    env,
    text: true,
    encoding: "utf8",
    stdio: "pipe",
    windowsHide: true,
  });
}

function summarize(result) {
  return {
    status: result.status,
    stdout: (result.stdout || "").trim().slice(0, 400),
    stderr: (result.stderr || "").trim().slice(0, 400),
  };
}
