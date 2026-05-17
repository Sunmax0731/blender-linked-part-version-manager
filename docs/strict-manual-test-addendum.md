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
- 読み込んだ `.blend` の collection 一覧がチェックボックス表示され、チェック済み collection だけが `Preview Link` / `Link Candidate` で複数 Link される。
- source `.blend` 内に nested Blender Link がある場合、`Preview Link` に `sourceLinkedLibraries`、実行結果に `linkedLibraries` / `indirectLinkedLibraries` が出る。
- source `.blend` に `ref` collection と production collection / object が混在する場合、`Preview Link` が先頭 `ref` ではなく intended collection / object を recommended target にし、存在しない明示 collection は失敗として候補一覧を表示する。
- Reference 用画像、ライト、カメラがある source `.blend` では `availableObjectDetails` に object type / category / selection が表示され、明示 object 名でだけ Link される。floor helper は除外理由付きで失敗する。
- `Preview Integrate` が対象 linked file と output file を表示し、`Integrate Link` の cancel で `.blend`、Link 状態、Part Registry が変わらない。
- コピーした fixture で `Integrate Link` を確認あり実行し、linked datablock が local data になり、report に結果と warning が残る。
- Blender の表示言語を日本語にしたとき、`Linked Parts` タブ、`Part Registry` パネル、主要ボタン、Auto Reload status、operator report が日本語表示になる。

## 判定

Link reload と Viewport 反映は通過済み。GUI registry editing、collection checkbox multi-link、indirect linked library report、Link Candidate target selection、Link target type expansion、link integration、日本語 UI 表示の実機確認で失敗した場合は `Issues/` に再現手順、Blender version、registry、`dist/blender-dry-run-report.json` を記録する。
