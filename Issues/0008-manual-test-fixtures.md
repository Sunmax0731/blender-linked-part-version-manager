# 手動テスト用 `.blend` fixture を alpha release に同梱する

- Status: done
- Priority: P2
- Type: release-asset
- Source: user-request
- Phase: 05-test
- Created: 2026-05-15
- QCDS: Quality, Delivery, Satisfaction

## Context

`docs/manual-test.md` は `integration/character_integration.blend` と部位別 `.blend` を前提にしていたが、repo と alpha release には実体がなかった。テスト協力者が release asset だけで同じ手順を実施できるように fixture を同梱する。

## Acceptance Criteria

- [x] `integration/character_integration.blend` が存在する。
- [x] `parts/hair/main_hair.blend`、`parts/body/base_body.blend`、`parts/face/main_face.blend`、`parts/accessories/glasses.blend` が存在する。
- [x] fixture 生成手順が `scripts/create-blend-fixtures.py` として残っている。
- [x] `npm test` の release packaging が `dist/blender-linked-part-version-manager-fixtures.zip` を生成する。
- [x] `docs/manual-test.md` と release evidence が fixture ZIP を案内している。

## Notes

- Fixture は Blender 5.1.1 で生成した。
- `integration/character_integration.blend` は4つの部位 `.blend` collection を Link 済み。
- 実 reload の Viewport 確認は `Issues/0006-blender-runtime-link-reload-manual.md` に残す。
