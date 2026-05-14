# Strict Manual Test Addendum

この alpha release は Codex 環境で Windows platform runtime gate を通している。2026-05-15 時点で `D:\SteamLibrary\steamapps\common\Blender\blender.exe` から Blender 5.1.1 の CLI smoke とアドオン import も通過済みである。ユーザー手元の Blender 5.1.1 では Link reload と Viewport 反映まで確認済みである。

## リリース後に必須の確認

- Blender 4.2 以降で add-on ZIP を install できる。
- `Linked Parts` パネルが表示される。
- `blender-linked-part-version-manager-fixtures.zip` を展開し、`samples/representative-suite.json` を読み込める。
- `integration/character_integration.blend` が部位別 `.blend` を Link しており、`Build Sync Preview` が更新候補と blocked 状態を表示する。
- `local-dirty` と `conflict-risk` で自動更新が止まる。
- safe な linked library の reload preview で Hair part が `reloaded` に出る。
- 実 reload が成功し、Viewport で対象部位の更新を確認できる。
- `Start Auto Reload` 後、保存済み Hair `.blend` の変更が interval 内に integration Viewport へ反映される。
- 未保存の別 Blender 編集は Auto Reload では反映されないことを確認する。
- `Scan Current Links`、`Save Registry`、`Add File Candidate`、`Preview Link`、`Link Candidate` が GUI registry editing の想定通りに動く。
- Blender の表示言語を日本語にしたとき、`Linked Parts` タブ、`Part Registry` パネル、主要ボタン、Auto Reload status、operator report が日本語表示になる。

## 判定

Link reload と Viewport 反映は通過済み。GUI registry editing または日本語 UI 表示の実機確認で失敗した場合は `Issues/` に再現手順、Blender version、registry、`dist/blender-dry-run-report.json` を記録する。
