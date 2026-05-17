# 読み込んだ `.blend` の collection をチェックボックスで複数 Link できるようにする

- Status: done
- Priority: P2
- Type: feature
- Source: user-request
- Phase: 04-implementation
- Created: 2026-05-17
- QCDS: Quality, Satisfaction

## Context

`Add File Candidate` で読み込んだ Blender ファイルから collection の一覧を表示し、ユーザーがチェックを入れた collection ごとに `Preview Link` / `Link Candidate` で現在の Blender tree へ Link できるようにする。既存の単一 `linkedCollection` 入力と object 明示 Link は維持し、`.blend` は自動保存しない。

## Acceptance Criteria

- [x] 読み込んだ `.blend` の collection 一覧が Blender UI にチェックボックスとして表示される
- [x] チェック済み collection だけを `Preview Link` の dry-run 対象にできる
- [x] チェック済み collection ごとに `Link Candidate` が current scene tree へ Link できる
- [x] チェックがない場合は誤 Link せず、既存 object 明示 Link の fallback は維持される
- [x] docs、tests、QCDS evidence、TODO / Issues が同期されている

## Notes

- 2026-05-17: `BLPVM_LinkCollectionChoice` を追加し、`Add File Candidate` で読み取った available collection を registry candidate 上の checkbox として保持するようにした。
- 2026-05-17: `link_collections_from_file` を追加し、チェック済み collection を dry-run では `linkedCollections` として report、実行時は各 collection を current scene tree へ Link するようにした。
- 2026-05-17: collection checkbox がある場合はチェック済み collection を優先し、チェックなしで候補内 collection を指す場合は誤 Link を止める。collection 候補外の object 名は既存の明示 object Link fallback として維持した。
- 自動検証: `python -m unittest tests.test_registry_plan` と `cmd.exe /d /s /c npm test` が通過した。
