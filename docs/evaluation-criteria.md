# 評価基準

## QCDS

QCDS は Quality、Cost、Delivery、Satisfaction を `S+ / S- / A+ / A- / B+ / B- / C+ / C- / D+ / D-` で評価する。

## Quality

- Part Registry が必要な Link 情報を漏れなく検査できる。
- Blender CLI smoke が実行済みで、Link reload の manual host test が結果付きで追跡されている。
- linked file 統合は dry-run、確認ダイアログ、cancel 無変更、report evidence を持つ。
- local-dirty と conflict-risk の自動更新を止められる。

## Cost

- Git、local folder、future adapter が同じ contract に乗る。
- Blender API 依存を `blender.link` に閉じ込め、core は通常テストで検証できる。
- credentials や環境依存 path を docs / samples に固定しない。

## Delivery

- README、導入手順、手動テスト、release checklist、QCDS が揃っている。
- closed alpha package と docs ZIP が生成できる。
- GitHub prerelease evidence が残っている。

## Satisfaction

- 統合担当者が、更新すべき部位と危険な部位を迷わず判別できる。
- 部位担当者が push 前に必要な確認項目を理解できる。
- Link 破損や外部取得失敗が、次の復旧操作に結びつく表現で表示される。
