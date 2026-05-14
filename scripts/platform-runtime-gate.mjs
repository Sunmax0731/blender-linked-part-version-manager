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
const defaultBlenderDirectory = "D:\\SteamLibrary\\steamapps\\common\\Blender";

const version = run(launcher, ["--version"], env);
const settings = run(launcher, ["init-settings", "--registry", registry], env);
const installerDryRun = run(installer, ["--dry-run"], env);
const settingsPath = path.join(tempAppData, "BlenderLinkedPartVersionManager", "settings.json");
const settingsSaved = fs.existsSync(settingsPath);
const blender = detectBlenderExecutable();
const blenderVersion = blender.executablePath ? runDirect(blender.executablePath, ["--version"]) : null;
const blenderSmoke = blender.executablePath ? runBlenderSmoke(blender.executablePath) : null;
const blenderSmokePassed = !blender.executablePath || blenderSmoke?.status === 0;

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
    status: blender.executablePath
      ? (blenderSmoke?.status === 0 ? "cli-smoke-passed" : "cli-smoke-failed")
      : "not-run-blender-cli-not-found",
    detectedBy: blender.detectedBy,
    defaultDirectory: defaultBlenderDirectory,
    executablePath: blender.executablePath,
    searchedPaths: blender.searchedPaths,
    versionLaunch: blenderVersion ? summarize(blenderVersion) : null,
    cliSmoke: blenderSmoke ? summarize(blenderSmoke) : null,
    manualTestRequired: true,
    manualTestReason: "CLI smoke verifies Blender startup and add-on import only; integration .blend link reload remains a manual host test.",
  },
};
result.passed = result.passed && blenderSmokePassed;

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

function runDirect(file, args) {
  return spawnSync(file, args, {
    cwd: root,
    text: true,
    encoding: "utf8",
    stdio: "pipe",
    windowsHide: true,
    timeout: 60_000,
  });
}

function runBlenderSmoke(file) {
  const addonPath = path.join(root, "addon").replace(/\\/g, "/");
  const expression = [
    "import sys, bpy",
    `sys.path.insert(0, ${JSON.stringify(addonPath)})`,
    "import blender_linked_part_version_manager as blpvm",
    "blpvm.register()",
    "print('BLPVM_BLENDER_SMOKE_OK', bpy.app.version_string, blpvm.bl_info['version'])",
    "print('BLPVM_REGISTER_SMOKE_OK')",
    "blpvm.unregister()",
  ].join("; ");
  return runDirect(file, ["--background", "--factory-startup", "--python-expr", expression]);
}

function detectBlenderExecutable() {
  const searchedPaths = [];
  const candidates = [
    { source: "BLENDER_EXE", file: process.env.BLENDER_EXE },
    { source: "default-steam-directory", file: path.join(defaultBlenderDirectory, "blender.exe") },
    ...whereBlenderCandidates().map((file) => ({ source: "PATH", file })),
  ];

  for (const candidate of candidates) {
    if (!candidate.file) {
      continue;
    }
    const normalized = path.resolve(candidate.file);
    searchedPaths.push({ source: candidate.source, file: normalized });
    if (fs.existsSync(normalized)) {
      return {
        detectedBy: candidate.source,
        executablePath: normalized,
        searchedPaths,
      };
    }
  }

  return {
    detectedBy: null,
    executablePath: null,
    searchedPaths,
  };
}

function whereBlenderCandidates() {
  const result = spawnSync("cmd.exe", ["/d", "/s", "/c", "where blender"], {
    text: true,
    encoding: "utf8",
    stdio: "pipe",
    windowsHide: true,
  });
  if (result.status !== 0) {
    return [];
  }
  return result.stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function summarize(result) {
  return {
    status: result.status,
    stdout: (result.stdout || "").trim().slice(0, 400),
    stderr: (result.stderr || "").trim().slice(0, 400),
  };
}
