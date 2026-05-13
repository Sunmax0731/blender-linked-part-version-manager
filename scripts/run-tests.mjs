import { spawnSync } from "node:child_process";

const steps = [
  ["node", ["scripts/check-docs.mjs"]],
  ["python", ["-m", "compileall", "-q", "addon", "tests"]],
  ["python", ["-m", "unittest", "discover", "-s", "tests"]],
  ["node", ["scripts/platform-runtime-gate.mjs"]],
  ["node", ["scripts/package-release.mjs"]],
  ["node", ["scripts/check-release-artifacts.mjs"]],
];

for (const [command, args] of steps) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: false,
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

console.log("Release validation passed.");
