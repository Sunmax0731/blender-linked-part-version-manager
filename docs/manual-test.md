# 手動テスト

## 前提

- Windows 10/11
- Blender 4.2 以降
- Git CLI
- Node.js 20 以降
- `blender-linked-part-version-manager-fixtures.zip` または repo 内の `integration/` と `parts/`

## Codex 側での確認

```powershell
cd D:\AI\BlenderAddon\blender-linked-part-version-manager
npm test
```

期待結果:

- `Docs completeness check passed.` が表示される。
- Python unit test が通る。
- `Platform runtime gate passed.` が表示される。
- `dist/runtime-gate.json`、`dist/test-summary.json`、`dist/blender-linked-part-version-manager.zip`、`dist/blender-linked-part-version-manager-docs.zip` が生成される。
- `D:\SteamLibrary\steamapps\common\Blender\blender.exe` または `BLENDER_EXE` が存在する環境では、`dist/runtime-gate.json` の `blenderHostGate.status` が `cli-smoke-passed` になり、Blender version と `BLPVM_BLENDER_SMOKE_OK` が記録される。

## Windows companion 確認

```powershell
windows\blpvm-companion.cmd --version
windows\blpvm-companion.cmd validate-registry --registry samples\representative-suite.json
windows\blpvm-companion.cmd status --registry samples\representative-suite.json
windows\blpvm-companion.cmd init-settings --registry samples\representative-suite.json
windows\install-alpha.cmd --dry-run
```

期待結果:

- version が `0.1.2` として表示される。
- registry validation が `ok: true` を返す。
- `%APPDATA%\BlenderLinkedPartVersionManager\settings.json` が作成され、registry path が保存される。
- installer dry-run が `ok: true` を返し、実ファイルコピーは行わない。

## Blender 実機確認手順

alpha release 後に手作業で実施する。

1. release asset `blender-linked-part-version-manager-fixtures.zip` を展開する。repo から実施する場合は `D:\AI\BlenderAddon\blender-linked-part-version-manager` を fixture root として使う。
2. `<fixture-root>\integration\character_integration.blend` を Blender で開く。
3. `Linked Parts` パネルが表示されることを確認する。
4. add-on preferences の `Registry Path` に `<fixture-root>\samples\representative-suite.json` を指定する。
5. `docs/character-blend-relationship.md` の関係表と fixture path が対応していることを確認する。`character_integration.blend` は統合表示用、`base_body.blend` は共通素体、`main_face.blend` は頭 / 表情、`main_hair.blend` は髪、`glasses.blend` はアクセサリとして扱う。
6. `Validate Registry` を実行し、registry が OK になることを確認する。
7. `Scan Current Links` を実行し、現在の linked library / collection から editable な registry 候補が表示されることを確認する。
8. 候補の `owner`、`source.type`、`versionRef`、`updatePolicy` が安全な初期値であることを確認し、必要に応じて GUI 上で編集する。
9. `Save Registry` を実行し、`Registry Path` の JSON が保存されることを確認する。その後 `Validate Registry` を再実行し、保存済み registry が OK になることを確認する。
10. `Add File Candidate` で Explorer / Blender file selector から `.blend` を選び、候補として追加できることを確認する。preview JSON に available collection / object、recommended target、warnings が出ることを確認する。`Preview Link` は dry-run のみで、`Link Candidate` は明示操作として現在の Blender tree へ Link する。どちらも自動保存しない。
11. source `.blend` に `ref` collection と production collection / object が混在する場合、`Preview Link` が先頭 `ref` ではなく production collection または production object を target にすることを確認する。明示的に存在しない `linkedCollection` を入力した場合は、Link せず候補一覧と失敗理由が表示されることを確認する。
12. `Build Sync Preview` を実行し、summary が表示され、`remote-newer`、`local-dirty`、`broken-link` の代表状態が dry-run report に記録されることを確認する。
13. `Preview Reload` を実行し、Hair の library だけが dry-run `reloaded`、他の library が `skipped` として表示されることを確認する。
14. 実 reload を確認する場合は、`parts/hair/main_hair.blend` を別ウィンドウで開き、Hair marker を少し移動して保存する。その後 `character_integration.blend` に戻り、`Reload Safe Links` を実行して Viewport の Hair が更新されることを確認する。
15. `Preview Integrate` を実行し、選択中の registry 候補に対応する target linked file、output file、datablockCount が preview / report に出ることを確認する。
16. `Integrate Link` を実行して確認ダイアログを表示し、`Cancel` した場合に `.blend` 本体、Link 状態、Part Registry、`Report Path` の内容が変わらないことを確認する。
17. 実統合を確認する場合は fixture をコピーしてから `Integrate Link` を確認あり実行し、linked datablock が local data になり、`Report Path` に `operation=integrate-linked-library`、result、warning が保存されることを確認する。現在の `.blend` は自動保存されないため、確認後に保存するか破棄する。
18. Auto Reload を確認する場合は、`Start Auto Reload` を実行してから `parts/hair/main_hair.blend` を別ウィンドウで変更して保存する。`Auto Reload Interval` の秒数以内に integration 側の Hair が更新されることを確認する。
19. `Stop Auto Reload` で監視を停止する。
20. Blender の Preferences > Interface > Translation で Language を `Japanese (日本語)` に変更し、Interface 翻訳を有効にする。
21. `Linked Parts` タブ、`Part Registry` パネル、`Scan Current Links`、`Save Registry`、`Preview Link`、`Reload Safe Links`、`Preview Integrate`、`Integrate Link`、Auto Reload status、operator report が日本語で表示されることを確認する。
22. Language を English または既定に戻し、英語表示が壊れていないことを確認する。
23. Link 先ファイルを一時的に移動する場合は、コピーで退避してから `broken-link` 表示を確認し、必ず元の場所へ戻す。
24. local-dirty / conflict-risk 相当は `representative-suite.json` の `expectedStatus` で dry-run 表示され、自動更新対象から外れることを確認する。

