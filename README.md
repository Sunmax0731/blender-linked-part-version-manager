# Blender Linked Part Version Manager

Blender Linked Part Version Manager は、キャラクターや複合モデルを **Hair / Body / Face / Accessories** などの部位別 `.blend` に分けて制作し、統合用 `.blend` では Blender Link で安全に確認するための Blender アドオンです。

部位ごとの担当者、リンク元ファイル、更新状態、reload 対象を Part Registry として管理し、更新前に dry-run で影響範囲を確認できます。Windows では Blender を起動せず registry を検証する companion launcher も同梱しています。

## できること

- 現在の Blender Link から Part Registry を生成する
- GUI で partId、部位タグ、担当者、リンク先 collection、source、versionRef、updatePolicy を編集する
- `.blend` ファイルを選んで Link 候補として追加し、ファイル内の collection / object 候補を確認してから Blender tree に Link する
- 読み込んだ `.blend` の collection 一覧をチェックボックスで確認し、チェック済み collection をまとめて Link する
- Link した Collection が別 `.blend` を参照している場合、Preview / Link report で source linked library と indirect linked library を確認する
- Reference 画像、ライト、カメラなど 3D モデル以外の object も型付き候補として report し、明示選択した場合だけ Link する
- registry の不備、missing-link、broken-link、local-dirty、conflict-risk を確認する
- 更新前に sync preview を作り、安全な linked library だけ reload する
- 保存済み linked `.blend` の変更を監視し、安全な対象だけ Auto Reload する
- 選択した linked `.blend` を確認ダイアログ後に現在の Blender ファイルへ統合する
- Blender の表示言語が日本語の場合、パネル、ボタン、主要メッセージを日本語で表示する
- Windows companion で registry validation、status preview、settings 保存、installer dry-run を実行する
- `Character.blend` と素体、頭 / 表情、髪、服、アクセサリの参照関係を関係表として確認する

詳しい機能は [機能一覧](docs/features.md) を参照してください。

## 想定する利用者

- 複数人で 3D キャラクターや装備、衣装、表情、髪型を分担制作しているチーム
- 統合用 Blender ファイルと部位別 Blender ファイルを分けて管理したいリードモデラー
- Git、共有フォルダ、NAS などで `.blend` を受け渡しながら Link 切れや取得漏れを減らしたい制作チーム
- 更新前に「どの部位が変わるか」「危険な状態があるか」を確認してから reload したいユーザー

## インストール

1. GitHub Releases から正式リリース `v0.1.0` の `blender-linked-part-version-manager.zip` を取得する。
2. Blender を開き、`Edit > Preferences > Add-ons > Install...` を選ぶ。
3. `blender-linked-part-version-manager.zip` を選択して install する。
4. `Blender Linked Part Version Manager` を有効化する。
5. View3D Sidebar の `Linked Parts` タブを開く。

手順の詳細と fixture の展開方法は [インストールガイド](docs/installation-guide.md) を参照してください。

## 基本的な使い方

### 1. Registry を用意する

既存の統合 `.blend` に Link が入っている場合は、`Linked Parts` パネルで `Scan Current Links` を実行します。現在の linked library / collection から Part Registry 候補が作られます。

新しい部位ファイルを追加したい場合は、`Add File Candidate` で `.blend` を選びます。候補は `.blend` 内の collection / object 名と object 種別を確認し、collection 一覧をチェックボックスとして表示します。`ref` や camera / light だけを暗黙選択しない安全な初期値で追加されます。

- `owner=unassigned`
- `source.type=local`
- `source.root=.`
- `versionRef=local`
- `updatePolicy=manual`

### 2. GUI で内容を確認して保存する

候補リストから部位を選び、次の項目を編集します。

- `partId`
- `partTag`
- `displayName`
- `blendPath`
- `linkedCollection`
- `owner`
- `source`
- `versionRef`
- `updatePolicy`

内容を確認したら `Save Registry` で `Registry Path` に JSON として保存します。

### 3. Registry を検証する

`Validate Registry` を実行すると、必須項目、重複 partId、未知の部位タグ、source 設定などを検査できます。問題がある場合は、保存前または保存後に GUI で修正します。

