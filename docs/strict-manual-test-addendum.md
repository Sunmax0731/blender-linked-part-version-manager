# Strict Manual Test Addendum

この alpha release は Codex 環境で Windows platform runtime gate を通しているが、Blender CLI が PATH 上にないため Blender 実機 Link reload は未実施である。

## リリース後に必須の確認

- Blender 4.2 以降で add-on ZIP を install できる。
- `Linked Parts` パネルが表示される。
- `samples/representative-suite.json` 相当の registry を読み込める。
- integration `.blend` から部位別 `.blend` を Link し、`Build Sync Preview` が更新候補と blocked 状態を表示する。
- `local-dirty` と `conflict-risk` で自動更新が止まる。
- safe な linked library の reload が成功し、Viewport で対象部位の更新を確認できる。

## 判定

全項目が通ったら次リリースで Blender host runtime gate を `passed` に更新する。失敗した場合は `Issues/` に再現手順、Blender version、registry、`dist/blender-dry-run-report.json` を記録する。
