# TODO

This file is the phase TODO source for local Work Items. Keep a `phase=...` token on every TODO line so completed and open items do not fall back to `00-inbox`.

## 00-inbox TODO

No current TODO. New uncategorized work should be moved into one of the phase sections below before it is started.

## 01-requirements TODO

- [x] Create repo at `D:\AI\BlenderAddon\blender-linked-part-version-manager`. [phase=01-requirements]
- [x] Create public GitHub remote and set local `origin`. [phase=01-requirements]
- [x] Add repo-local `README.md`, `AGENTS.md`, and `SKILL.md`. [phase=01-requirements]
- [x] Register idea No.7 in `D:\AI\IDEAS\BlenderAddon\ideas.md` and `D:\AI\BlenderAddon\ideas.md`. [phase=01-requirements]
- [x] [P1] 部位別 Link 共同制作の要件を確定する [Issue](Issues/0001-link-part-workspace-requirements.md) / [GitHub #1](https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/1) [phase=01-requirements] [QCDS:Quality,Satisfaction]

## 02-specification TODO

- [x] [P1] レジストリ、同期計画、衝突状態の仕様を確定する [Issue](Issues/0002-registry-sync-specification.md) / [GitHub #2](https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/2) [phase=02-specification] [QCDS:Quality,Cost]

## 03-design TODO

- [x] [P2] Blender UI と更新前プレビューの導線を固める [Issue](Issues/0003-blender-link-refresh-design.md) / [GitHub #3](https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/3) [phase=03-design] [QCDS:Satisfaction]

## 04-implementation TODO

- [x] 実装開始時に `codex/linked-part-mvp` ブランチを作成する。 [phase=04-implementation]
- [x] 部位レジストリ validator と dry-run report を実装する。 [phase=04-implementation]
- [x] Git / local folder sync adapter の最小 contract を実装する。 [phase=04-implementation]
- [x] Blender Link reload operator の MVP を実装する。 [phase=04-implementation]
- [x] Windows companion launcher と設定保存 gate を実装する。 [Issue](Issues/0004-alpha-mvp-release.md) / [GitHub #4](https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/4) [phase=04-implementation] [QCDS:Quality,Satisfaction]

## 05-test TODO

- [x] 代表シナリオ JSON の自動検証を追加する。 [phase=05-test]
- [x] Windows local executable / installer dry-run の runtime gate を通す。 [phase=05-test]
- [x] [P3] Blender runtime gate で統合 `.blend` と部位別 `.blend` の Link 更新を確認する。Alpha release 後の手動確認として実施する。 [Issue](Issues/0006-blender-runtime-link-reload-manual.md) [phase=05-test]

## 06-release TODO

- [x] インストール手順、ユーザーガイド、QCDS、release checklist、docs ZIP を更新する。 [phase=06-release]
- [x] alpha release の prerelease evidence を準備する。 [Issue](Issues/0004-alpha-mvp-release.md) / [GitHub #4](https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/4) [phase=06-release]
- [x] [P3] ユーザー手元の Blender で alpha manual test を実行し、結果を次リリースの evidence に反映する。 [Issue](Issues/0007-alpha-manual-test-evidence.md) [phase=06-release]

## Work Items
- [x] [P2] [Phase:05-test] Blender実体パスを使った検証対応 [Issue](Issues/0005-blender.md) [QCDS:Quality,Delivery]
- [x] [P2] [Phase:05-test] 手動テスト用 `.blend` fixture を alpha release に同梱する [Issue](Issues/0008-manual-test-fixtures.md) [QCDS:Quality,Delivery,Satisfaction]
- [x] [P2] [Phase:05-test] Manual test で検出した reload 対象 path 不一致を修正する [Issue](Issues/0009-reload-target-path-fix.md) [QCDS:Quality,Satisfaction]
- [x] [P2] [Phase:04-implementation] 保存済み linked `.blend` の Auto Reload を追加する [Issue](Issues/0010-auto-reload-saved-links.md) [QCDS:Quality,Satisfaction]
- [x] [P2] [Phase:04-implementation] Blender GUI で Part Registry を生成・編集できるようにする [Issue](Issues/0011-blender-gui-part-registry.md) [QCDS:Quality,Delivery,Satisfaction]
- [x] [P2] [Phase:06-release] Blender GUI で Part Registry を生成・編集できるようにする [Issue](Issues/0012-blender-gui-part-registry.md) [QCDS:Quality,Delivery,Satisfaction]
- [x] [P2] [Phase:06-release] MVP後の実装とリリース準備 [Issue](Issues/0013-mvp.md) [QCDS:Quality,Cost,Delivery,Satisfaction]
- [x] [P2] [Phase:06-release] MVP後の実装とリリース準備 [Issue](Issues/0014-mvp.md) [QCDS:Quality,Cost,Delivery,Satisfaction]
- [x] [P2] [Phase:06-release] GitHub トップ README を利用者向けに整理し、機能一覧ドキュメントを追加する [Issue](Issues/0015-user-facing-readme-features.md) [QCDS:Quality,Satisfaction]
- [x] [P2] [Phase:04-implementation] Blender表示言語に連動した日本語UI対応 [Issue](Issues/0016-blender-ui.md) [QCDS:Quality,Satisfaction]
- [x] [P2] [Phase:05-test] リンクファイル統合機能を追加する [Issue](Issues/0017-issue.md) [QCDS:Quality,Cost,Satisfaction]
- [x] [P1] [Phase:04-implementation] Link Candidate が `ref` collection だけをリンクする不具合を修正する [Issue](Issues/0018-link-candidate-ref-only.md) [QCDS:Quality,Delivery,Satisfaction]
