# QCDS 評価

## Current Evaluation

| 観点 | 評価 | 理由 |
| --- | --- | --- |
| Quality | A- | registry validation、sync plan、Git/local adapter、Blender add-on shell、GUI registry editing、Japanese UI localization、Windows runtime gate、Blender CLI smoke、manual reload、Auto Reload target selection、unit test が通っている。 |
| Cost | A- | core、adapter、Blender binding、Windows companion を分離し、MVP の依存を Git / local folder / Node launcher に抑えている。 |
| Delivery | A- | README、AGENTS、SKILL、docs、TODO、Issues、release checklist、docs ZIP、fixture ZIP、release notes、runtime gate evidence、Blender 実体パス検証 evidence、GUI registry editing evidence を同期した。 |
| Satisfaction | A- | Blender UI shell、GUI での registry 生成・編集・保存、日本語表示環境での主要 UI 翻訳、Explorer / Blender file selector からの Link 候補追加、Windows companion、手動テスト fixture で dry-run、手動 reload、保存後の Viewport 反映を確認できる。Auto Reload は保存済みファイル監視として未保存編集の限界を明記した。 |

## Gate

Windows アプリとしての platform runtime gate は local executable / installer dry-run 起動で `passed`。Blender host は `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、CLI smoke、アドオン import、`register()` / `unregister()` smoke が通過済み。ユーザー手元の Blender 5.1.1 で add-on install、fixture 表示、registry validation、sync preview、Preview Reload、Reload Safe Links、保存後の Viewport 反映を確認済み。Auto Reload は保存済み linked `.blend` の mtime 監視として追加した。
GUI registry editing は Python unit test で候補生成初期値と linked library scan を検証済み。Blender 上の `Scan Current Links`、`Save Registry`、`Add File Candidate`、`Preview Link`、`Link Candidate` は次回手動確認項目に追加済み。
Japanese UI localization は Python unit test で主要 translation table coverage を検証し、Blender 5.1.1 CLI で `ja_JP` の `pgettext_iface` が `Scan Current Links` と `Part Registry` を日本語へ解決することを確認済み。

## Required Improvements

- 次回手動確認で GUI registry editing と日本語 UI 表示の実機操作を確認し、失敗した場合は再現 Issue に分離する。
