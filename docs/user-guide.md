# ユーザーガイド

## 基本フロー

1. 統合 `.blend` と部位別 `.blend` の対応を registry JSON に記録する。
2. Blender の `Linked Parts` パネルで `Validate Registry` を実行する。
3. `Build Sync Preview` で更新候補、危険状態、reload 候補を確認する。
4. `local-dirty`、`conflict-risk`、`broken-link` がある場合は自動更新せず、担当者に確認する。
5. 問題がない部位だけ `Reload Safe Links` の dry-run を確認し、手動判断で reload する。

## Registry

必須項目は `partId`、`partTag`、`blendPath`、`linkedCollection`、`owner`、`source`、`versionRef`、`updatePolicy`。`partTag` は `Hair`、`Body`、`Face`、`Accessories`、`Clothes`、`Rig`、`Props` を使う。

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
