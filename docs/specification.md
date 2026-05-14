# 仕様

## 用語

| 用語 | 意味 |
| --- | --- |
| Integration File | 全体確認用の `.blend`。部位別ファイルを Link で参照する。 |
| Part File | Hair、Body、Face などの担当者が編集する部位別 `.blend`。 |
| Part Registry | 部位と Link、外部取得元、担当者、バージョン参照を保持する JSON。 |
| Sync Plan | 取得、reload、検証、push 前確認の予定をまとめた dry-run 結果。 |
| Sync Adapter | GitHub、Git CLI、ローカル共有フォルダなど外部取得元を抽象化する実装境界。 |
| Windows Companion | Blender 外で registry 検証、status preview、設定保存を行う alpha 用 launcher。 |

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
| Auto Reload | 保存済み linked `.blend` の更新時刻を一定間隔で監視し、安全な対象だけ reload する。 | Yes |
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
- Auto Reload: 未保存変更は対象外とし、保存済み `.blend` の mtime が増えた場合だけ reload する。外部 pull / push は実行しない。
- 保存: MVP では自動保存しない。ユーザー確認後の保存を手動手順に残す。

## GUI Registry Editing

`Linked Parts` パネルは Part Registry を直接 JSON 編集しなくても扱えるようにする。

| 操作 | 内容 | 破壊的変更 |
| --- | --- | --- |
| `Scan Current Links` | `bpy.data.libraries` と linked collection から registry 候補を作成する。 | なし |
| `Add File Candidate` | Explorer / Blender file selector で選んだ `.blend` を local source の registry 候補として追加する。 | なし |
| `Save Registry` | GUI 上の候補を `Registry Path` の JSON に保存し、既存 validator で検証する。 | registry JSON のみ |
| `Preview Link` | 選択候補を現在の Blender tree へ Link する前の dry-run を表示する。 | なし |
| `Link Candidate` | 選択候補の collection を現在の Blender tree へ明示的に Link する。 | 現在の Blender session のみ。自動保存しない。 |

GUI 生成候補の初期値は `owner=unassigned`、`source.type=local`、`source.root=.`、`versionRef=local`、`updatePolicy=manual` とする。

## UI Localization

Blender UI は英語を既定表示とし、Blender の表示言語が日本語の場合だけ `ja_JP` 翻訳を適用する。

| 対象 | 仕様 |
| --- | --- |
| パネル / タブ | `Part Registry`、`Linked Parts` を日本語へ翻訳する。 |
| Operator / ボタン | `Scan Current Links`、`Save Registry`、`Preview Link`、`Reload Safe Links` など主要操作を日本語へ翻訳する。 |
| Properties | `Registry Path`、`Report Path`、`Auto Reload Interval`、registry 編集欄の表示名を日本語へ翻訳する。 |
| Messages | `self.report` と Auto Reload status の主要メッセージを `pgettext_iface` helper 経由で翻訳する。 |
| Fallback | Blender が日本語以外または UI 翻訳無効の場合は英語の msgid をそのまま表示する。 |

翻訳登録は Blender 標準の `bpy.app.translations.register(__name__, BLPVM_TRANSLATIONS)` を使い、アドオンの `unregister()` で解除する。

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

## Windows Companion Contract

`windows/blpvm-companion.cmd` は次の command を提供する。

| Command | 内容 |
| --- | --- |
| `--version` | launcher version を表示する。 |
| `validate-registry --registry <path>` | registry JSON の必須項目と重複を検査する。 |
| `status --registry <path>` | registry の代表 status を JSON で表示する。 |
| `init-settings --registry <path>` | `%APPDATA%` 配下に設定 JSON を保存する。 |

`windows/install-alpha.cmd --dry-run` は installer 起動確認用であり、dry-run ではファイルコピーを行わない。
