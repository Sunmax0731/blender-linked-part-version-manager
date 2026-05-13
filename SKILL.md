# SKILL

Use this repository for Blender Link based part-version management work.

## Start Order

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read this `SKILL.md`.
4. Read `docs/requirements.md`, `docs/specification.md`, and `docs/architecture.md`.
5. Check `TODO.md` and the linked file under `Issues/`.
6. Run `npm test` after documentation or scaffold changes.

## Implementation Guidance

- Keep Blender UI operators thin. Put registry validation, sync planning, and conflict classification in testable modules.
- Treat GitHub, Git CLI, local folder sync, and future asset systems as adapters behind the same plan/result contract.
- Never auto-overwrite a linked `.blend` path without a preview report and a rollback note.
- Store part metadata in a small registry first: `partId`, `partTag`, `blendPath`, `linkedCollection`, `owner`, `source`, `versionRef`, `updatePolicy`, and `lastSync`.
- Runtime validation must include a Blender Link reload smoke test before any release.

## Validation

```powershell
npm test
```

Future implementation should add Python unit tests, Git fixture tests, and a Blender runtime gate that opens an integration `.blend`, reloads linked libraries, and writes a JSON result.
