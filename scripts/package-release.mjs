import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const dist = path.join(root, "dist");
fs.mkdirSync(dist, { recursive: true });

writeTestSummary();
compressDirectory(
  "addon\\blender_linked_part_version_manager",
  "dist\\blender-linked-part-version-manager.zip",
);
compressPaths(
  [
    "README.md",
    "AGENTS.md",
    "SKILL.md",
    "TODO.md",
    "docs",
    "Issues",
    "samples",
    "integration",
    "parts",
    "windows",
  ],
  "dist\\blender-linked-part-version-manager-docs.zip",
);
compressPaths(
  [
    "samples\\representative-suite.json",
    "integration",
    "parts",
    "docs\\manual-test.md",
    "docs\\strict-manual-test-addendum.md",
  ],
  "dist\\blender-linked-part-version-manager-fixtures.zip",
);

console.log("Release artifacts packaged.");

function writeTestSummary() {
  const runtimeGatePath = path.join(dist, "runtime-gate.json");
  const runtimeGate = fs.existsSync(runtimeGatePath)
    ? JSON.parse(fs.readFileSync(runtimeGatePath, "utf8"))
    : null;
  const summary = {
    schemaVersion: 1,
    product: "blender-linked-part-version-manager",
    version: "0.1.0-alpha.2",
    automatedChecks: [
      "node scripts/check-docs.mjs",
      "python -m compileall -q addon tests",
      "python -m unittest discover -s tests",
      "node scripts/platform-runtime-gate.mjs",
      "node scripts/package-release.mjs",
      "node scripts/check-release-artifacts.mjs",
    ],
    runtimeGatePassed: Boolean(runtimeGate?.passed),
    blenderHostGateStatus: runtimeGate?.blenderHostGate?.status ?? "unknown",
    blenderHostExecutablePath: runtimeGate?.blenderHostGate?.executablePath ?? null,
    fixturePackage: "dist/blender-linked-part-version-manager-fixtures.zip",
    blenderManualTestPending: true,
  };
  fs.writeFileSync(path.join(dist, "test-summary.json"), JSON.stringify(summary, null, 2) + "\n", "utf8");
}

function compressDirectory(source, destination) {
  runPowerShell(`Compress-Archive -LiteralPath '${source}' -DestinationPath '${destination}' -Force`);
}

function compressPaths(paths, destination) {
  const literalPaths = paths.map((item) => `'${item}'`).join(", ");
  runPowerShell(`Compress-Archive -LiteralPath ${literalPaths} -DestinationPath '${destination}' -Force`);
}

function runPowerShell(command) {
  const result = spawnSync("powershell", ["-NoProfile", "-Command", command], {
    cwd: root,
    text: true,
    encoding: "utf8",
    stdio: "pipe",
  });
  if (result.status !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    process.exit(result.status ?? 1);
  }
}
