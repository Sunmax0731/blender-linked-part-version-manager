# Alpha manual test 結果を次リリース evidence に反映する

- Status: done
- Priority: P3
- Type: release-evidence
- Source: TODO.md
- Phase: 06-release
- Created: 2026-05-15
- QCDS: Quality, Delivery, Satisfaction

## Context

`v0.1.0-alpha.1` は prerelease 済みで、Windows runtime gate と Blender CLI smoke は自動証跡として残っている。ユーザー手元の Blender manual test 結果を release evidence、QCDS、release checklist に反映する。

## Blocked Reason

完了。Blender 5.1.1 で add-on install、fixture 表示、registry validation、sync preview、manual reload、保存後 Viewport 反映を確認済み。

## Acceptance Criteria

- [x] `Issues/0006-blender-runtime-link-reload-manual.md` の手動確認結果を受け取っている。
- [x] `docs/release-evidence.json` に Blender version、実施日、対象 registry、結果を反映している。
- [x] `docs/qcds-evaluation.md` と `docs/qcds-strict-metrics.json` の Blender host gate 表記を manual 結果に合わせて更新している。
- [x] `docs/release-checklist.md` の Blender runtime gate 項目を結果に合わせて更新している。
- [x] 失敗した path 照合不一致は `Issues/0009-reload-target-path-fix.md` に分離して解決済み。

## Next Action

完了。
