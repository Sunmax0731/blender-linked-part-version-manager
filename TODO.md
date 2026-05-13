# TODO

This file is the phase TODO source for local Work Items. Keep a `phase=...` token on every TODO line so completed and open items do not fall back to `00-inbox`.

## 00-inbox TODO

No current TODO. New uncategorized work should be moved into one of the phase sections below before it is started.

## 01-requirements TODO

- [x] Create repo at `D:\AI\BlenderAddon\blender-linked-part-version-manager`. [phase=01-requirements]
- [x] Add repo-local `README.md`, `AGENTS.md`, and `SKILL.md`. [phase=01-requirements]
- [x] Register idea No.7 in `D:\AI\IDEAS\BlenderAddon\ideas.md` and `D:\AI\BlenderAddon\ideas.md`. [phase=01-requirements]
- [ ] [P1] 部位別 Link 共同制作の要件を確定する [Issue](Issues/0001-link-part-workspace-requirements.md) [phase=01-requirements] [QCDS:Quality,Satisfaction]

## 02-specification TODO

- [ ] [P1] レジストリ、同期計画、衝突状態の仕様を確定する [Issue](Issues/0002-registry-sync-specification.md) [phase=02-specification] [QCDS:Quality,Cost]

## 03-design TODO

- [ ] [P2] Blender UI と更新前プレビューの導線を固める [Issue](Issues/0003-blender-link-refresh-design.md) [phase=03-design] [QCDS:Satisfaction]

## 04-implementation TODO

- [ ] 実装開始時に `codex/linked-part-mvp` ブランチを作成する。 [phase=04-implementation]
- [ ] 部位レジストリ validator と dry-run report を実装する。 [phase=04-implementation]
- [ ] GitHub / local folder sync adapter の最小 contract を実装する。 [phase=04-implementation]
- [ ] Blender Link reload operator の MVP を実装する。 [phase=04-implementation]

## 05-test TODO

- [ ] 代表シナリオ JSON の自動検証を追加する。 [phase=05-test]
- [ ] Blender runtime gate で統合 `.blend` と部位別 `.blend` の Link 更新を確認する。 [phase=05-test]

## 06-release TODO

- [ ] インストール手順、ユーザーガイド、QCDS、release checklist、docs ZIP を更新する。 [phase=06-release]
- [ ] closed alpha release の prerelease evidence を準備する。 [phase=06-release]
