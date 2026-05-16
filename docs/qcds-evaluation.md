# QCDS 評価

## Current Evaluation

| 観点 | 評価 | 理由 |
| --- | --- | --- |
| Quality | A- | registry validation、sync plan、Git/local adapter、Blender add-on shell、GUI registry editing、Character.blend 関係表、Link candidate collection/object selection、Japanese UI localization、Windows runtime gate、Blender CLI smoke、manual reload、Auto Reload target selection、linked file integration helper、unit test が通っている。 |
| Cost | A- | core、adapter、Blender binding、Windows companion を分離し、MVP の依存を Git / local folder / Node launcher に抑えている。Character.blend 関係表では素体依存を hidden transitive reload として実装せず、docs / registry / report の確認事項として扱う。 |
| Delivery | A- | README、AGENTS、SKILL、docs、TODO、Issues、release checklist、docs ZIP、fixture ZIP、release notes、runtime gate evidence、Blender 実体パス検証 evidence、GUI registry editing evidence、Character.blend 関係表を同期した。 |
| Satisfaction | A- | Blender UI shell、GUI での registry 生成・編集・保存、Character.blend と素体 / 頭・表情 / 髪 / 服 / アクセのユースケース整理、日本語表示環境での主要 UI 翻訳、Explorer / Blender file selector からの Link 候補追加、`ref` 誤リンクを避ける候補 inspection、linked file 統合の preview / confirmation / report、Windows companion、手動テスト fixture で dry-run、手動 reload、保存後の Viewport 反映を確認できる。Auto Reload は保存済みファイル監視として未保存編集の限界を明記した。 |

## Gate

Windows アプリとしての platform runtime gate は local executable / installer dry-run 起動で `passed`。Blender host は `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、CLI smoke、アドオン import、`register()` / `unregister()` smoke が通過済み。ユーザー手元の Blender 5.1.1 で add-on install、fixture 表示、registry validation、sync preview、Preview Reload、Reload Safe Links、保存後の Viewport 反映を確認済み。Auto Reload は保存済み linked `.blend` の mtime 監視として追加した。
GUI registry editing は Python unit test で候補生成初期値と linked library scan を検証済み。Blender 上の `Scan Current Links`、`Save Registry`、`Add File Candidate`、`Preview Link`、`Link Candidate` は次回手動確認項目に追加済み。
Link candidate collection/object selection は Python unit test で production collection / object selection、missing collection 時の先頭 `ref` fallback 禁止を検証済み。Blender 5.1.1 CLI で `D:\Work\Blender\Shirayukikokoro\blender\base_blender\base.blend` の available collection / object を inspection し、修正後の dry-run が `ref` ではなく `1_costume` を recommended target にすることを確認済み。
Japanese UI localization は Python unit test で主要 translation table coverage を検証し、Blender 5.1.1 CLI で `ja_JP` の `pgettext_iface` が `Scan Current Links` と `Part Registry` を日本語へ解決することを確認済み。
Link integration は Python unit test で dry-run が local 化しないこと、確認あり実行側の helper が選択 target の linked datablock だけを local 化することを検証済み。Blender UI 上の confirmation cancel / 実統合は次回手動確認項目に追加済み。
Character.blend 関係表は `docs/character-blend-relationship.md` に追加し、素体が頭 / 表情、髪、服、アクセサリから参照される関係、`Character.blend` 側の統合表示、Part Registry / Link 管理 / 検証レポートの責務分離を README、features、user guide、design、architecture、manual test へ接続済み。

## Required Improvements

- 次回手動確認で GUI registry editing と日本語 UI 表示の実機操作を確認し、失敗した場合は再現 Issue に分離する。
- 次回手動確認でユーザー報告ファイルの `Link Candidate` を実行し、`ref` だけではなく intended collection / object が Viewport と Outliner に出ることを確認する。
- 次回手動確認で `Integrate Link` の cancel 無変更とコピー fixture での実統合を確認し、失敗した場合は再現 Issue に分離する。