期待される fixture path:

```text
integration/character_integration.blend
parts/hair/main_hair.blend
parts/body/base_body.blend
parts/face/main_face.blend
parts/accessories/glasses.blend
samples/representative-suite.json
```

## Blender 実体パス smoke

2026-05-15 時点で `D:\SteamLibrary\steamapps\common\Blender\blender.exe` を検出し、Blender 5.1.1 の CLI smoke とアドオン import は通過済み。

## Troubleshooting

- `Preview Reload` / `Reload Safe Links` が `failed: []` でも `reloaded: []` かつ全件 `skipped` になる場合は、古い add-on ZIP が入っている可能性がある。GitHub Release から更新後の `blender-linked-part-version-manager.zip` を再取得し、Blender の Add-ons で一度 remove してから install し直す。
- `Reload Safe Links` で `dryRun: false`、Hair が `reloaded`、Body / Accessories / Face が `skipped` なら reload 対象解決は成功。Viewport の見た目の変化まで確認するには、先に `parts/hair/main_hair.blend` を変更して保存する。
- Auto Reload も保存済みファイルだけを監視する。別 Blender ウィンドウの未保存編集は `.blend` に書き出されていないため、Blender Link reload では反映できない。
- `Integrate Link` は linked datablock を local data に変えるため、確認あり実行はコピーした fixture で行う。cancel した場合は operator が実行されず、`.blend` と registry は変更されない。
- `Report Path` は fixture root 直下の `blender-dry-run-report.json` など、書き込み可能で見つけやすい場所にする。
- `Link Candidate` で `ref` だけが Link される場合は、`Preview Link` の `availableCollections`、`availableObjects`、`recommendedCollection`、`recommendedObjects` を確認する。修正後は指定 collection が見つからないと先頭 `ref` へ fallback せず、production collection または production object を report する。
- 日本語表示が切り替わらない場合は Blender Preferences の Interface 翻訳が有効か確認する。アドオン側は `ja_JP` translation table を登録しているため、英語環境では英語 msgid がそのまま表示される。

## 未実施項目

Blender 上での Link reload 実機確認はユーザー手元の Blender 5.1.1 で通過済み。今回追加した GUI registry editing、Explorer / Blender file selector からの Link 候補追加、link integration、日本語 UI 表示は、次回手動確認で `Scan Current Links`、`Save Registry`、`Add File Candidate`、`Preview Link`、`Link Candidate`、`Preview Integrate`、`Integrate Link`、日本語表示切替の順に確認する。
