# Blender Linked Part Version Manager

Blender Linked Part Version Manager は、統合用 `.blend` と部位別作業 `.blend` を分けて共同制作するチーム向けの Blender アドオンと Windows companion launcher です。Hair、Body、Face、Accessories などの部位タグ、外部リポジトリまたはファイル管理システムからの取得、Blender Link の再読み込み、更新前プレビューを同じ作業単位で扱います。

## Source

- Domain / Idea No: BlenderAddon / 7
- Repository: blender-linked-part-version-manager
- Public repo: `https://github.com/Sunmax0731/blender-linked-part-version-manager`
- created_idea: `D:/AI/BlenderAddon/created_idea_007_blender-linked-part-version-manager`
- 同梱 ZIP: `D:/AI/BlenderAddon/created_idea_007_blender-linked-part-version-manager/idea_007_blender-linked-part-version-manager.zip`
- 主な公開先: GitHub Release / Blender Extensions / Windows alpha launcher

## 目標

- 統合用 Blender ファイルが、部位別 `.blend` を Link で参照する構成を安全に維持する。
- 各作業者が担当部位を push し、他の作業者が任意または定期タイミングで pull して最新表示できる流れを定義する。
- 部位タグ、担当者、リンク元、取得状態、検証結果を一覧化し、更新時の見落としを減らす。

## MVP スコープ

- 部位レジストリ JSON の定義と検証
- Git / ローカルファイル管理を抽象化する同期アダプタ MVP
- Blender Link 対象の検出、再読み込み、更新前 dry-run のアドオン shell
- Windows companion launcher による registry 検証、状態 preview、設定保存
- 代表シナリオと手動検証手順
- QCDS、release checklist、docs ZIP、closed alpha release evidence

## 主要コンポーネント

- `addon/blender_linked_part_version_manager/`: Blender 4.2 以降向けアドオン。
- `addon/blender_linked_part_version_manager/core/`: Blender 非依存の registry validation と sync plan。
- `addon/blender_linked_part_version_manager/adapters/`: Git / local folder の dry-run adapter。
- `windows/`: Windows companion launcher と alpha installer dry-run。
- `scripts/`: docs、unit test、runtime gate、release package の検証。

## 開発コマンド

```powershell
cd D:\AI\BlenderAddon\blender-linked-part-version-manager
npm test
```

`npm test` は docs/JSON/文字化け検査、Python unit test、Windows runtime gate、release package 生成、release artifact 検査を実行します。

## Windows Alpha Launcher

```powershell
windows\blpvm-companion.cmd --version
windows\blpvm-companion.cmd validate-registry --registry samples\representative-suite.json
windows\blpvm-companion.cmd init-settings --registry samples\representative-suite.json
windows\install-alpha.cmd --dry-run
```

`init-settings` は `%APPDATA%\BlenderLinkedPartVersionManager\settings.json` に設定を保存します。credential、token、`.blend` 本体は保存しません。

## Alpha Release Notes

`v0.1.0-alpha.1` は prerelease として公開し、リリース後に Blender 実機で Link reload の手動確認を行います。Codex 環境では `D:\SteamLibrary\steamapps\common\Blender\blender.exe` を検出し、Blender 5.1.1 の CLI smoke とアドオン import は通過済みです。統合 `.blend` と部位別 `.blend` の Link reload は手動確認として残します。
