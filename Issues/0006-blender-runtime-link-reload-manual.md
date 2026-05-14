# Blender runtime gate で Link reload を手動確認する

- Status: done
- Priority: P3
- Type: manual-test
- Source: TODO.md
- Phase: 05-test
- Created: 2026-05-15
- QCDS: Quality, Satisfaction

## Context

Blender 実体パス `D:\SteamLibrary\steamapps\common\Blender\blender.exe` は検出でき、Blender 5.1.1 の CLI smoke とアドオン import は `dist/runtime-gate.json` に記録済みである。`integration/character_integration.blend` と部位別 `.blend` fixture を使い、ユーザー手元の Blender 5.1.1 で Link reload と Viewport 反映まで確認済み。

## Blocked Reason

完了。未保存の source `.blend` は Blender Link reload では反映できないため、保存後の reload を正式な確認境界とする。

## Acceptance Criteria

- [x] Blender 4.2 以降で add-on ZIP を install / enable できる。
- [x] `integration/character_integration.blend` から Hair、Body、Face、Accessories の部位別 `.blend` を Link できる fixture がある。
- [x] `Build Sync Preview` が更新候補、blocked 状態、broken-link 候補を表示する。
- [x] `Preview Reload` と `Reload Safe Links` が Hair part を reload 対象として処理できる。
- [x] Hair source `.blend` を変更して保存した後、`Reload Safe Links` で Viewport 上の Hair が更新されたことを確認できる。
- [x] 結果、Blender version、registry path、失敗時の再現手順を `docs/manual-test.md` と次リリース evidence に転記できる。

## Manual Evidence

- 2026-05-15: ユーザー手元の Blender 5.1.1 で add-on install / enable、`integration/character_integration.blend` の表示、`Validate Registry` の `issues: []`、`Build Sync Preview` の `totalParts: 4` / `currentParts: 1` / `updateCandidates: 1` / `blockedParts: 2` を確認。
- 2026-05-15: `Preview Reload` / `Reload Safe Links` が `failed: []` だが `reloaded: []` / 全件 `skipped` になった。原因は registry の project-root relative `parts/...` と Blender library の `//../parts/...` の照合不一致。`Issues/0009-reload-target-path-fix.md` で修正済み。
- 2026-05-15: 修正版 add-on ZIP 再インストール後、`Preview Reload` は `dryRun: true`、`targets` と `reloaded` に `parts/hair/main_hair.blend` を表示し、Body / Accessories / Face を `skipped` に表示した。
- 2026-05-15: `Reload Safe Links` は `dryRun: false`、`targets` と `reloaded` に `parts/hair/main_hair.blend` を表示し、Body / Accessories / Face を `skipped` に表示した。
- 2026-05-15: Hair source `.blend` を X=2.0022 付近へ移動して保存後、`Reload Safe Links` で integration Viewport 上の Hair が右側へ移動したことを確認。

## Next Action

完了。保存前の変更は reload に反映できないため、Auto Reload は `Issues/0010-auto-reload-saved-links.md` で保存済みファイル監視として追加する。
