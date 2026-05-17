# ユーザーガイド

各機能の詳しい説明は [機能一覧](features.md) を参照してください。

`Character.blend` と素体、頭 / 表情、髪、服、アクセサリの参照方向を先に整理したい場合は [Character.blend 統合構成の関係表](character-blend-relationship.md) を参照してください。

## 基本フロー

1. 統合 `.blend` と部位別 `.blend` の対応を registry JSON に記録する。
2. JSON がまだない場合は Blender の `Linked Parts` パネルで `Scan Current Links` を実行し、GUI 上の候補を編集して `Save Registry` で保存する。
3. 追加の `.blend` は `Add File Candidate` で選ぶ。preview に available collection / object、recommended target、sourceLinkedLibraries が出るので、`linkedCollection` と dependency を確認してから `Preview Link`、`Link Candidate` の順に現在の Blender tree へ明示的に Link する。
4. `Validate Registry` を実行する。
5. `Build Sync Preview` で更新候補、危険状態、reload 候補を確認する。
6. `local-dirty`、`conflict-risk`、`broken-link` がある場合は自動更新せず、担当者に確認する。
7. 問題がない部位だけ `Reload Safe Links` の dry-run を確認し、手動判断で reload する。
8. Link 参照を 1 つの `.blend` にまとめる必要がある場合だけ、対象候補を選び `Preview Integrate` と `Integrate Link` の確認ダイアログを通す。

## Character.blend 統合構成

`Character.blend` は素体、頭 / 表情、髪、服、アクセサリを Link して統合表示する確認用ファイルとして扱う。頭 / 表情、髪、服、アクセサリの各 Part File は素体用 `.blend` を参照しながら個別編集し、最終表示は `Character.blend` 側で reload して確認する。

アドオンの Link 管理対象は `Character.blend` が直接参照する Part File である。素体用 `.blend` が各 Part File から参照される関係は制作上の依存として関係表と検証レポートで確認し、外部 sync や `.blend` 自動保存とは混ぜない。

## Registry

必須項目は `partId`、`partTag`、`blendPath`、`linkedCollection`、`owner`、`source`、`versionRef`、`updatePolicy`。`partTag` は `Hair`、`Body`、`Face`、`Accessories`、`Clothes`、`Rig`、`Props` を使う。

GUI で生成した候補は `owner=unassigned`、`source.type=local`、`source.root=.`、`versionRef=local`、`updatePolicy=manual` で始まる。チーム運用に合わせて owner、Git source、branch、versionRef を編集してから保存する。

## Link 候補の選び方

`Add File Candidate` は source `.blend` 内の collection / object 名と object 種別を読み取り、collection 一覧をチェックボックスとして表示する。複数 collection を Link したい場合は対象 collection にチェックを入れてから `Preview Link` / `Link Candidate` を実行する。チェック済み collection がある場合は、その collection だけが Link 対象になる。

source `.blend` の Collection が別 `.blend` を Link している場合、Preview JSON の `sourceLinkedLibraries` で依存 library を確認できる。`Link Candidate` 実行後は、直接 source が `linkedLibraries`、Blender が読み込んだ依存 library が `indirectLinkedLibraries` に出る。依存 library は report 対象であり、この操作では local 化や自動保存をしない。

`ref`、`reference`、camera、light、floor 系は暗黙選択しない。目的データが collection ではなく scene 直下 object の場合は、`Armature` や mesh 名を production object として Link 対象にする。Reference 用画像、ライト、カメラは `availableObjectDetails` に explicit candidate として出るため、Link したい場合は object 名を `linkedCollection` に明示してから `Preview Link` / `Link Candidate` を実行する。floor helper などの非対応 object は除外理由を preview に表示する。明示的に入力した `linkedCollection` が存在しない場合は、先頭 collection へ勝手に fallback せず、候補一覧と失敗理由を preview に表示する。

## Status

| Status | 意味 | 推奨操作 |
| --- | --- | --- |
| `current` | 更新不要 | 操作しない |
| `remote-newer` | 取得候補あり | dry-run を確認して pull / reload |
| `local-dirty` | ローカル変更あり | 自動更新せず publish / stash 判断 |
| `missing-link` | registry にあるが Link されていない | Link 追加を手動確認 |
| `broken-link` | Link 先が見つからない | path 修正または取得 |
| `conflict-risk` | 競合可能性あり | 担当者と手動確認 |

## Windows companion

Blender を起動せず、registry と設定保存だけを確認する。

```powershell
windows\blpvm-companion.cmd validate-registry --registry samples\representative-suite.json
windows\blpvm-companion.cmd status --registry samples\representative-suite.json
```

Windows companion は `.blend` を変更しない。Blender Link の reload は Blender add-on 側の確認操作で行う。

## Link 統合

`Integrate Link` は選択中の linked `.blend` の datablock を current file の local data に変える。実行前に対象ファイル、出力先、不可逆操作であることを確認し、cancel した場合は何も変更しない。実行後も current file は自動保存されないため、`Report Path` の JSON と Viewport を確認してから手動で保存する。

## 表示言語

Blender の表示言語が日本語で Interface 翻訳が有効な場合、`Linked Parts` パネルの主要ボタン、設定名、操作メッセージは日本語で表示される。英語やその他の言語では既存の英語表示に戻る。
