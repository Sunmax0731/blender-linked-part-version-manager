# QCDS 評価

## Current Evaluation

| 観点 | 評価 | 理由 |
| --- | --- | --- |
| Quality | A- | registry validation、sync plan、Git/local adapter、Blender add-on shell、Windows runtime gate、Blender CLI smoke、manual reload、Auto Reload target selection、unit test が通っている。 |
| Cost | A- | core、adapter、Blender binding、Windows companion を分離し、MVP の依存を Git / local folder / Node launcher に抑えている。 |
| Delivery | A- | README、AGENTS、SKILL、docs、TODO、Issues、release checklist、docs ZIP、fixture ZIP、release notes、runtime gate evidence、Blender 実体パス検証 evidence を同期した。 |
| Satisfaction | A- | Blender UI shell、Windows companion、手動テスト fixture で dry-run、手動 reload、保存後の Viewport 反映を確認できる。Auto Reload は保存済みファイル監視として未保存編集の限界を明記した。 |

## Gate

Windows アプリとしての platform runtime gate は local executable / installer dry-run 起動で `passed`。Blender host は `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、CLI smoke とアドオン import が `cli-smoke-passed`。ユーザー手元の Blender 5.1.1 で add-on install、fixture 表示、registry validation、sync preview、Preview Reload、Reload Safe Links、保存後の Viewport 反映を確認済み。Auto Reload は保存済み linked `.blend` の mtime 監視として追加した。

## Required Improvements

- alpha release 後に Blender 4.2 以降で Link reload 手動確認を行い、次リリースで `docs/release-evidence.json` と QCDS を `passed` または再現 Issue に更新する。
