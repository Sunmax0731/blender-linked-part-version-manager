# 機能一覧

Blender Linked Part Version Manager は、部位別 `.blend` を Link で統合する制作フローを、registry、preview、reload、manual evidence に分けて扱います。このページでは各機能が何をするか、何のために使うかを説明します。

## Part Registry

Part Registry は、統合 `.blend` が参照する部位別 `.blend` の一覧です。各部位に `partId`、`partTag`、`displayName`、`blendPath`、`linkedCollection`、`owner`、`source`、`versionRef`、`updatePolicy` を持たせます。

何のために使うか:

- どの部位がどの `.blend` にあるかを一覧化する
- Hair、Body、Face、Accessories などの担当範囲を明確にする
- 更新前 preview、reload、Auto Reload の対象を決める
- broken-link や missing-link を再現可能な JSON として残す

## Scan Current Links

`Scan Current Links` は、現在開いている Blender ファイルの `bpy.data.libraries` と linked collection を読み取り、Part Registry 候補を作ります。

何のために使うか:

- 既に Link 済みの統合 `.blend` から registry を作り始める
- JSON を手書きせず、実際の Blender Link 状態を起点にする
- linked library と collection の対応を確認する

## Editable Registry List

`Linked Parts` パネルには registry 候補の一覧と編集欄があります。候補を選ぶと、部位タグ、表示名、担当者、source、versionRef、updatePolicy などを編集できます。

何のために使うか:

- registry JSON を直接編集しなくても運用を始められる
- `owner=unassigned` の候補を担当者名に直す
- local source から git source へ切り替える
- scheduled / disabled などの update policy を整理する

## Save Registry

`Save Registry` は、GUI 上で編集した候補を `Registry Path` の JSON に保存します。保存前に validator を通し、必須項目や source の不備がある場合は保存を止めます。

何のために使うか:

- GUI で編集した内容をチーム共有できる registry として残す
- 保存後に `Validate Registry` と `Build Sync Preview` へつなげる
- `.blend` 本体ではなく、外部 JSON として管理する

## Add File Candidate

`Add File Candidate` は、Explorer / Blender file selector で選んだ `.blend` を registry 候補に追加します。初期値は安全側に寄せています。

初期値:

- `owner=unassigned`
- `source.type=local`
- `source.root=.`
- `versionRef=local`
- `updatePolicy=manual`

何のために使うか:

- 新しい部位ファイルを registry に追加する
- まだ Blender tree に Link していない `.blend` を候補化する
- Link する前に collection 名や担当者を確認する

## Preview Link / Link Candidate

`Preview Link` は、選択中の候補を Link する前の dry-run です。`Link Candidate` は、選択中の `.blend` collection を現在の Blender tree に明示的に Link します。

何のために使うか:

- Link 前に対象 path と collection を確認する
- 誤った `.blend` を Link するリスクを下げる
- Link 実行後も現在の `.blend` を自動保存しないことで、ユーザーが結果を見てから保存判断できるようにする

## Validate Registry

`Validate Registry` は、registry JSON の必須項目、重複、部位タグ、source 設定、update policy を検査します。

何のために使うか:

- チームで共有する前に registry の構造を確認する
- source path や owner の抜けを見つける
- Windows companion や CI 的な runtime gate でも同じ registry を検査する

## Build Sync Preview

`Build Sync Preview` は、registry と現在の Blender Link 状態から dry-run report を作ります。更新候補、blocked part、manual review が必要な部位をまとめます。

何のために使うか:

- reload 前に影響範囲を確認する
- `remote-newer` のような更新候補を見つける
- `local-dirty`、`conflict-risk`、`broken-link` を自動更新から外す
- report path に JSON evidence を残す

## Preview Reload / Reload Safe Links

`Preview Reload` は、safe な linked library だけを reload 対象として dry-run 表示します。`Reload Safe Links` は、blocked ではない対象だけ実際に reload します。

何のために使うか:

