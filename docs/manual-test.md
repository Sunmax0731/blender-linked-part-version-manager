# 手動テスト

## 前提

- Windows 10/11
- Blender 4.2 以降
- Git CLI
- Node.js 20 以降
- テスト用 Git repository またはローカル共有フォルダ

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

1. `integration/character_integration.blend` を開く。
2. `parts/hair/main_hair.blend`、`parts/body/base_body.blend`、`parts/face/main_face.blend`、`parts/accessories/glasses.blend` を Link する。
3. アドオンの `Part Registry` パネルで `Create Registry from Current Links` を実行する。
4. Git またはローカル共有フォルダで部位ファイルを更新する。
5. `Sync Preview` で `remote-newer` が表示されることを確認する。
6. `Pull & Reload` を実行し、対象部位だけが更新されることを確認する。
7. Link 先ファイルを一時的に移動し、`broken-link` と復旧候補が表示されることを確認する。
8. local-dirty の部位を用意し、自動更新が停止することを確認する。

## Blender 実体パス smoke

2026-05-15 時点で `D:\SteamLibrary\steamapps\common\Blender\blender.exe` を検出し、Blender 5.1.1 の CLI smoke とアドオン import は通過済み。

## 未実施項目

Blender 上での Link reload 実機確認は未実施。alpha release 後、ユーザー手元の Blender 4.2 以降で本手順を実施し、結果を次リリースの `docs/release-evidence.json` に反映する。
