# Windows Companion

`blpvm-companion.cmd` is the closed-alpha Windows launcher for registry validation, status preview, and settings initialization outside Blender.

```powershell
windows\blpvm-companion.cmd --version
windows\blpvm-companion.cmd validate-registry --registry samples\representative-suite.json
windows\blpvm-companion.cmd init-settings --registry samples\representative-suite.json
```

The launcher writes settings to `%APPDATA%\BlenderLinkedPartVersionManager\settings.json`. It does not store credentials, tokens, or `.blend` file contents.
