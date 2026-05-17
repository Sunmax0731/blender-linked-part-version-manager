import fs from "node:fs";
import path from "node:path";

const required = [
  "dist/blender-linked-part-version-manager.zip",
  "dist/blender-linked-part-version-manager-docs.zip",
  "dist/blender-linked-part-version-manager-fixtures.zip",
  "dist/test-summary.json",
  "dist/runtime-gate.json",
  "docs/qcds-strict-metrics.json",
  "docs/release-evidence.json",
  "docs/releases/v0.1.0.md",
];

for (const file of required) {
  if (!fs.existsSync(path.join(process.cwd(), file))) {
    throw new Error(`Missing release artifact: ${file}`);
  }
}

const runtimeGate = JSON.parse(fs.readFileSync("dist/runtime-gate.json", "utf8"));
if (!runtimeGate.passed) {
  throw new Error("Runtime gate did not pass.");
}

const metrics = JSON.parse(fs.readFileSync("docs/qcds-strict-metrics.json", "utf8"));
const allowed = new Set(["S+", "S-", "A+", "A-", "B+", "B-", "C+", "C-", "D+", "D-"]);
for (const key of ["Quality", "Cost", "Delivery", "Satisfaction"]) {
  if (!allowed.has(metrics.grades?.[key])) {
    throw new Error(`Invalid QCDS grade for ${key}: ${metrics.grades?.[key]}`);
  }
}

console.log("Release artifacts check passed.");
