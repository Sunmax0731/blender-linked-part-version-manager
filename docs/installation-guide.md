# インストールガイド

## 前提

- Windows 10/11
- Blender 4.2 以降
- Node.js 20 以降
- Git CLI

## Alpha artifact

GitHub Release `v0.1.0-alpha.3` から次を取得する。

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
7. 既存の Link から registry を作る場合は `Scan Current Links`、内容確認後に `Save Registry` を実行する。
8. 新しい部位 `.blend` を追加する場合は `Add File Candidate` で選び、collection 一覧のチェックボックス、preview JSON の available collection / object、availableObjectDetails、recommended target を確認する。複数 collection を Link したい場合は対象 collection にチェックを入れる。Reference 用画像やライトは明示 object 名でだけ Link する。`Preview Link` 後に `Link Candidate` を実行する。現在の `.blend` は自動保存されないため、結果を確認してから手動で保存する。
9. linked file を current file に統合する場合は `Preview Integrate` で対象を確認し、`Integrate Link` の確認ダイアログを通す。実行後も現在の `.blend` は自動保存されない。

Blender の表示言語が日本語で Interface 翻訳が有効な場合、上記のタブ、ボタン、主要メッセージは日本語で表示される。

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
