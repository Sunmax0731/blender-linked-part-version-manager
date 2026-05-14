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
- [ ] Blender runtime gate が手動確認で `passed` になっている。
- [x] `docs/qcds-evaluation.md` の全観点が `A-` 以上になっている。
- [x] `docs/installation-guide.md` と `docs/user-guide.md` を追加した。
- [x] GitHub prerelease と docs ZIP を作成した。

## Release Evidence

初回 release 前に次を作成する。

- `dist/blender-linked-part-version-manager.zip`
- `dist/blender-linked-part-version-manager-docs.zip`
- `dist/test-summary.json`
- `dist/runtime-gate.json`
- `docs/release-evidence.json`
