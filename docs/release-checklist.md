# リリースチェックリスト

## 開発準備

- [x] IDEAS と正式ドメインの `ideas.md` に No.7 を登録した。
- [x] public GitHub remote を作成し、local `origin` を設定した。
- [x] `README.md`、`AGENTS.md`、`SKILL.md`、`TODO.md` を作成した。
- [x] `docs/requirements.md`、`docs/specification.md`、`docs/design.md`、`docs/architecture.md` を作成した。
- [x] `docs/implementation-plan.md`、`docs/test-plan.md`、`docs/manual-test.md` を作成した。
- [x] created_idea pack を準備した。

## Closed Alpha 前

- [x] Blender アドオン manifest と最小実装を追加した。
- [x] Part Registry validator と dry-run report が動く。
- [x] Git / local adapter の MVP が動く。
- [x] Windows runtime gate が `passed` になっている。
- [x] 指定 Blender 実体パスで CLI smoke と add-on import が `passed` になっている。
- [x] alpha 手動テスト用 `.blend` fixture と fixture ZIP が生成されている。
- [x] Blender runtime gate が手動確認で `passed` になっている。
- [x] Auto Reload が保存済み linked `.blend` 監視として実装されている。
- [x] Blender GUI で Part Registry 候補を scan / edit / save できる。
- [x] Explorer / Blender file selector から `.blend` を Link 候補へ追加し、明示操作で Blender tree に反映できる。
- [x] Link Candidate が source `.blend` の collection / object 候補を inspection し、先頭 `ref` collection へ暗黙 fallback しない。
- [x] 読み込んだ `.blend` の collection 一覧を checkbox 表示し、チェック済み collection を複数 Link できる。
- [x] source `.blend` 内の nested Blender Link を `sourceLinkedLibraries` / `indirectLinkedLibraries` として report できる。
- [x] Link Candidate が Reference 用画像、ライト、カメラを型付き明示候補として report し、floor / helper 系を除外理由付きで扱う。
- [x] Blender 表示言語が日本語の場合の UI 翻訳が実装され、Blender CLI で `pgettext_iface` 解決を確認している。
- [x] linked file 統合の preview、confirmation、report、local 化 helper が実装され、unit test で検証されている。
- [x] `Character.blend` と素体、頭 / 表情、髪、服、アクセサリの参照関係をユーザー向け関係表として整理している。
- [x] `docs/qcds-evaluation.md` の全観点が `A-` 以上になっている。
- [x] `docs/installation-guide.md` と `docs/user-guide.md` を追加した。
- [x] GitHub prerelease と docs ZIP を作成した。
- [x] `Issues/0019-issue.md` で現行バージョンの release verification を完了した。

## Release Evidence

初回 release 前に次を作成する。

- `dist/blender-linked-part-version-manager.zip`
- `dist/blender-linked-part-version-manager-docs.zip`
- `dist/blender-linked-part-version-manager-fixtures.zip`
- `dist/test-summary.json`
- `dist/runtime-gate.json`
- `docs/release-evidence.json`
