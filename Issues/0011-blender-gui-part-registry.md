# Blender GUI で Part Registry を生成・編集できるようにする

- Status: done
- Priority: P2
- Type: feature
- Source: local
- Draft source: codex-cli
- Phase: 04-implementation
- Created: 2026-05-14
- QCDS: Quality, Delivery, Satisfaction

## Context

実務ユーザーが registry JSON を直接編集しなくても、Blender GUI の Linked Parts パネルから現在の linked .blend / linked collection を検出し、Part Registry を生成・編集・保存できるようにする。対象 repo は D:\AI\BlenderAddon\blender-linked-part-version-manager。既存の Validate Registry、Build Sync Preview、Preview Reload、Reload Safe Links、Start Auto Reload を壊さず、.blend 本体への破壊的変更や未コミット .blend 差分の操作は行わない。既存の AGENTS.md ルール、UTF-8/LF、Git 書き込み前確認に従う。

## Acceptance Criteria

- [x] Linked Parts パネルに Scan Current Links と Save Registry が追加され、現在の bpy.data.libraries と linked collection から registry 候補を生成できる。
- [x] GUI 上で partId、partTag、displayName、blendPath、linkedCollection、owner、source、versionRef、updatePolicy を最低限設定でき、owner=unassigned、source.type=local、versionRef=local、updatePolicy=manual が安全な初期値になる。
- [x] 既存の Registry Path を使って registry JSON を保存でき、保存した registry を Validate Registry できる。
- [x] 保存した registry で Build Sync Preview が動作し、既存の Linked Parts 関連操作が退行しない。
- [x] docs、TODO、Issues、tests、QCDS evidence が同期更新され、npm test が通る。

## Notes

- Implemented `BLPVM_RegistryPartItem`, `Scan Current Links`, editable registry list, and `Save Registry` in `addon/blender_linked_part_version_manager/__init__.py`.
- Added core helpers in `core.registry` and linked-library scan in `blender.link`.
- Added unit tests for GUI registry candidate defaults and linked-library scan behavior.

## Codex Sessions

- 2026-05-14T19:23:55.911Z `codex-session-20260514192355-ttu5sf` - All Work Items (VS Code Codex handoff); access=danger-full-access; model=gpt-5.5; intelligence=xhigh; [prompt](c:/Users/gkkjh/AppData/Roaming/Code/User/workspaceStorage/915f2e6b3223925d61deb8335d66d110/sunmax0731.codex-friendly-project-starter/first-prompt-20260514T192355Z.md)
