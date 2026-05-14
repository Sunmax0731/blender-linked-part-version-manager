# AGENTS

この repo は `blender-linked-part-version-manager` の開発準備単位です。

## Scope

- Root: `D:\AI\BlenderAddon\blender-linked-part-version-manager`
- Domain: BlenderAddon
- Product kind: Blender add-on + Windows companion launcher
- Source pack: `D:/AI/BlenderAddon/created_idea_007_blender-linked-part-version-manager/idea_007_blender-linked-part-version-manager.zip`
- Public repo: `https://github.com/Sunmax0731/blender-linked-part-version-manager`

## Working Rules

- README、AGENTS、SKILL、docs、TODO、Issues を同じ変更単位で更新する。
- GitHub repository top の `README.md` は利用者向けに保ち、詳細な機能説明は `docs/features.md` へ分離してリンクする。
- Blender Link と外部同期を同じ責務に混ぜず、Link 管理、部位レジストリ、同期アダプタ、検証レポートを分ける。
- Windows companion は起動、設定保存、registry preview に限定し、`.blend` 本体の更新は Blender アドオン側の確認操作に残す。
- Blender GUI で生成した Part Registry は `owner=unassigned`、`source.type=local`、`versionRef=local`、`updatePolicy=manual` を安全な初期値とし、Link 操作は明示ボタンで実行して自動保存しない。
- GitHub 操作はまず dry-run / status 確認を前面に出し、push / pull / reset 相当の危険操作は影響範囲を明示する。
- `.blend` 本体の自動生成や破壊的更新を実装する前に、サンプル registry と dry-run レポートで検証する。
- Blender UI 文言を追加または変更する場合は、英語の既定表示と `ja_JP` 翻訳テーブルを同じ変更で更新する。
- 作業ブランチは `codex/<task-summary>` 形式を1本だけ使い、工程完了後に main へ merge して push する。
- Markdown / JSON / JavaScript / Python は UTF-8 と LF を維持する。

## Current Phase

`v0.1.0-alpha.2` のリリース段階です。作業開始時に `README.md`、`AGENTS.md`、`SKILL.md` を読み、続けて `docs/requirements.md`、`docs/specification.md`、`docs/design.md`、`docs/architecture.md`、`docs/implementation-plan.md`、`docs/test-plan.md`、`docs/manual-test.md`、`TODO.md`、`Issues/` を確認します。Blender CLI が PATH 上にない場合でも、既定候補 `D:\SteamLibrary\steamapps\common\Blender\blender.exe` または `BLENDER_EXE` を検出して非破壊 smoke を自動検証します。統合 `.blend` と部位別 `.blend` の Link reload は `docs/manual-test.md` と QCDS に明記します。
