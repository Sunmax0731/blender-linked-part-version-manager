# 仕様

## 用語

| 用語 | 意味 |
| --- | --- |
| Integration File | 全体確認用の `.blend`。部位別ファイルを Link で参照する。 |
| Part File | Hair、Body、Face などの担当者が編集する部位別 `.blend`。 |
| Part Registry | 部位と Link、外部取得元、担当者、バージョン参照を保持する JSON。 |
| Sync Plan | 取得、reload、検証、push 前確認の予定をまとめた dry-run 結果。 |
| Sync Adapter | GitHub、Git CLI、ローカル共有フォルダなど外部取得元を抽象化する実装境界。 |

## Registry Schema

MVP の registry は `samples/representative-suite.json` の `parts` 配列を基準にする。

```json
{
  "partId": "hair-main",
  "partTag": "Hair",
  "displayName": "Main Hair",
  "blendPath": "parts/hair/main_hair.blend",
  "linkedCollection": "CHR_Hair_Main",
  "owner": "artist-a",
  "source": {
    "type": "git",
    "remote": "origin",
    "branch": "main",
    "path": "parts/hair/main_hair.blend"
  },
  "versionRef": "main",
  "updatePolicy": "manual",
  "lastSync": null
}
```

## Sync Modes

| Mode | 内容 | 既定 |
| --- | --- | --- |
| Manual Pull | ユーザー操作で取得し、結果を確認して reload する。 | Yes |
| Scheduled Pull | タイマーで status / fetch / pull 相当を実行し、reload は確認付きにする。 | MVP 後 |
| Batch Refresh | 複数部位を一括取得して Link を再読み込みする。 | Yes |
| Push Part | 担当部位を commit / push する前の確認を行う。 | MVP 後 |

## Status Classification

| Status | 意味 | 操作 |
| --- | --- | --- |
| `current` | 取得元と Link が一致している。 | 操作不要 |
| `remote-newer` | 取得元が新しい。 | pull / reload 候補 |
| `local-dirty` | ローカル部位ファイルに未保存または未 commit 変更がある。 | push / stash / skip 判断 |
| `missing-link` | Integration File に該当 library / collection がない。 | Link 追加候補 |
| `broken-link` | Link パスが存在しない。 | パス修正または取得 |
| `conflict-risk` | 取得元更新とローカル変更が競合する可能性がある。 | 自動更新禁止 |

## Blender Operations

- Link 追加: `bpy.data.libraries.load(..., link=True)` を使う方針で設計する。
- Link 状態検出: `bpy.data.libraries` と linked collection / object の library 情報を照合する。
- Reload: linked library の reload API を使用し、失敗時は registry と result に原因を残す。
- 保存: MVP では自動保存しない。ユーザー確認後の保存を手動手順に残す。

## Adapter Contract

各 sync adapter は次の contract を返す。

```json
{
  "adapter": "git",
  "partId": "hair-main",
  "status": "remote-newer",
  "plannedActions": ["fetch", "pull", "reload-link"],
  "risk": "low",
  "messages": ["Remote branch main has newer file metadata."]
}
```

## Security and Privacy

- 認証情報は registry に保存しない。
- GitHub token を扱う場合もアドオン設定へ平文保存しない。
- ローカルパスを外部レポートへ出す場合は、ユーザーが明示的に export した場合だけにする。
