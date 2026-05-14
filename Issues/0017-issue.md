# リンクファイル統合機能を追加する

- Status: done
- Priority: P2
- Type: feature
- Source: local
- Draft source: codex-cli
- Phase: 05-test
- Created: 2026-05-14
- QCDS: Quality, Cost, Satisfaction

## Context

リンクされた部位ファイルを1つのBlenderファイルへ統合できる機能を追加する。統合は不可逆または破壊的になり得るため、実行前に対象と影響範囲を明示し、ユーザー確認を必須にする。

## Acceptance Criteria

- [x] 統合対象のリンクファイルを選択または確認できる操作がBlenderアドオン側に追加されている
- [x] 実行前に不可逆操作であること、対象ファイル、出力先を示す確認ダイアログが表示される
- [x] 確認ダイアログでキャンセルした場合、.blend本体、リンク状態、Part Registry が変更されない
- [x] 実行後に統合結果と発生した警告を確認できるレポートが表示または保存される
- [x] 確認あり実行とキャンセルの手順が手動テストで検証できる

## Notes

- Added `Preview Integrate` / `Integrate Link` to the Blender add-on panel.
- `Integrate Link` uses a confirmation dialog before calling the localize helper; cancel means `execute` is not called, so `.blend`, link state, and registry data remain unchanged.
- Reports are written to the configured `Report Path` with `operation=integrate-linked-library`.
- Automated evidence: `python -m unittest tests.test_registry_plan` passed with link integration dry-run and localize helper tests.
- Manual evidence remains pending for Blender UI confirmation cancel and copied-fixture execution; steps are documented in `docs/manual-test.md`.
