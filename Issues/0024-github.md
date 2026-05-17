# 正式リリース向けドキュメント再整備とGitHubリリース

- Status: done
- Priority: P2
- Type: feature
- Source: local
- Draft source: codex-cli
- Phase: 06-release
- Created: 2026-05-17
- QCDS: Quality, Delivery, Satisfaction

## Context

正式リリースに向けて、利用者向けドキュメントを再整備し、リリース版としてGitHubへ反映する。既存GUI入力の priority/type/phase は維持し、README、AGENTS、SKILL、docs、TODO、Issues の整合性と正式リリースに必要な公開状態を確認する。

## Acceptance Criteria

- [x] 正式リリース向けに必要なREADMEおよび関連ドキュメントの内容が更新されている
- [x] README、AGENTS、SKILL、docs、TODO、Issues の記載に矛盾がない
- [x] 正式リリース版のバージョン、変更点、既知事項が確認できる状態になっている
- [x] GitHub Releases に正式リリース版が作成され、必要な配布物または参照情報が紐づいている

## Notes

- 2026-05-17: 正式リリース tag は `v0.1.0`。実装バージョンは `0.1.2` を維持する。
- 2026-05-17: README、AGENTS、SKILL、installation guide、manual test、test plan、release checklist、QCDS、release evidence、release notes、TODO、Issues を `v0.1.0` 向けに同期した。
- 2026-05-17: GitHub Release URL は https://github.com/Sunmax0731/blender-linked-part-version-manager/releases/tag/v0.1.0 。配布物は add-on ZIP、docs ZIP、fixture ZIP、manual-test.md。
- Evidence: `docs/releases/v0.1.0.md`、`docs/release-evidence.json`、`docs/qcds-strict-metrics.json`、`dist/test-summary.json`、`dist/runtime-gate.json`。

## Codex Sessions

- 2026-05-17T05:17:58.642Z `codex-session-20260517051758-849zy1` - All Work Items (VS Code Codex handoff); access=danger-full-access; model=gpt-5.5; intelligence=xhigh; [prompt](c:/Users/gkkjh/AppData/Roaming/Code/User/workspaceStorage/915f2e6b3223925d61deb8335d66d110/sunmax0731.codex-friendly-project-starter/first-prompt-20260517T051758Z.md)
