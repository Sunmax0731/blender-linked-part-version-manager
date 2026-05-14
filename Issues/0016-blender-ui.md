# Blender表示言語に連動した日本語UI対応

- Status: done
- Priority: P2
- Type: feature
- Source: local
- Draft source: codex-cli
- Phase: 04-implementation
- Created: 2026-05-14
- QCDS: Quality, Satisfaction

## Context

Blender上の表示言語を日本語に設定した利用者向けに、アドオンの表示文言も日本語で表示されるようにする。Blender本体の言語設定に追従し、英語など日本語以外の環境では既存表示または適切なフォールバックを維持する。

## Acceptance Criteria

- [x] Blenderの表示言語が日本語の場合、アドオンのパネル、メニュー、ボタン、オペレーター名、主要メッセージが日本語で表示される。
- [x] Blenderの表示言語が日本語以外の場合、既存の英語表示または既定表示が壊れない。
- [x] Blenderの標準的な翻訳仕組みに沿って実装され、表示言語の判定や文言管理が保守しやすい形になっている。
- [x] 日本語表示の手動確認条件が明確で、主要UIで未翻訳または不自然な表示が残っていないことを確認できる。

## Notes

- `bpy.app.translations.register(__name__, BLPVM_TRANSLATIONS)` で `ja_JP` UI 翻訳を登録し、`unregister()` で解除する。
- `pgettext_iface` helper を通して text override と主要 report / status message を翻訳する。
- 自動テストで翻訳テーブルの主要 UI coverage を確認した。
- Blender 5.1.1 CLI で `preferences.view.language='ja_JP'`、`use_translate_interface=True` を設定し、`Scan Current Links` と `Part Registry` が日本語へ解決されることを確認した。

## Evidence

- Code: `addon/blender_linked_part_version_manager/__init__.py`
- Tests: `tests/test_registry_plan.py`
- Runtime: `D:\SteamLibrary\steamapps\common\Blender\blender.exe --background --factory-startup --python-expr ...`
- Docs: `docs/features.md`, `docs/manual-test.md`, `docs/test-plan.md`, `docs/qcds-evaluation.md`

## Codex Sessions

- 2026-05-14T20:27:26.666Z `codex-session-20260514202726-0yj6dx` - All Work Items (VS Code Codex handoff); access=danger-full-access; model=gpt-5.5; intelligence=xhigh; [prompt](c:/Users/gkkjh/AppData/Roaming/Code/User/workspaceStorage/915f2e6b3223925d61deb8335d66d110/sunmax0731.codex-friendly-project-starter/first-prompt-20260514T202726Z.md)
