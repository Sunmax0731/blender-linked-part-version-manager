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
| GUI registry candidate defaults | Blender add-on / core.registry | scan / file selector 由来の候補が安全な local source 初期値を持ち、保存後に registry validator を通過する。 |
| GUI linked library scan | Blender add-on / blender.link | `bpy.data.libraries` と linked collection から `blendPath` と `linkedCollection` を持つ editable part 候補を生成できる。 |
| Link candidate target selection | Blender add-on / blender.link | `Add File Candidate` / `Preview Link` が available collection / object を report し、`ref` への先頭 fallback を避けて production collection / object を選ぶ。 |
| Japanese UI localization | Blender add-on / UI translations | `ja_JP` 翻訳テーブルが主要 panel、operator、button、property、message を持ち、Blender の `pgettext_iface` で日本語へ解決できる。 |
| Link integration helper | Blender add-on / blender.link | dry-run は対象 datablock を報告するだけで local 化せず、実行時は選択 target の linked datablock だけを local 化する。 |
| Release artifact check | dist / docs | add-on ZIP、docs ZIP、test summary、runtime gate、QCDS metrics が存在する。 |

## Blender Runtime Gate

手動 host test で次を確認する。

1. `blender-linked-part-version-manager-fixtures.zip` を展開する。
2. Integration File `integration/character_integration.blend` を開く。
3. Part Registry を生成する。
4. `Scan Current Links` で linked library / collection から editable 候補が生成されることを確認する。
5. `Add File Candidate` で Explorer / Blender file selector から `.blend` を候補追加し、`Preview Link` が dry-run 結果を出すことを確認する。
6. `Save Registry` 後に `Validate Registry` と `Build Sync Preview` が通ることを確認する。
7. Part File を更新した fixture を用意する。
8. `Pull & Reload` の dry-run を実行する。
9. 確認後に reload し、Viewport で更新が反映されることを確認する。
10. `Start Auto Reload` 後に Hair source `.blend` を保存し、interval 内に Viewport へ反映されることを確認する。
11. `Preview Integrate` で対象 linked file と report が表示されることを確認する。
12. `Integrate Link` の確認ダイアログを cancel し、`.blend`、Link 状態、Part Registry が変わらないことを確認する。
13. コピーした fixture で `Integrate Link` を確認あり実行し、linked datablock が local data になり、report に warning / result が残ることを確認する。
14. Blender の表示言語を日本語に変更し、`Linked Parts` タブ、`Part Registry` パネル、主要ボタン、Auto Reload status、operator report が日本語表示になることを確認する。
15. `dist/runtime-gate.json` に Blender version、対象ファイル、結果を保存する。

## Manual Tests

- GitHub remote が使える場合の pull / reload。
- local folder adapter だけで運用する場合の更新確認。
- Link 先が消えた場合の broken-link 表示。
- collection 名が registry と違う場合の mismatch 表示。
- local-dirty 時に自動更新が止まること。

## Current Status

`npm test` は docs / JSON / 文字化け検査、Python unit test、Windows runtime gate、Blender CLI smoke、release package、release artifact check を行う。2026-05-15 時点で `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、add-on import smoke は通過済み。追加で `register()` / `unregister()` smoke も通過済み。統合 `.blend` と部位別 `.blend` の Link reload / Viewport 反映はユーザー手元の Blender 5.1.1 で手動確認済み。

2026-05-15 時点で GUI registry candidate defaults、linked library scan、Japanese UI localization table coverage、link integration dry-run / localize helper は Python unit test に追加済み。Blender 5.1.1 CLI で `preferences.view.language='ja_JP'`、`use_translate_interface=True` を設定し、`Scan Current Links` と `Part Registry` が日本語へ解決されることを確認済み。Blender UI 上の `Scan Current Links`、`Save Registry`、`Add File Candidate`、`Preview Link`、`Link Candidate`、`Preview Integrate`、`Integrate Link`、日本語 UI 表示は次回 manual test で実機確認する。

2026-05-16 時点で `D:\Work\Blender\Shirayukikokoro\blender\base_blender\base.blend` を Blender 5.1.1 CLI で inspection し、available collection が `ref`、`Collection`、`2_acc`、`1_costume`、`0_hair`、available object が `base_face`、`base_body`、`Armature` などであることを確認した。修正後の `Preview Link` はファイル名既定値 `base` から先頭 `ref` へ fallback せず、recommended collection `1_costume` を dry-run に出す。
