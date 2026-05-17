# Character.blend 統合構成の関係表

このドキュメントは、`Character.blend` を統合表示用ファイルとして使い、素体、頭 / 表情、髪、服、アクセサリを部位別 `.blend` として管理する場合の参照関係を整理する。添付スケッチで示された「Character 側で統合して表示し、各部位は個別編集する」運用を、Blender Linked Part Version Manager の Link 管理、Part Registry、検証レポートへ落とし込むためのユーザー向け関係表である。

## 前提

- `Character.blend` は統合表示用の Integration File とし、部位そのものの制作編集は行わない。
- 素体用 `.blend` は、頭 / 表情、髪、服、アクセサリの制作時に参照される共通 base file とする。
- 頭 / 表情、髪、服、アクセサリは、それぞれ独立した Part File として編集する。
- `Character.blend` には最終確認に必要な部位を Blender Link で読み込み、更新は preview と明示 reload の後に確認する。
- MVP の registry schema は `dependsOn` 専用フィールドを持たないため、素体への依存は `displayName`、`source.path`、検証レポートの note、または運用ドキュメントで確認する。

## 参照関係の全体像

```text
base_body.blend
  -> head_face.blend / main_face.blend
  -> hair.blend / main_hair.blend
  -> clothes.blend
  -> accessories.blend / glasses.blend

Character.blend
  -> base_body.blend
  -> head_face.blend / main_face.blend
  -> hair.blend / main_hair.blend
  -> clothes.blend
  -> accessories.blend / glasses.blend
```

`base_body.blend` は各部位ファイルが形状合わせのために参照する。`Character.blend` も統合表示のために素体を直接 Link するが、素体の編集責務は `base_body.blend` 側に残す。

## ファイル別の役割と参照方向

| Blend file | 役割 | 参照する file | 参照される file | 主な編集対象 | `Character.blend` での表示対象 |
| --- | --- | --- | --- | --- | --- |
| `Character.blend` | Integration File。全体確認、registry validation、sync preview、reload 操作の起点。 | `base_body.blend`、頭 / 表情、髪、服、アクセサリの Part File | なし | 統合表示、配置確認、Link 状態確認。部位メッシュは編集しない。 | 素体、頭 / 表情、髪、服、アクセサリを統合表示する。 |
| `base_body.blend` | 共通素体。頭 / 表情、髪、服、アクセサリが合わせ込む基準。 | 必要に応じて参照画像、Rig、基準 object | `Character.blend`、頭 / 表情、髪、服、アクセサリの Part File | 素体 mesh、基準 Armature、体形基準、接合位置。 | Body / Rig / base reference として表示する。 |
| `head_face.blend` または `parts/face/main_face.blend` | 頭、顔、表情差分の制作 file。 | `base_body.blend` | `Character.blend` | 頭部 mesh、顔パーツ、表情 shape、口 / 目など。 | Face / Head collection として表示する。 |
| `hair.blend` または `parts/hair/main_hair.blend` | 髪の制作 file。 | `base_body.blend`、必要に応じて head reference | `Character.blend` | 髪 mesh、眉、まつ毛、髪留めなど髪側の付属要素。 | Hair collection として表示する。 |
| `clothes.blend` | 服の制作 file。 | `base_body.blend` | `Character.blend` | 服、靴、手袋、cloth 用補助 object。 | Clothes collection として表示する。 |
| `accessories.blend` または `parts/accessories/glasses.blend` | アクセサリの制作 file。 | `base_body.blend`、必要に応じて head / clothes reference | `Character.blend` | 眼鏡、装飾、武器、小物。 | Accessories collection として表示する。 |

## Part Registry での扱い

