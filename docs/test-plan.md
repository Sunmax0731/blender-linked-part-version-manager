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
| Windows runtime gate | companion launcher / installer | local executable 起動、settings 保存、installer dry-run が成功する。 |
| Blender CLI smoke | Blender host | `BLENDER_EXE`、`D:\SteamLibrary\steamapps\common\Blender\blender.exe`、PATH のいずれかで Blender を検出し、`--version` と add-on import smoke が成功する。 |
| Blend fixture packaging | manual-test assets | integration `.blend`、部位別 `.blend`、registry が release fixture ZIP に同梱される。 |
| Auto Reload target selection | Blender add-on | `current` / `remote-newer` の saved linked files だけが監視対象になり、blocked part は対象外になる。 |
| Release artifact check | dist / docs | add-on ZIP、docs ZIP、test summary、runtime gate、QCDS metrics が存在する。 |

## Blender Runtime Gate

手動 host test で次を確認する。

1. `blender-linked-part-version-manager-fixtures.zip` を展開する。
2. Integration File `integration/character_integration.blend` を開く。
3. Part Registry を生成する。
4. Part File を更新した fixture を用意する。
5. `Pull & Reload` の dry-run を実行する。
6. 確認後に reload し、Viewport で更新が反映されることを確認する。
7. `Start Auto Reload` 後に Hair source `.blend` を保存し、interval 内に Viewport へ反映されることを確認する。
8. `dist/runtime-gate.json` に Blender version、対象ファイル、結果を保存する。

## Manual Tests

- GitHub remote が使える場合の pull / reload。
- local folder adapter だけで運用する場合の更新確認。
- Link 先が消えた場合の broken-link 表示。
- collection 名が registry と違う場合の mismatch 表示。
- local-dirty 時に自動更新が止まること。

## Current Status

`npm test` は docs / JSON / 文字化け検査、Python unit test、Windows runtime gate、Blender CLI smoke、release package、release artifact check を行う。2026-05-15 時点で `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、add-on import smoke は通過済み。統合 `.blend` と部位別 `.blend` の Link reload / Viewport 反映はリリース後の手動確認として残す。
