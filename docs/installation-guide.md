# インストールガイド

## 前提

- Windows 10/11
- Blender 4.2 以降
- Node.js 20 以降
- Git CLI

## Alpha artifact

GitHub Release `v0.1.0-alpha.1` から次を取得する。

- `blender-linked-part-version-manager.zip`
- `blender-linked-part-version-manager-docs.zip`
- `blender-linked-part-version-manager-fixtures.zip`
- `manual-test.md`

## Blender add-on

1. Blender を開く。
2. `Edit > Preferences > Add-ons > Install...` を開く。
3. `blender-linked-part-version-manager.zip` を選択する。
4. `Blender Linked Part Version Manager` を有効化する。
5. View3D Sidebar の `Linked Parts` タブを開く。
6. `Registry Path` に registry JSON を指定し、`Validate Registry` と `Build Sync Preview` を実行する。

## Manual test fixtures

`blender-linked-part-version-manager-fixtures.zip` を任意の作業フォルダに展開する。展開後の構成は次の通り。

```text
integration/character_integration.blend
parts/hair/main_hair.blend
parts/body/base_body.blend
parts/face/main_face.blend
parts/accessories/glasses.blend
samples/representative-suite.json
```

Blender では `integration/character_integration.blend` を開き、add-on preferences の `Registry Path` に展開先の `samples/representative-suite.json` を指定する。

## Windows companion

repo または docs ZIP 展開先で次を実行する。

```powershell
windows\blpvm-companion.cmd --version
windows\blpvm-companion.cmd init-settings --registry samples\representative-suite.json
windows\install-alpha.cmd --dry-run
```

`init-settings` は `%APPDATA%\BlenderLinkedPartVersionManager\settings.json` を作成する。credential、token、`.blend` 本体は保存しない。

## Uninstall

- Blender では Add-ons から disable / remove する。
- Windows companion の設定は `%APPDATA%\BlenderLinkedPartVersionManager` を削除する。
