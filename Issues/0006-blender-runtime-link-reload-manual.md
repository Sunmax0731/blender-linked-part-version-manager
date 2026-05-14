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

- [ ] Blender 4.2 以降で add-on ZIP を install / enable できる。
- [x] `integration/character_integration.blend` から Hair、Body、Face、Accessories の部位別 `.blend` を Link できる fixture がある。
- [ ] `Build Sync Preview` が更新候補、blocked 状態、broken-link 候補を表示する。
- [ ] `Reload Safe Links` 後に対象部位だけが Viewport 上で更新されたことを確認できる。
- [ ] 結果、Blender version、registry path、失敗時の再現手順を `docs/manual-test.md` と次リリース evidence に転記できる。

## Next Action

ユーザーが `docs/manual-test.md` と `docs/strict-manual-test-addendum.md` に沿って Blender UI で確認し、結果を `Issues/0007-alpha-manual-test-evidence.md` に渡す。
