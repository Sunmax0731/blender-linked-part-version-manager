# Blender 実体パス検証

## 対象

- 既定候補: `D:\SteamLibrary\steamapps\common\Blender\blender.exe`
- 上書き候補: `BLENDER_EXE`
- PATH 候補: `where blender`

`npm test` 内の `scripts/platform-runtime-gate.mjs` は、`BLENDER_EXE`、既定 Steam directory、PATH の順に Blender 実行ファイルを探す。

## 自動検証で実行する項目

| 項目 | 実行条件 | Evidence |
| --- | --- | --- |
| Windows companion 起動 | 常時 | `dist/runtime-gate.json` |
| settings 保存 | 常時 | `dist/runtime-gate.json` |
| installer dry-run | 常時 | `dist/runtime-gate.json` |
| Blender `--version` | Blender executable 検出時 | `dist/runtime-gate.json.blenderHostGate.versionLaunch` |
| Blender CLI smoke | Blender executable 検出時 | `dist/runtime-gate.json.blenderHostGate.cliSmoke` |

Blender CLI smoke は `--background --factory-startup --python-expr` で Blender を起動し、repo の `addon` path を `sys.path` に追加して `blender_linked_part_version_manager` を import する。`.blend` の作成、保存、Link reload は行わない。

## 2026-05-15 結果

- 検出: `D:\SteamLibrary\steamapps\common\Blender\blender.exe`
- 検出元: `default-steam-directory`
- Version: Blender 5.1.1
- CLI smoke: `BLPVM_BLENDER_SMOKE_OK 5.1.1 (0, 1, 1)`
- Gate: `dist/runtime-gate.json` の `blenderHostGate.status` は `cli-smoke-passed`

## 手動確認に残す項目

- integration `.blend` から部位別 `.blend` を Link できること。
- `Build Sync Preview` が実際の Link 状態と registry 差分を表示すること。
- `Reload Safe Links` 後に Viewport 上で対象部位だけが更新されること。
- `local-dirty` と `conflict-risk` で自動更新が止まること。

これらはユーザーの Blender UI と制作 fixture を使う manual host test とし、`Issues/0006-blender-runtime-link-reload-manual.md` と `Issues/0007-alpha-manual-test-evidence.md` で追跡する。
