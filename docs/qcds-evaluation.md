# QCDS 評価

## Current Evaluation

| 観点 | 評価 | 理由 |
| --- | --- | --- |
| Quality | A- | registry validation、sync plan、Git/local adapter、Blender add-on shell、Windows runtime gate、Blender CLI smoke、unit test が通っている。Blender 実機 reload は alpha 後の手動確認として残る。 |
| Cost | A- | core、adapter、Blender binding、Windows companion を分離し、MVP の依存を Git / local folder / Node launcher に抑えている。 |
| Delivery | A- | README、AGENTS、SKILL、docs、TODO、Issues、release checklist、docs ZIP、release notes、runtime gate evidence、Blender 実体パス検証 evidence を同期した。 |
| Satisfaction | A- | Blender UI shell と Windows companion で dry-run と設定保存を確認できる。実制作 `.blend` での Link reload 体験は手動確認待ち。 |

## Gate

Windows アプリとしての platform runtime gate は local executable / installer dry-run 起動で `passed`。Blender host は `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 を検出し、CLI smoke とアドオン import が `cli-smoke-passed`。統合 `.blend` と部位別 `.blend` の Link reload は `blocked` の manual host test として残る。

## Required Improvements

- alpha release 後に Blender 4.2 以降で Link reload 手動確認を行い、次リリースで `docs/release-evidence.json` と QCDS を `passed` または再現 Issue に更新する。
