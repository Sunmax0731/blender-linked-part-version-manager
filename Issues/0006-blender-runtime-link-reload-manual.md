# Blender runtime gate で Link reload を手動確認する

- Status: blocked
- Priority: P3
- Type: manual-test
- Source: TODO.md
- Phase: 05-test
- Created: 2026-05-15
- QCDS: Quality, Satisfaction

## Context

Blender 実体パス `D:\SteamLibrary\steamapps\common\Blender\blender.exe` は検出でき、Blender 5.1.1 の CLI smoke とアドオン import は `dist/runtime-gate.json` に記録済みである。ただし統合 `.blend` と部位別 `.blend` の Link reload、Viewport 反映、`local-dirty` / `conflict-risk` 時の体験確認は手動 host test として残る。

## Blocked Reason

この項目はユーザー手元の Blender UI で、実際の integration `.blend` と part `.blend` を Link して reload 結果を目視確認する必要がある。Codex は非破壊 CLI smoke まで実施済みだが、ユーザーの制作ファイルを自動生成・保存して手動確認を代替しない。

## Acceptance Criteria

- [ ] Blender 4.2 以降で add-on ZIP を install / enable できる。
- [ ] `integration/character_integration.blend` から Hair、Body、Face、Accessories の部位別 `.blend` を Link できる。
- [ ] `Build Sync Preview` が更新候補、blocked 状態、broken-link 候補を表示する。
- [ ] `Reload Safe Links` 後に対象部位だけが Viewport 上で更新されたことを確認できる。
- [ ] 結果、Blender version、registry path、失敗時の再現手順を `docs/manual-test.md` と次リリース evidence に転記できる。

## Next Action

ユーザーが `docs/manual-test.md` と `docs/strict-manual-test-addendum.md` に沿って Blender UI で確認し、結果を `Issues/0007-alpha-manual-test-evidence.md` に渡す。