- 更新対象を見てから reload する
- broken-link や conflict-risk を避ける
- 統合 `.blend` の表示を最新化する

## Preview Integrate / Integrate Link

`Preview Integrate` は、選択中の registry 候補に対応する linked `.blend` を current file に統合した場合の対象 datablock と warning を dry-run 表示します。`Integrate Link` は確認ダイアログで不可逆操作、対象 linked file、出力先 current file を表示した後、linked datablock を local data にします。

何のために使うか:

- Link 参照を外し、1 つの `.blend` として受け渡せる状態にする
- 実行前に対象ファイルと出力先を確認する
- cancel 時に `.blend`、Link 状態、Part Registry を変更しない
- 実行後に `Report Path` の JSON とパネル preview で warning を確認する
- current file を自動保存せず、結果を見てからユーザーが保存判断する

## Auto Reload

`Start Auto Reload` は、保存済み linked `.blend` の更新時刻を監視し、安全な対象だけ reload します。`Stop Auto Reload` で監視を停止します。

何のために使うか:

- 別担当者が保存した部位 `.blend` の更新を統合側に反映しやすくする
- 手動 reload の回数を減らす
- 保存済みファイルだけを対象にして、未保存編集や危険状態を自動反映しない

## Japanese UI Localization

Blender の表示言語が日本語の場合、`Linked Parts` タブ、`Part Registry` パネル、主要ボタン、operator 名、Auto Reload status、主要 report message を日本語で表示します。

何のために使うか:

- 日本語表示の Blender 環境でも操作意図を読み取りやすくする
- Blender 標準の翻訳設定に追従し、英語環境では既存の英語表示を維持する
- JSON registry や dry-run report のキーは英語のまま保ち、チーム共有 evidence の互換性を崩さない

## Status Classification

registry と Link 状態は次の status に分類します。

| Status | 意味 | 使い方 |
| --- | --- | --- |
| `current` | 更新不要 | 操作不要 |
| `remote-newer` | 取得または reload 候補あり | dry-run 後に pull / reload を検討 |
| `local-dirty` | ローカル作業が残っている | 自動更新せず担当者に確認 |
| `missing-link` | registry にはあるが Blender に Link がない | Link 追加候補として確認 |
| `broken-link` | Link 先 path が見つからない | path 修正または再取得 |
| `conflict-risk` | 更新とローカル作業が衝突する可能性がある | 手動レビュー |
| `unknown` | 判断材料が足りない | registry と source を確認 |

## Windows Companion

Windows companion は Blender を起動せず registry を検証するための launcher です。

主な command:

```powershell
windows\blpvm-companion.cmd --version
windows\blpvm-companion.cmd validate-registry --registry samples\representative-suite.json
windows\blpvm-companion.cmd status --registry samples\representative-suite.json
windows\blpvm-companion.cmd init-settings --registry samples\representative-suite.json
windows\install-alpha.cmd --dry-run
```

何のために使うか:

- Blender を開く前に registry を検証する
- settings 保存先を確認する
- installer dry-run を release gate として確認する
- `.blend` 本体に触れずに環境確認する

## Manual Test Fixtures

release asset には manual test 用 fixture を同梱しています。

```text
integration/character_integration.blend
parts/hair/main_hair.blend
parts/body/base_body.blend
parts/face/main_face.blend
parts/accessories/glasses.blend
samples/representative-suite.json
```

何のために使うか:

- 初回導入後に `Linked Parts` パネルを試す
- registry validation、sync preview、reload を同じ条件で確認する
- 不具合報告時に再現 path と registry を揃える

## Release / Evidence Documents

リリースごとに QCDS、manual test、release evidence を残します。

関連ドキュメント:

- [インストールガイド](installation-guide.md)
- [ユーザーガイド](user-guide.md)
- [手動テスト手順](manual-test.md)
- [QCDS 評価](qcds-evaluation.md)
- [Release evidence](release-evidence.json)
