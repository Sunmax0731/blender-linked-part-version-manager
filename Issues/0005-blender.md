# Blender実体パスを使った検証対応

- Status: done
- Priority: P2
- Type: feature
- Source: local
- Draft source: codex-cli
- Phase: 05-test
- Created: 2026-05-14
- QCDS: Quality, Delivery

## Context

Blender の実体が `D:\SteamLibrary\steamapps\common\Blender` にあるため、このパスを前提に実施可能な自動検証や手動確認準備を進める。Blender Link reload など実環境依存の確認は、実行可能範囲と未確認範囲を分けて扱う。

## Acceptance Criteria

- [x] 指定された Blender ディレクトリから実行可能な Blender 本体または CLI を検出できる。
- [x] Blender 実体パスを使って実施可能なテスト項目が整理され、実行対象と手動確認対象が区別されている。
- [x] 実行した検証結果と、環境制約で残る確認事項が記録されている。

## Notes

- 2026-05-15: `D:\SteamLibrary\steamapps\common\Blender\blender.exe` を検出した。
- 2026-05-15: `node scripts/platform-runtime-gate.mjs` で Blender 5.1.1 の `--version` と `--background --factory-startup --python-expr` smoke を実行し、`BLPVM_BLENDER_SMOKE_OK 5.1.1 (0, 1, 0)` を確認した。
- Evidence: `dist/runtime-gate.json` の `blenderHostGate.status` は `cli-smoke-passed`。
- Link reload の Viewport 反映確認は自動 smoke では代替しないため、`Issues/0006-blender-runtime-link-reload-manual.md` と `Issues/0007-alpha-manual-test-evidence.md` に分離した。

## Codex Sessions

- 2026-05-14T17:23:44.483Z `codex-session-20260514172344-tpz3mt` - All Work Items (VS Code Codex handoff); access=danger-full-access; model=gpt-5.5; intelligence=high; [prompt](c:/Users/gkkjh/AppData/Roaming/Code/User/workspaceStorage/915f2e6b3223925d61deb8335d66d110/sunmax0731.codex-friendly-project-starter/first-prompt-20260514T172344Z.md)
