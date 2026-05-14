# Manual test で検出した reload 対象 path 不一致を修正する

- Status: done
- Priority: P2
- Type: bug
- Source: manual-test
- Phase: 05-test
- Created: 2026-05-15
- QCDS: Quality, Satisfaction

## Context

ユーザー手動テストで `Validate Registry` と `Build Sync Preview` は通ったが、`Preview Reload` / `Reload Safe Links` が `reloaded: []`、全 library `skipped` になった。

## Cause

Registry の `blendPath` は project root relative の `parts/hair/main_hair.blend` だが、Blender の linked library は integration file から見た `//../parts/hair/main_hair.blend` として保持される。reload 対象の照合が current `.blend` relative だけだったため、実在 library と一致しなかった。

## Acceptance Criteria

- [x] Registry が `samples/` 配下にある場合でも `parts/...` を project root relative として解決できる。
- [x] `Preview Reload` 相当の dry-run で Hair part が `reloaded` に出る。
- [x] 既存 unit test に path 解決の回帰テストがある。
- [x] Manual test docs に、修正前症状と再インストール手順が残っている。

## Evidence

- `python -m unittest discover -s tests`
- Blender 5.1.1 background verification: `BLPVM_RELOAD_RESULT` で `reloaded` に `parts/hair/main_hair.blend`、`skipped` に他3 library が出た。
