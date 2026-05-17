# QCDS 評価

## Current Evaluation

| 観点 | 評価 | 理由 |
| --- | --- | --- |
| Quality | A- | registry validation、sync plan、Git/local adapter、Blender add-on shell、GUI registry editing、Character.blend 関係表、Link candidate collection/object selection、collection checkbox multi-link、indirect linked library report、Link target type expansion、Japanese UI localization、Windows runtime gate、Blender CLI smoke、manual reload、Auto Reload target selection、linked file integration helper、unit test、正式リリース docs check が通っている。 |
| Cost | A- | core、adapter、Blender binding、Windows companion を分離し、MVP の依存を Git / local folder / Node launcher に抑えている。Character.blend 関係表では素体依存を hidden transitive reload として実装せず、docs / registry / report の確認事項として扱う。 |
| Delivery | A- | README、AGENTS、SKILL、docs、TODO、Issues、release checklist、docs ZIP、fixture ZIP、release notes、runtime gate evidence、Blender 実体パス検証 evidence、GUI registry editing evidence、Character.blend 関係表、正式リリース `v0.1.0` evidence を同期した。 |
| Satisfaction | A- | Blender UI shell、GUI での registry 生成・編集・保存、Character.blend と素体 / 頭・表情 / 髪 / 服 / アクセのユースケース整理、日本語表示環境での主要 UI 翻訳、Explorer / Blender file selector からの Link 候補追加、読み込んだ collection をチェックボックスで複数 Link する導線、source `.blend` 内の nested Link dependency を report する導線、`ref` 誤リンクを避ける候補 inspection、Reference 用画像 / ライト / カメラの型付き明示 Link 候補、linked file 統合の preview / confirmation / report、Windows companion、手動テスト fixture で dry-run、手動 reload、保存後の Viewport 反映を確認できる。Auto Reload は保存済みファイル監視として未保存編集の限界を明記した。 |

## Gate

Windows アプリとしての platform runtime gate は local executable / installer dry-run 起動で `passed`。Blender host は `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、CLI smoke、アドオン import、`register()` / `unregister()` smoke が通過済み。ユーザー手元の Blender 5.1.1 で add-on install、fixture 表示、registry validation、sync preview、Preview Reload、Reload Safe Links、保存後の Viewport 反映を確認済み。Auto Reload は保存済み linked `.blend` の mtime 監視として追加した。
GUI registry editing は Python unit test で候補生成初期値と linked library scan を検証済み。Blender 上の `Scan Current Links`、`Save Registry`、`Add File Candidate`、`Preview Link`、`Link Candidate` は次回手動確認項目に追加済み。
Link candidate collection/object selection は Python unit test で production collection / object selection、missing collection 時の先頭 `ref` fallback 禁止を検証済み。Blender 5.1.1 CLI で `D:\Work\Blender\Shirayukikokoro\blender\base_blender\base.blend` の available collection / object を inspection し、修正後の dry-run が `ref` ではなく `1_costume` を recommended target にすることを確認済み。
Collection checkbox multi-link は Python unit test でチェック済み collection の dry-run / execute と missing collection の事前失敗を検証済み。Blender UI 上の checkbox 表示と複数 collection Link は次回手動確認項目に追加済み。
Indirect linked library report は Python unit test で source dependency inspection と Link 実行時の indirect library report を検証済み。Blender UI 上の `sourceLinkedLibraries` / `indirectLinkedLibraries` 確認は次回手動確認項目に追加済み。
Link target type expansion は Python unit test で Reference 用画像 object と light object が explicit candidate として `availableObjectDetails` に出ること、ファイル名既定値から暗黙選択されないこと、明示 object 名なら Link できること、floor helper は除外理由付きで失敗することを検証済み。
Japanese UI localization は Python unit test で主要 translation table coverage を検証し、Blender 5.1.1 CLI で `ja_JP` の `pgettext_iface` が `Scan Current Links` と `Part Registry` を日本語へ解決することを確認済み。
Link integration は Python unit test で dry-run が local 化しないこと、確認あり実行側の helper が選択 target の linked datablock だけを local 化することを検証済み。Blender UI 上の confirmation cancel / 実統合は次回手動確認項目に追加済み。
Character.blend 関係表は `docs/character-blend-relationship.md` に追加し、素体が頭 / 表情、髪、服、アクセサリから参照される関係、`Character.blend` 側の統合表示、Part Registry / Link 管理 / 検証レポートの責務分離を README、features、user guide、design、architecture、manual test へ接続済み。

## Formal Release v0.1.0

`v0.1.0` は `v0.1.0-alpha.3` の配布内容を正式リリース化する。実装バージョンは `0.1.2` のまま維持し、利用者向け README、installation guide、release notes、release checklist、release evidence、TODO / Issues を正式リリース向けに同期する。GitHub Release は prerelease ではなく通常 release とし、同じ配布物名で add-on ZIP、docs ZIP、fixture ZIP、manual-test.md を紐づける。

## S 評価へ必要な TODO

| 観点 | 現状 | S 評価へ必要な TODO |
| --- | --- | --- |
| Quality | Automated gate と Blender CLI smoke は通過済み。Blender UI 上の一部操作は次回手動確認として残る。 | GUI registry editing、collection checkbox multi-link、indirect linked library report、Link target type expansion、link integration、日本語 UI 表示切替を同一 manual pass で確認し、失敗があれば再現 Issue に分離する。 |
| Cost | core / adapter / UI / Windows companion の責務分離は維持できている。 | 手動確認で得た再現手順を script 化できる範囲へ移し、次回 release で host 操作の再確認コストを下げる。 |
| Delivery | `v0.1.0` の docs、evidence、release assets は同期済み。 | GitHub release 公開後に `gh release view v0.1.0 --json tagName,isPrerelease,targetCommitish,assets,url` で対象 commit と asset を確認し、次回 release checklist に結果を転記する。 |
| Satisfaction | 利用者向け README、機能一覧、インストール、ユーザーガイド、manual test は揃っている。 | 実ユーザーの Blender UI 操作結果を反映し、初回導入時に迷いやすい `Add File Candidate` / `Preview Link` / `Integrate Link` のスクリーンショットまたは短い手順補足を追加する。 |

## Required Improvements

- 次回手動確認で GUI registry editing と日本語 UI 表示の実機操作を確認し、失敗した場合は再現 Issue に分離する。
- 次回手動確認で collection checkbox multi-link が Outliner にチェック済み collection だけを追加することを確認する。
- 次回手動確認で nested Link を含む source `.blend` を Link し、`sourceLinkedLibraries` と `indirectLinkedLibraries` が report に出ることを確認する。
- 次回手動確認でユーザー報告ファイルの `Link Candidate` を実行し、`ref` だけではなく intended collection / object が Viewport と Outliner に出ることを確認する。
- 次回手動確認で Reference 用画像 / ライト / カメラが `availableObjectDetails` に型付き表示され、明示 object 名でだけ Link されることを確認する。
- 次回手動確認で `Integrate Link` の cancel 無変更とコピー fixture での実統合を確認し、失敗した場合は再現 Issue に分離する。
