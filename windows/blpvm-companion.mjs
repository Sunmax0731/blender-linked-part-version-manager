#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const version = "0.1.0";
const appName = "BlenderLinkedPartVersionManager";

function main(argv) {
  const command = argv[2] || "--help";
  if (command === "--version" || command === "version") {
    console.log(`blpvm-companion ${version}`);
    return;
  }
  if (command === "--help" || command === "help") {
    printHelp();
    return;
  }
  if (command === "validate-registry") {
    const registry = loadRegistry(readOption(argv, "--registry"));
    const issues = validateRegistry(registry);
    printJson({ ok: issues.length === 0, issues, parts: registry.parts?.length || 0 });
    process.exitCode = issues.length === 0 ? 0 : 1;
    return;
  }
  if (command === "status") {
    const registry = loadRegistry(readOption(argv, "--registry"));
    const plan = registry.parts.map((part) => ({
      partId: part.partId,
      partTag: part.partTag,
      status: part.expectedStatus || "unknown",
      blocked: ["local-dirty", "conflict-risk", "broken-link"].includes(part.expectedStatus),
    }));
    printJson({ product: registry.product, parts: plan.length, plan });
    return;
  }
  if (command === "init-settings") {
    const registryPath = path.resolve(readOption(argv, "--registry"));
    const dryRun = argv.includes("--dry-run");
    const settingsPath = resolveSettingsPath();
    const settings = {
      schemaVersion: 1,
      product: "blender-linked-part-version-manager",
      registryPath,
      addonPackage: "blender-linked-part-version-manager.zip",
      createdAt: new Date(0).toISOString(),
    };
    if (!dryRun) {
      fs.mkdirSync(path.dirname(settingsPath), { recursive: true });
      fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + "\n", "utf8");
    }
    printJson({ ok: true, dryRun, settingsPath, settings });
    return;
  }
  throw new Error(`Unknown command: ${command}`);
}

function loadRegistry(registryPath) {
  if (!registryPath) {
    throw new Error("Missing --registry <path>.");
  }
  return JSON.parse(fs.readFileSync(path.resolve(registryPath), "utf8"));
}

function validateRegistry(registry) {
  const issues = [];
  if (!Array.isArray(registry.parts) || registry.parts.length === 0) {
    issues.push({ code: "parts-required", message: "parts must be a non-empty array." });
    return issues;
  }
  const seen = new Set();
  for (const [index, part] of registry.parts.entries()) {
    for (const field of ["partId", "partTag", "blendPath", "linkedCollection", "owner", "source", "updatePolicy"]) {
      if (!part[field]) {
        issues.push({ code: "missing-field", index, field });
      }
    }
    if (seen.has(part.partId)) {
      issues.push({ code: "duplicate-part-id", index, partId: part.partId });
    }
    seen.add(part.partId);
  }
  return issues;
}

function readOption(argv, name) {
  const index = argv.indexOf(name);
  if (index === -1 || index + 1 >= argv.length) {
    return "";
  }
  return argv[index + 1];
}

function resolveSettingsPath() {
  const base = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
  return path.join(base, appName, "settings.json");
}

function printJson(value) {
  console.log(JSON.stringify(value, null, 2));
}

function printHelp() {
  console.log(`Usage:
  blpvm-companion --version
  blpvm-companion validate-registry --registry samples/representative-suite.json
  blpvm-companion status --registry samples/representative-suite.json
  blpvm-companion init-settings --registry samples/representative-suite.json [--dry-run]`);
}

try {
  main(process.argv);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
