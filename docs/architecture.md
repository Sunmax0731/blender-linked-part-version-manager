# アーキテクチャ

## 基本方針

Blender Link 操作、部位レジストリ、外部同期、検証レポートを分ける。UI は operator の入口に留め、実処理はテスト可能な core と adapter に置く。

## Options

| Option | 概要 | 強み | 弱み | 判定 |
| --- | --- | --- | --- | --- |
| A | Blender アドオン内に core と sync adapter を持つ | 導入が簡単で Blender 内で完結する | 長時間処理で UI 負荷に注意が必要 | MVP 採用 |
| B | 外部常駐アプリが Git / file sync を担当し Blender は表示だけ行う | 大規模チームや長時間処理に強い | installer と常駐権限が必要 | Deferred |
| C | Git hooks と手順書だけで運用する | 実装が少ない | Blender Link 状態を検出できず利用者負荷が高い | 不採用 |

MVP は Option A を採用する。処理が重くなる場合は adapter 実行を worker に逃がし、将来 Option B へ移行できる contract を保つ。

## Module Boundary

| Layer | Responsibility |
| --- | --- |
| `ui` | パネル、operator、ユーザー確認、結果表示 |
| `core.registry` | part registry の読み書き、schema validation、tag 正規化 |
| `core.plan` | status classification、sync plan 作成、risk 判定 |
| `adapters.git` | Git status / fetch / pull / push preview |
| `adapters.local` | 共有フォルダやローカル mirror の存在確認とコピー計画 |
| `blender.link` | linked library 検出、Link 追加、reload、broken link レポート |
| `report` | JSON / Markdown レポート、QCDS / release evidence 連携 |
| `windows` | Blender 外の registry 検証、設定保存、installer dry-run |
| `scripts` | docs、unit test、runtime gate、release package 検証 |

## Data Flow

```mermaid
flowchart LR
  A["Part Registry"] --> B["Sync Planner"]
  C["Integration .blend"] --> D["Blender Link Inspector"]
  D --> B
  E["Git / File Adapter"] --> B
  B --> F["Dry-run Report"]
  F --> G["User Confirmation"]
  G --> H["Fetch / Pull"]
  H --> I["Link Reload"]
  I --> J["Validation Result"]
  K["Windows Companion"] --> A
  K --> F
```

## Failure Policy

- `local-dirty` と `conflict-risk` は自動更新しない。
- `broken-link` は registry と Blender 側 Link の両方を表示し、ユーザーに修正候補を選ばせる。
- adapter 実行失敗時は `.blend` を保存せず、result JSON に終了コード、標準エラー要約、対象部位を残す。
- scheduled pull は MVP 後とし、まず manual / batch 操作を安定させる。
- Windows companion は `.blend` を開かず、設定保存と registry preview に限定する。
