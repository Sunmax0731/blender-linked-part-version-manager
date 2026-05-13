# AGENTS

この repo は `blender-linked-part-version-manager` の開発準備単位です。

## Scope

- Root: `D:\AI\BlenderAddon\blender-linked-part-version-manager`
- Domain: BlenderAddon
- Product kind: Blender add-on
- Source pack: `D:/AI/BlenderAddon/created_idea_007_blender-linked-part-version-manager/idea_007_blender-linked-part-version-manager.zip`
- Public repo: `https://github.com/Sunmax0731/blender-linked-part-version-manager`

## Working Rules

- README、AGENTS、SKILL、docs、TODO、Issues を同じ変更単位で更新する。
- Blender Link と外部同期を同じ責務に混ぜず、Link 管理、部位レジストリ、同期アダプタ、検証レポートを分ける。
- GitHub 操作はまず dry-run / status 確認を前面に出し、push / pull / reset 相当の危険操作は影響範囲を明示する。
- `.blend` 本体の自動生成や破壊的更新を実装する前に、サンプル registry と dry-run レポートで検証する。
- 作業ブランチは `codex/<task-summary>` 形式を1本だけ使い、工程完了後に main へ merge して push する。
- Markdown / JSON / JavaScript / Python は UTF-8 と LF を維持する。

## Current Phase

開発準備段階です。実装開始前に `docs/requirements.md`、`docs/specification.md`、`docs/design.md`、`docs/architecture.md`、`docs/implementation-plan.md`、`docs/test-plan.md`、`docs/manual-test.md` を読み、`TODO.md` と `Issues/` から1件ずつ進めます。
