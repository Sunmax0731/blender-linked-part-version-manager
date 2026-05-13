# レジストリ、同期計画、衝突状態の仕様を確定する

- Status: open
- Priority: P1
- Phase: 02-specification
- Linked TODO: [TODO.md](../TODO.md)
- GitHub Issue: https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/2

## 背景

`.blend` はバイナリであり、意味的な自動マージは難しい。実装前に Part Registry と sync plan の contract を固め、危険状態を自動更新しない仕様にする。

## Acceptance Criteria

- [ ] Registry schema の必須項目と optional 項目が確定している。
- [ ] status classification がテストケースに落とせる。
- [ ] Git adapter と local adapter の返却 contract が一致している。
- [ ] `samples/representative-suite.json` が仕様と同期している。
