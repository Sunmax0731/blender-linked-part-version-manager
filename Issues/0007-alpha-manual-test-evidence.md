# Alpha manual test 結果を次リリース evidence に反映する

- Status: blocked
- Priority: P3
- Type: release-evidence
- Source: TODO.md
- Phase: 06-release
- Created: 2026-05-15
- QCDS: Quality, Delivery, Satisfaction

## Context

`v0.1.0-alpha.1` は prerelease 済みで、Windows runtime gate と Blender CLI smoke は自動証跡として残っている。次リリースではユーザー手元の Blender manual test 結果を release evidence、QCDS、release checklist に反映する必要がある。

## Blocked Reason

`Issues/0006-blender-runtime-link-reload-manual.md` の manual Link reload 結果が未提供のため、次リリース evidence を `passed` に更新できない。

## Acceptance Criteria

- [ ] `Issues/0006-blender-runtime-link-reload-manual.md` の手動確認結果を受け取っている。
- [ ] `docs/release-evidence.json` に Blender version、実施日、対象 registry、結果を反映している。
- [ ] `docs/qcds-evaluation.md` と `docs/qcds-strict-metrics.json` の Blender host gate 表記を manual 結果に合わせて更新している。
- [ ] `docs/release-checklist.md` の Blender runtime gate 項目を結果に合わせて更新している。
- [ ] 失敗した場合は再現手順とログを新しい follow-up Issue に分離している。

## Next Action

ユーザーが Blender manual test 結果を共有した後、次リリース用の evidence 更新として再開する。
