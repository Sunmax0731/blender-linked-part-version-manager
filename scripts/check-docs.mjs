import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const requiredFiles = [
  "README.md",
  "AGENTS.md",
  "SKILL.md",
  "TODO.md",
  "docs/requirements.md",
  "docs/specification.md",
  "docs/design.md",
  "docs/architecture.md",
  "docs/implementation-plan.md",
  "docs/test-plan.md",
  "docs/manual-test.md",
  "docs/blender-real-path-validation.md",
  "docs/installation-guide.md",
  "docs/features.md",
  "docs/user-guide.md",
  "docs/strict-manual-test-addendum.md",
  "docs/release-checklist.md",
  "docs/competitive-benchmark.md",
  "docs/evaluation-criteria.md",
  "docs/qcds-evaluation.md",
  "docs/qcds-strict-metrics.json",
  "docs/source-idea-pack.json",
  "docs/release-evidence.json",
  "docs/releases/v0.1.0-alpha.1.md",
  "docs/releases/v0.1.0-alpha.2.md",
  "samples/representative-suite.json",
  "scripts/create-blend-fixtures.py",
  "Issues/README.md",
  "Issues/0004-alpha-mvp-release.md",
  "Issues/0005-blender.md",
  "Issues/0006-blender-runtime-link-reload-manual.md",
  "Issues/0007-alpha-manual-test-evidence.md",
  "Issues/0008-manual-test-fixtures.md",
  "Issues/0009-reload-target-path-fix.md",
  "Issues/0010-auto-reload-saved-links.md",
  "Issues/0011-blender-gui-part-registry.md",
  "Issues/0012-blender-gui-part-registry.md",
  "Issues/0013-mvp.md",
  "Issues/0014-mvp.md",
  "Issues/0015-user-facing-readme-features.md",
  "Issues/0016-blender-ui.md",
  "windows/blpvm-companion.mjs",
  "windows/blpvm-companion.cmd",
  "windows/install-alpha.cmd",
  "windows/README.md",
  "addon/blender_linked_part_version_manager/blender_manifest.toml"
];

const requiredBinaryFiles = [
  "integration/character_integration.blend",
  "parts/hair/main_hair.blend",
  "parts/body/base_body.blend",
  "parts/face/main_face.blend",
  "parts/accessories/glasses.blend",
];

const suspiciousCodePoints = new Set([0x7e67, 0x90e2, 0x9aeb, 0xfffd]);

function readText(relativePath) {
  const absolutePath = path.join(root, relativePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`Missing required file: ${relativePath}`);
  }
  return fs.readFileSync(absolutePath, "utf8");
}

function checkText(relativePath) {
  const text = readText(relativePath);
  for (const char of text) {
    const codePoint = char.codePointAt(0);
    if (suspiciousCodePoints.has(codePoint)) {
      throw new Error(`Suspicious mojibake code point U+${codePoint.toString(16).toUpperCase()} in ${relativePath}`);
    }
    if (codePoint < 0x20 && ![0x09, 0x0a, 0x0d].includes(codePoint)) {
      throw new Error(`Control character U+${codePoint.toString(16).toUpperCase()} in ${relativePath}`);
    }
  }
}

for (const file of requiredFiles) {
  checkText(file);
}

for (const file of requiredBinaryFiles) {
  const absolutePath = path.join(root, file);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`Missing required binary fixture: ${file}`);
  }
  if (fs.statSync(absolutePath).size <= 0) {
    throw new Error(`Empty binary fixture: ${file}`);
  }
}

const packageJson = JSON.parse(readText("package.json"));
if (packageJson.name !== "blender-linked-part-version-manager") {
  throw new Error("package.json name does not match repository name.");
}

const sourcePack = JSON.parse(readText("docs/source-idea-pack.json"));
if (sourcePack.idea_no !== 7 || sourcePack.repository !== packageJson.name) {
  throw new Error("source-idea-pack.json is not synchronized with idea No.7.");
}

const suite = JSON.parse(readText("samples/representative-suite.json"));
if (!Array.isArray(suite.parts) || suite.parts.length < 4) {
  throw new Error("representative suite must include at least four parts.");
}
if (!fs.existsSync(path.join(root, suite.integration_file || ""))) {
  throw new Error(`Representative integration file is missing: ${suite.integration_file}`);
}

const requiredPartFields = ["partId", "partTag", "blendPath", "linkedCollection", "owner", "source", "updatePolicy"];
for (const part of suite.parts) {
  for (const field of requiredPartFields) {
    if (!part[field]) {
      throw new Error(`Representative part is missing ${field}: ${JSON.stringify(part)}`);
    }
  }
  if (!fs.existsSync(path.join(root, part.blendPath))) {
    throw new Error(`Representative part blend is missing: ${part.blendPath}`);
  }
}

const metrics = JSON.parse(readText("docs/qcds-strict-metrics.json"));
const allowedGrades = new Set(["S+", "S-", "A+", "A-", "B+", "B-", "C+", "C-", "D+", "D-"]);
for (const key of ["Quality", "Cost", "Delivery", "Satisfaction"]) {
  if (!allowedGrades.has(metrics.grades?.[key])) {
    throw new Error(`Invalid QCDS grade for ${key}.`);
  }
}

const releaseEvidence = JSON.parse(readText("docs/release-evidence.json"));
if (releaseEvidence.version !== "0.1.0-alpha.2") {
  throw new Error("release-evidence.json version must match alpha release.");
}

console.log("Docs completeness check passed.");
