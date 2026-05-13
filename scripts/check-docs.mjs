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
  "docs/release-checklist.md",
  "docs/competitive-benchmark.md",
  "docs/evaluation-criteria.md",
  "docs/qcds-evaluation.md",
  "docs/source-idea-pack.json",
  "samples/representative-suite.json",
  "Issues/README.md"
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

const requiredPartFields = ["partId", "partTag", "blendPath", "linkedCollection", "owner", "source", "updatePolicy"];
for (const part of suite.parts) {
  for (const field of requiredPartFields) {
    if (!part[field]) {
      throw new Error(`Representative part is missing ${field}: ${JSON.stringify(part)}`);
    }
  }
}

console.log("Docs completeness check passed.");
