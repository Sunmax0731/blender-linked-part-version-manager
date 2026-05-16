# SKILL

Use this repository for Blender Link based part-version management work.

## Start Order

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read this `SKILL.md`.
4. Read `docs/requirements.md`, `docs/specification.md`, `docs/design.md`, `docs/architecture.md`, and `docs/character-blend-relationship.md`.
5. For public-facing documentation changes, keep `README.md`, `docs/features.md`, `docs/installation-guide.md`, and `docs/user-guide.md` consistent.
6. Check `TODO.md` and the linked file under `Issues/`.
7. Run `npm test` after documentation, scaffold, runtime-gate, or release changes.

## Implementation Guidance

- Keep Blender UI operators thin. Put registry validation, sync planning, and conflict classification in testable modules.
- Treat GitHub, Git CLI, local folder sync, and future asset systems as adapters behind the same plan/result contract.
- Never auto-overwrite a linked `.blend` path without a preview report and a rollback note.
- Treat linked file integration as a destructive Blender-session operation: preview first, require a confirmation dialog that names target files and output file, write a report, and never auto-save the current `.blend`.
- Store part metadata in a small registry first: `partId`, `partTag`, `blendPath`, `linkedCollection`, `owner`, `source`, `versionRef`, `updatePolicy`, and `lastSync`.
- GUI-created registry candidates must default to `owner=unassigned`, `source.type=local`, `versionRef=local`, and `updatePolicy=manual`; file-selector candidates may be linked only through an explicit Blender add-on operation and must not auto-save the current `.blend`.
- File-selector link candidates must inspect linkable collection / object names before linking. Do not silently fall back to the first collection; avoid reference-only collections such as `ref`, and report available candidates when the requested collection is missing.
- Blender UI strings must keep the English default labels stable and add `ja_JP` entries in `BLPVM_TRANSLATIONS`; dynamic reports should go through the local `pgettext_iface` helper.
- Windows companion must stay outside `.blend` mutation. It may validate registry data, show status, launch installer dry-run, and save settings under `%APPDATA%`.
- Character production topology is documented in `docs/character-blend-relationship.md`; keep `Character.blend` integration links, base-body references, Part Registry rows, and validation reports separate instead of adding hidden transitive Link behavior.
- Alpha release validation must include the Windows local executable / installer launch gate and, when available, a non-mutating Blender CLI smoke from `BLENDER_EXE` or `D:\SteamLibrary\steamapps\common\Blender\blender.exe`. Blender Link reload remains a required manual test until an integration `.blend` and part `.blend` are confirmed by the user.

## Validation

```powershell
npm test
```

`npm test` runs docs checks, Python unit tests, Windows runtime gate, Blender CLI smoke when a Blender executable is detected, release packaging, and release artifact checks. Blender Link reload validation is tracked in `docs/manual-test.md` and should be executed manually after installing the alpha in Blender.
