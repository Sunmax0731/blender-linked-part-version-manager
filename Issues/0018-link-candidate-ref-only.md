# Link Candidate が `ref` collection だけをリンクする不具合を修正する

- Status: done
- Priority: P1
- Type: bug
- Source: user-report
- Draft source: codex-cli
- Phase: 04-implementation
- Created: 2026-05-16
- QCDS: Quality, Delivery, Satisfaction

## Context

ユーザーが部位 `.blend` から画像1枚目の対象を画像2枚目の統合ファイルへ `Link Candidate` でリンクしようとしたところ、目的の衣装/素体ではなく `ref` だけがリンクされた。

画像2枚目の Outliner では `ref` 配下に `ref1_front`、`ref2_back`、`ref3_side1`、`ref4_side2` が増えており、Part Registry 側の `linkedCollection` も `ref` になっている。画像1枚目の Outliner には `Armature`、`base_body`、`base_face`、`ref` など複数 collection があるため、候補追加または Link 実行時の collection 選択が曖昧なまま先頭 collection を選んでいる可能性が高い。

## Acceptance Criteria

- [x] `Add File Candidate` / `Preview Link` がリンク対象 `.blend` 内の collection / object 候補を確認でき、`ref` など参照用 collection を誤って既定選択しにくい
- [x] `Link Candidate` が選択対象または recommended target をリンクし、`.blend` 内の先頭 collection へ暗黙 fallback しない
- [x] 明示的に指定した collection が存在しない場合は、実 Link を行わず候補一覧と失敗理由を report に残す
- [x] `ref`、`reference`、カメラ/ライト/floor 系を避けて、メッシュ/アーマチュアを含む production collection / object を優先する自動候補がある
- [x] Blender UI の英語既定表示と `ja_JP` 翻訳は新規表示ラベルなしで維持され、追加情報は preview JSON に記録されている
- [x] Python unit test と Blender CLI smoke で collection 選択と fallback 禁止を検証できる

## Notes

- ユーザー報告日: 2026-05-16
- 想定原因: `bpy.data.libraries.load(..., link=True)` の `data_from.collections` から `available[0]` を暗黙選択しているため、目的 collection より前にある `ref` がリンクされる。
- `.blend` は自動保存しない。修正確認も preview / report を先に出す。
- 修正: Link 前に `availableCollections` / `availableObjects` を inspection し、`recommendedCollection` / `recommendedObjects` / `linkMode` を preview JSON に出すようにした。ファイル名由来の既定 `linkedCollection` が実在しない場合は production collection を推奨し、collection がない場合だけ production object link に fallback する。明示的な missing collection は失敗にする。
- 実ファイル確認: Blender 5.1.1 CLI で `D:\Work\Blender\Shirayukikokoro\blender\base_blender\base.blend` を inspection し、collections=`ref`, `Collection`, `2_acc`, `1_costume`, `0_hair`、objects=`base_face`, `base_body`, `Armature` などを確認した。旧既定 `base` の preview は修正後 `ref` ではなく `1_costume` を recommended target にする。
- 自動検証: `python -m unittest tests.test_registry_plan` と `cmd.exe /d /s /c npm test` が通過した。
