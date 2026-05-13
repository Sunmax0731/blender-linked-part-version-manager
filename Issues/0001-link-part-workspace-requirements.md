# 部位別 Link 共同制作の要件を確定する

- Status: done
- Priority: P1
- Phase: 01-requirements
- Linked TODO: [TODO.md](../TODO.md)
- GitHub Issue: https://github.com/Sunmax0731/blender-linked-part-version-manager/issues/1

## 背景

Blender Link を使って統合 `.blend` と部位別 `.blend` を分ける運用では、部位タグ、担当者、リンク元、取得状態、更新ポリシーを先に固める必要がある。

## Acceptance Criteria

- [x] MVP で扱う部位タグと必須項目が確定している。
- [x] GitHub / Git / local folder のどこまでを MVP に含めるか決まっている。
- [x] scheduled pull と push 支援を MVP に含めるか post-MVP に送るか決まっている。
- [x] `docs/requirements.md` と `docs/qcds-evaluation.md` が更新されている。

## Resolution

MVP は manual pull / batch refresh、Git adapter dry-run、local folder adapter dry-run、Blender Link reload preview、Windows companion launcher に限定する。scheduled pull と push 実行支援は post-MVP とし、alpha release 後の Blender 実機確認で追加判断する。
