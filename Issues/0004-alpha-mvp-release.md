# Alpha MVP 実装と release evidence を完了する

- Status: done
- Priority: P1
- Phase: 04-implementation, 05-test, 06-release
- Linked TODO: [TODO.md](../TODO.md)
- GitHub Issue: https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/4

## 背景

Windows アプリ統合として扱う alpha では、Blender アドオンだけでなく、Windows 上で起動できる companion launcher、設定保存、installer dry-run、release artifact を同じ単位で揃える必要がある。

## Acceptance Criteria

- [x] Blender アドオン shell、registry validator、dry-run sync plan、Link reload preview が実装されている。
- [x] Windows companion launcher が起動し、registry validation と設定保存を実行できる。
- [x] `npm test` が docs、Python unit test、platform runtime gate、release artifact を検証する。
- [x] `docs/installation-guide.md`、`docs/user-guide.md`、`docs/qcds-evaluation.md`、`docs/qcds-strict-metrics.json`、release notes、docs ZIP が揃っている。
- [x] GitHub prerelease に添付する artifact 名と手動確認の残項目が記録されている。

## Resolution

`v0.1.0-alpha.1` の対象は Blender アドオン ZIP、docs ZIP、manual-test 文書、Windows companion launcher の動作確認である。Codex 環境では Blender CLI が見つからなかったため、Blender 実機 Link reload はリリース後の手動確認として残す。
