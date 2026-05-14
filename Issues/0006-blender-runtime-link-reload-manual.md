# Blender runtime gate で Link reload を手動確認する

- Status: blocked
- Priority: P3
- Type: manual-test
- Source: TODO.md
- Phase: 05-test
- Created: 2026-05-15
- QCDS: Quality, Satisfaction

## Context

Blender 実体パス `D:\SteamLibrary\steamapps\common\Blender\blender.exe` は検出でき、Blender 5.1.1 の CLI smoke とアドオン import は `dist/runtime-gate.json` に記録済みである。`integration/character_integration.blend` と部位別 `.blend` fixture も用意済み。ただし Link reload、Viewport 反映、`local-dirty` / `conflict-risk` 時の体験確認はユーザーまたはテスト協力者の手動 host test として残る。

## Blocked Reason

この項目はユーザー手元の Blender UI で、fixture を開いて reload 結果を目視確認する必要がある。Codex は非破壊 CLI smoke と fixture 生成まで実施済みだが、Viewport の確認結果はユーザーまたはテスト協力者の実行証跡として扱う。

## Acceptance Criteria

- [x] Blender 4.2 以降で add-on ZIP を install / enable できる。
- [x] `integration/character_integration.blend` から Hair、Body、Face、Accessories の部位別 `.blend` を Link できる fixture がある。
- [x] `Build Sync Preview` が更新候補、blocked 状態、broken-link 候補を表示する。
- [ ] `Reload Safe Links` 後に対象部位だけが Viewport 上で更新されたことを確認できる。
- [ ] 結果、Blender version、registry path、失敗時の再現手順を `docs/manual-test.md` と次リリース evidence に転記できる。

## Manual Evidence

- 2026-05-15: ユーザー手元の Blender 5.1.1 で add-on install / enable、`integration/character_integration.blend` の表示、`Validate Registry` の `issues: []`、`Build Sync Preview` の `totalParts: 4` / `currentParts: 1` / `updateCandidates: 1` / `blockedParts: 2` を確認。
- 2026-05-15: `Preview Reload` / `Reload Safe Links` が `failed: []` だが `reloaded: []` / 全件 `skipped` になった。原因は registry の project-root relative `parts/...` と Blender library の `//../parts/...` の照合不一致。`Issues/0009-reload-target-path-fix.md` で修正済み。
- Next: 修正版 add-on ZIP を再インストールし、`Preview Reload` が Hair part を `reloaded` に出すことを再確認する。

## Next Action

ユーザーが `docs/manual-test.md` と `docs/strict-manual-test-addendum.md` に沿って Blender UI で確認し、結果を `Issues/0007-alpha-manual-test-evidence.md` に渡す。