| Registry part | `partTag` | `blendPath` 例 | `linkedCollection` 例 | owner 初期値 | source 初期値 | updatePolicy | Link 管理上の扱い |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `body-body-base` | `Body` | `parts/body/base_body.blend` | `CHR_Body_Base` | `unassigned` | `local` | `manual` | 共通素体として `Character.blend` へ直接 Link する。各部位の参照元でもあるため、reload 前に影響範囲を確認する。 |
| `face-face-main` | `Face` | `parts/face/main_face.blend` | `CHR_Face_Main` | `unassigned` | `local` | `manual` | 頭 / 表情の制作成果として `Character.blend` へ Link する。素体参照は制作 file 側の依存として記録する。 |
| `hair-hair-main` | `Hair` | `parts/hair/main_hair.blend` | `CHR_Hair_Main` | `unassigned` | `local` | `manual` | 髪の制作成果として `Character.blend` へ Link する。head / body への合わせ込みは制作側で確認する。 |
| `clothes-main` | `Clothes` | `parts/clothes/main_clothes.blend` | `CHR_Clothes_Main` | `unassigned` | `local` | `manual` | 服の制作成果として `Character.blend` へ Link する。現在の fixture には未同梱の拡張候補。 |
| `accessories-acc-glasses` | `Accessories` | `parts/accessories/glasses.blend` | `CHR_ACC_Glasses` | `unassigned` | `local` | `manual` | アクセサリの制作成果として `Character.blend` へ Link する。head / clothes に合わせた位置を preview で確認する。 |

GUI で registry 候補を生成する場合、既定値は `owner=unassigned`、`source.type=local`、`source.root=.`、`versionRef=local`、`updatePolicy=manual` とする。素体参照のような部位間依存は自動 Link 対象として混ぜず、各 Part File の制作責務と検証レポートで明示する。

source `.blend` の Collection がさらに別 `.blend` を Link している場合は、Blender 標準の indirect Link として読み込ませ、`sourceLinkedLibraries` / `indirectLinkedLibraries` で依存関係を確認する。これは dependency report であり、Part Registry の直接管理行や linked datablock local 化とは分けて扱う。

## Link 管理、Registry、検証レポートの責務分離

| 領域 | 扱うもの | 扱わないもの |
| --- | --- | --- |
| Link 管理 | `Character.blend` が直接 Link している library / collection / object、preview link、reload、Auto Reload、Link integration。 | Git pull / push の責務、素体依存の意味付け、部位担当の判断。 |
| Part Registry | `partId`、`partTag`、`blendPath`、`linkedCollection`、`owner`、`source`、`versionRef`、`updatePolicy`。 | `.blend` 内部の実メッシュ編集、依存 file の自動書き換え、`Character.blend` の自動保存。 |
| 検証レポート | missing-link、broken-link、collection mismatch、reload 候補、blocked part、available collection / object、recommended target。 | 破壊的な修復実行、linked datablock の無確認 local 化、制作上の採否判断。 |

## 運用手順

1. `Character.blend` を開き、`Linked Parts` パネルで `Scan Current Links` を実行する。
2. 素体、頭 / 表情、髪、服、アクセサリの候補が Part Registry に分かれていることを確認する。
3. 未登録の Part File は `Add File Candidate` で追加し、`Preview Link` で `ref` / camera / light / floor ではなく production collection / object が推奨されていることを確認する。
4. `Save Registry` で registry JSON を保存し、`Validate Registry` を実行する。
5. `Build Sync Preview` で素体更新が head / face、hair、clothes、accessories に影響することを手動レビュー対象として扱う。
6. `Preview Reload` と `Reload Safe Links` は `Character.blend` が直接参照する Link だけを対象にする。各 Part File 内の素体参照更新は、該当 Part File を開いて確認する。
7. 納品や単一ファイル化が必要な場合だけ、コピーした fixture で `Preview Integrate` と `Integrate Link` を使い、current file は自動保存しない。

## Fixture との対応

現在の release fixture は次の最小構成を同梱している。

| Fixture path | この関係表での位置付け |
| --- | --- |
| `integration/character_integration.blend` | `Character.blend` 相当の Integration File。 |
| `parts/body/base_body.blend` | `base_body.blend` 相当の共通素体。 |
| `parts/face/main_face.blend` | 頭 / 表情 file の最小 fixture。 |
| `parts/hair/main_hair.blend` | 髪 file の最小 fixture。 |
| `parts/accessories/glasses.blend` | アクセサリ file の最小 fixture。 |
| `samples/representative-suite.json` | 上記 Link 関係を検証する Part Registry。 |

服 file は現在の fixture には含めていない。運用で追加する場合は `partTag=Clothes` の registry 行を追加し、素体参照と `Character.blend` への Link を preview で確認してから保存する。
