# Blender UI と更新前プレビューの導線を固める

- Status: done
- Priority: P2
- Phase: 03-design
- Linked TODO: [TODO.md](../TODO.md)
- GitHub Issue: https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/3

## 背景

共同制作では誤った pull / reload が統合ファイルの確認状態を壊す。ユーザーが部位、リスク、次の操作を理解できる UI を先に設計する。

## Acceptance Criteria

- [x] Part Registry、Sync Preview、Link Health、Publish Part の表示項目が確定している。
- [x] `local-dirty` と `conflict-risk` の操作制限が設計されている。
- [x] broken link の復旧候補の表示方針が決まっている。
- [x] `docs/design.md` と `docs/manual-test.md` が更新されている。

## Resolution

Blender Sidebar の `Linked Parts` パネルで registry validation、sync preview、dry-run reload を提供する。alpha では Publish Part は preview contract までに留め、push 実行は docs 手順に残す。