### 4. 更新前プレビューを作る

`Build Sync Preview` を実行すると、registry と現在の Link 状態から dry-run report を作ります。`local-dirty`、`conflict-risk`、`broken-link` のような危険状態がある部位は自動更新対象から外します。

### 5. Link / Reload を実行する

新しい候補を Link する場合は、先に `Preview Link` で dry-run を確認し、問題がなければ `Link Candidate` を実行します。collection 一覧にチェックが入っている場合は、チェック済み collection だけをまとめて Link します。source `.blend` 内の Collection が別 `.blend` を参照している場合は、Preview JSON に `sourceLinkedLibraries`、実行結果に `linkedLibraries` と `indirectLinkedLibraries` が表示されます。`linkedCollection` が `.blend` 内に存在しない場合でも、ファイル名から自動生成された既定値なら production collection を推奨し、collection がない場合は `Armature` や mesh などの production object を Link 対象にします。Reference 画像、ライト、カメラは object 種別付きの明示候補として表示し、自動選択しません。明示的に入力した collection / object 名が存在しない場合や、floor など非対応 helper の場合は、先頭 collection へ勝手に fallback せず失敗理由と候補一覧を表示します。

既存の linked library を更新する場合は、先に `Preview Reload` を確認し、問題がなければ `Reload Safe Links` を実行します。現在の `.blend` は自動保存されないため、結果を確認してから手動で保存してください。

### 6. linked file を統合する

Link 参照を 1 つの `.blend` にまとめたい場合は、registry 候補を選択して `Preview Integrate` を確認し、対象ファイルと出力先を確認してから `Integrate Link` を実行します。統合は linked datablock を current file の local data にする操作で、現在の `.blend` は自動保存されません。結果と warning は `Report Path` に JSON として保存されます。

### 7. Auto Reload を使う

`Start Auto Reload` を実行すると、保存済み linked `.blend` の更新時刻を監視し、安全な対象だけ reload します。別 Blender ウィンドウで未保存のまま編集している内容は `.blend` に書き込まれていないため、Auto Reload では反映されません。

## Windows Companion

Blender を起動せず registry や設定保存だけを確認したい場合に使います。

```powershell
windows\blpvm-companion.cmd --version
windows\blpvm-companion.cmd validate-registry --registry samples\representative-suite.json
windows\blpvm-companion.cmd status --registry samples\representative-suite.json
windows\blpvm-companion.cmd init-settings --registry samples\representative-suite.json
windows\install-alpha.cmd --dry-run
```

`init-settings` は `%APPDATA%\BlenderLinkedPartVersionManager\settings.json` に設定を保存します。credential、token、`.blend` 本体は保存しません。

## 安全設計

- reload / Link は preview と明示実行を分ける
- linked file 統合は確認ダイアログを挟み、`.blend` を自動保存しない
- `.blend` は自動保存しない
- `local-dirty`、`conflict-risk`、`broken-link` は自動更新しない
- Windows companion は `.blend` を変更しない
- registry と dry-run report を JSON として残せる

## 追加ドキュメント

- [機能一覧](docs/features.md)
- [Character.blend 統合構成の関係表](docs/character-blend-relationship.md)
- [インストールガイド](docs/installation-guide.md)
- [ユーザーガイド](docs/user-guide.md)
- [手動テスト手順](docs/manual-test.md)
- [仕様](docs/specification.md)
- [アーキテクチャ](docs/architecture.md)

## 開発者向け

```powershell
cd D:\AI\BlenderAddon\blender-linked-part-version-manager
npm test
```

`npm test` は docs check、Python unit test、Windows runtime gate、Blender CLI smoke、release package 生成、release artifact check を実行します。

## Release

現在の正式リリースは `v0.1.0` です。直前の prerelease は `v0.1.0-alpha.3`、Blender add-on / Windows companion の実装バージョンは `0.1.2` です。変更点と既知事項は [v0.1.0 release notes](docs/releases/v0.1.0.md) を参照してください。

Public repo: https://github.com/Sunmax0731/blender-linked-part-version-manager
