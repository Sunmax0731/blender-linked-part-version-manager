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
- `samples/representative-suite.json` が JSON として読める。
- 文字化け断片や制御文字の検出で失敗しない。

## Blender 実機確認手順

実装後に実施する。

1. `integration/character_integration.blend` を開く。
2. `parts/hair/main_hair.blend`、`parts/body/base_body.blend`、`parts/face/main_face.blend`、`parts/accessories/glasses.blend` を Link する。
3. アドオンの `Part Registry` パネルで `Create Registry from Current Links` を実行する。
4. Git またはローカル共有フォルダで部位ファイルを更新する。
5. `Sync Preview` で `remote-newer` が表示されることを確認する。
6. `Pull & Reload` を実行し、対象部位だけが更新されることを確認する。
7. Link 先ファイルを一時的に移動し、`broken-link` と復旧候補が表示されることを確認する。
8. local-dirty の部位を用意し、自動更新が停止することを確認する。

## 未実施項目

現時点では実装前のため、Blender 上での Link reload と Git adapter の実機確認は未実施。
