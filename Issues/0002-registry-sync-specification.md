# レジストリ、同期計画、衝突状態の仕様を確定する

- Status: done
- Priority: P1
- Phase: 02-specification
- Linked TODO: [TODO.md](../TODO.md)
- GitHub Issue: https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/2

## 背景

`.blend` はバイナリであり、意味的な自動マージは難しい。実装前に Part Registry と sync plan の contract を固め、危険状態を自動更新しない仕様にする。

## Acceptance Criteria

- [x] Registry schema の必須項目と optional 項目が確定している。
- [x] status classification がテストケースに落とせる。
- [x] Git adapter と local adapter の返却 contract が一致している。
- [x] `samples/representative-suite.json` が仕様と同期している。

## Resolution

`core.registry`、`core.plan`、`adapters.git`、`adapters.local` を追加し、`samples/representative-suite.json` の `expectedStatus` を自動テストの代表シナリオにした。危険状態は `blocked` risk として自動更新を止める。
