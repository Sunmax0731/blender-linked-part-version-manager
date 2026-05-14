# 保存済み linked `.blend` の Auto Reload を追加する

- Status: done
- Priority: P2
- Type: feature
- Source: manual-test-follow-up
- Phase: 04-implementation
- Created: 2026-05-15
- QCDS: Quality, Satisfaction

## Context

手動テストで `Reload Safe Links` は保存後に Viewport へ反映できることを確認した。ユーザーは一定間隔で自動 reload する `Auto Reload` と、未保存状態のリアルタイム反映可否を確認したい。

## Decision

Blender Link reload は保存済み `.blend` を読み直す仕組みなので、別 Blender ウィンドウの未保存変更は反映できない。MVP では `Start Auto Reload` / `Stop Auto Reload` を追加し、保存済み linked `.blend` の更新時刻を一定間隔で監視して、安全な part だけ reload する。

## Acceptance Criteria

- [x] `Linked Parts` パネルに `Start Auto Reload` / `Stop Auto Reload` がある。
- [x] Add-on preferences で `Auto Reload Interval` を設定できる。
- [x] 保存済み linked `.blend` の mtime が変わったときだけ reload する。
- [x] `local-dirty`、`conflict-risk`、`broken-link` 相当の blocked part は Auto Reload 対象にしない。
- [x] 未保存変更は反映できないことを manual test docs に明記している。
- [x] 自動テストで Auto Reload 対象選定を検証している。

## Evidence

- `python -m unittest discover -s tests`
- `npm test`
