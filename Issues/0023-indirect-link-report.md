# Link した Collection の間接 linked library を report する

- Status: done
- Priority: P2
- Type: feature
- Source: user-request
- Phase: 04-implementation
- Created: 2026-05-17
- QCDS: Quality, Satisfaction

## Context

source `.blend` の Collection 内に、さらに別 `.blend` から Link された Object / Collection が含まれる場合、Blender は依存 Link を indirect linked library として読み込める。この add-on では Blender 標準の Link 動作を維持し、local 化や自動保存は行わず、Preview / Link report に依存関係を可視化する。

## Acceptance Criteria

- [x] `Add File Candidate` / `Preview Link` が、選択した source `.blend` 内の linked library 依存を report する。
- [x] `Link Candidate` が、直接 Link した source library と、Blender が読み込んだ indirect library を report する。
- [x] Collection checkbox multi-link はチェック済み Collection だけを Link し、現在の `.blend` を自動保存しない。
- [x] source dependency inspection と indirect library reporting を Python unit test で検証する。
- [x] TODO、Issues、docs、tests、QCDS evidence、release evidence が同期されている。

## Notes

- 2026-05-17: `sourceLinkedLibraries` を linkable data inspection と Preview JSON に追加した。
- 2026-05-17: `linkedLibraries` と `indirectLinkedLibraries` を Link execution result に追加した。`indirectLinkedLibraries` は nested Link 参照から Blender が読み込んだ依存 library を記録する。
- 2026-05-17: 自動検証: `python -m unittest tests.test_registry_plan` が 25 tests で通過した。
