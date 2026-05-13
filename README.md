# Blender Linked Part Version Manager

Blender Linked Part Version Manager は、統合用 `.blend` と部位別作業 `.blend` を分けて共同制作するチーム向けの Blender アドオン案です。Hair、Body、Face、Accessories などの部位タグ、外部リポジトリまたはファイル管理システムからの取得、Blender Link の再読み込み、更新前プレビューを同じ作業単位で扱います。

## Source

- Domain / Idea No: BlenderAddon / 7
- Repository: blender-linked-part-version-manager
- Public repo: `https://github.com/Sunmax0731/blender-linked-part-version-manager`
- created_idea: `D:/AI/BlenderAddon/created_idea_007_blender-linked-part-version-manager`
- 同梱 ZIP: `D:/AI/BlenderAddon/created_idea_007_blender-linked-part-version-manager/idea_007_blender-linked-part-version-manager.zip`
- 主な公開先: GitHub Release / Blender Extensions

## 目標

- 統合用 Blender ファイルが、部位別 `.blend` を Link で参照する構成を安全に維持する。
- 各作業者が担当部位を push し、他の作業者が任意または定期タイミングで pull して最新表示できる流れを定義する。
- 部位タグ、担当者、リンク元、取得状態、検証結果を一覧化し、更新時の見落としを減らす。

## MVP スコープ

- 部位レジストリ JSON の定義と検証
- GitHub / ローカルファイル管理を抽象化する同期アダプタ設計
- Blender Link 対象の検出、再読み込み、更新前 dry-run の仕様化
- 代表シナリオと手動検証手順
- QCDS、競合比較、release checklist の初期版

## 開発コマンド

```powershell
cd D:\AI\BlenderAddon\blender-linked-part-version-manager
npm test
```

現時点では実装前の開発準備段階です。`npm test` は必須ドキュメント、JSON、文字化け断片、代表シナリオ定義を検査します。
