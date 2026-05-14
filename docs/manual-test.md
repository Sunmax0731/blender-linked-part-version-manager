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

- version が `0.1.0` として表示される。
- registry validation が `ok: true` を返す。
- `%APPDATA%\BlenderLinkedPartVersionManager\settings.json` が作成され、registry path が保存される。
- installer dry-run が `ok: true` を返し、実ファイルコピーは行わない。

## Blender 実機確認手順

alpha release 後に手作業で実施する。

1. release asset `blender-linked-part-version-manager-fixtures.zip` を展開する。repo から実施する場合は `D:\AI\BlenderAddon\blender-linked-part-version-manager` を fixture root として使う。
2. `<fixture-root>\integration\character_integration.blend` を Blender で開く。
3. `Linked Parts` パネルが表示されることを確認する。
4. add-on preferences の `Registry Path` に `<fixture-root>\samples\representative-suite.json` を指定する。
5. `Validate Registry` を実行し、registry が OK になることを確認する。
6. `Build Sync Preview` を実行し、summary が表示され、`remote-newer`、`local-dirty`、`broken-link` の代表状態が dry-run report に記録されることを確認する。
7. `Preview Reload` を実行し、対象 library が dry-run reloaded として表示されることを確認する。
8. 実 reload を確認する場合は、`parts/hair/main_hair.blend` を別ウィンドウで開き、Hair marker を少し移動して保存する。その後 `character_integration.blend` に戻り、`Reload Safe Links` を実行して Viewport の Hair が更新されることを確認する。
9. Link 先ファイルを一時的に移動する場合は、コピーで退避してから `broken-link` 表示を確認し、必ず元の場所へ戻す。
10. local-dirty / conflict-risk 相当は `representative-suite.json` の `expectedStatus` で dry-run 表示され、自動更新対象から外れることを確認する。

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

## 未実施項目

Blender 上での Link reload 実機確認は未実施。alpha release 後、ユーザーまたはテスト協力者の Blender 4.2 以降で本手順を実施し、結果を次リリースの `docs/release-evidence.json` に反映する。
