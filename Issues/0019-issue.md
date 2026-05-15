# 現行バージョンのリリース

- Status: done
- Priority: P2
- Type: release
- Source: local
- Draft source: codex-cli
- Phase: 06-release
- Created: 2026-05-15
- QCDS: Quality, Delivery, Satisfaction

## Context

現在のバージョンを利用者へ公開できる状態にする。README、AGENTS、SKILL、docs、TODO、Issues の整合を確認し、GitHub 反映と配布物の公開までをリリース作業として扱う。

## Acceptance Criteria

- [x] リリース対象の現在バージョン番号と変更内容が確認されている
- [x] 必要なドキュメントと TODO / Issues の状態がリリース内容と整合している
- [x] 配布物またはタグが作成され、GitHub 上で確認できる
- [x] リリース後に確認すべき手順と結果が記録されている

## Notes

- 2026-05-16: Release target is `v0.1.0-alpha.3`; Blender add-on / Windows companion implementation version is `0.1.2`.
- 2026-05-16: GitHub prerelease `v0.1.0-alpha.3` exists at https://github.com/Sunmax0731/blender-linked-part-version-manager/releases/tag/v0.1.0-alpha.3 and is marked prerelease.
- 2026-05-16: Required release assets are tracked as `dist/blender-linked-part-version-manager.zip`, `dist/blender-linked-part-version-manager-docs.zip`, `dist/blender-linked-part-version-manager-fixtures.zip`, and `manual-test.md`.
- 2026-05-16: Post-release verification is `npm test`, `docs/release-evidence.json`, `docs/qcds-strict-metrics.json`, `dist/runtime-gate.json`, and `dist/test-summary.json`.

## Codex Sessions

- 2026-05-15T23:09:40.172Z `codex-session-20260515230940-psd7el` - All Work Items (VS Code Codex handoff); access=danger-full-access; model=gpt-5.5; intelligence=high; [prompt](c:/Users/gkkjh/AppData/Roaming/Code/User/workspaceStorage/915f2e6b3223925d61deb8335d66d110/sunmax0731.codex-friendly-project-starter/first-prompt-20260515T230940Z.md)
