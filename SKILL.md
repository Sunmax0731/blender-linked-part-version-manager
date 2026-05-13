# SKILL

Use this repository for Blender Link based part-version management work.

## Start Order

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read this `SKILL.md`.
4. Read `docs/requirements.md`, `docs/specification.md`, `docs/design.md`, and `docs/architecture.md`.
5. Check `TODO.md` and the linked file under `Issues/`.
6. Run `npm test` after documentation, scaffold, runtime-gate, or release changes.

## Implementation Guidance

- Keep Blender UI operators thin. Put registry validation, sync planning, and conflict classification in testable modules.
- Treat GitHub, Git CLI, local folder sync, and future asset systems as adapters behind the same plan/result contract.
- Never auto-overwrite a linked `.blend` path without a preview report and a rollback note.
- Store part metadata in a small registry first: `partId`, `partTag`, `blendPath`, `linkedCollection`, `owner`, `source`, `versionRef`, `updatePolicy`, and `lastSync`.
- Windows companion must stay outside `.blend` mutation. It may validate registry data, show status, launch installer dry-run, and save settings under `%APPDATA%`.
- Alpha release validation must include the Windows local executable / installer launch gate. Blender Link reload remains a required manual test when Blender CLI is not available in the Codex environment.

## Validation

```powershell
npm test
```

`npm test` runs docs checks, Python unit tests, Windows runtime gate, release packaging, and release artifact checks. Blender runtime validation is tracked in `docs/manual-test.md` and should be executed manually after installing the alpha in Blender.
