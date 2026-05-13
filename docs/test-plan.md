# テスト計画

## Automated Tests

| Test | 対象 | 合格条件 |
| --- | --- | --- |
| Docs completeness | 開発準備 docs | 必須ファイルが存在し UTF-8 として読める。 |
| Mojibake check | docs / samples / scripts | 典型的な文字化け断片や制御文字がない。 |
| Registry validation | Part Registry | 必須項目、tag、source、updatePolicy を検査できる。 |
| Sync plan classification | status classifier | `current`、`remote-newer`、`local-dirty`、`missing-link`、`broken-link`、`conflict-risk` を分類できる。 |
| Git fixture | Git adapter | fetch / status / pull dry-run の結果を安定して返す。 |
| Local fixture | local adapter | 共有フォルダ mirror の存在、更新日時、コピー候補を分類できる。 |

## Blender Runtime Gate

公開前に次を確認する。

1. Integration File を開く。
2. Hair、Body、Face、Accessories の Part File を Link する。
3. Part Registry を生成する。
4. Part File を更新した fixture を用意する。
5. `Pull & Reload` の dry-run を実行する。
6. 確認後に reload し、Viewport で更新が反映されることを確認する。
7. `dist/runtime-gate.json` に Blender version、対象ファイル、結果を保存する。

## Manual Tests

- GitHub remote が使える場合の pull / reload。
- local folder adapter だけで運用する場合の更新確認。
- Link 先が消えた場合の broken-link 表示。
- collection 名が registry と違う場合の mismatch 表示。
- local-dirty 時に自動更新が止まること。

## Current Status

現時点では実装前のため、`npm test` は docs / JSON / 文字化け検査のみを行う。Blender runtime gate は未実施であり、QCDS の Quality と Satisfaction は `B+` 以下に留める。
