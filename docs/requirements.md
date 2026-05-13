# 要件定義

## 目的

Blender Linked Part Version Manager は、複数人が Hair、Body、Face、Accessories などの部位別 `.blend` を並行編集し、統合用 `.blend` では Blender Link によって最新状態を確認できるようにする。

## 対象ユーザー

- 3D キャラクターや複合モデルを部位ごとに分担する小規模チーム
- GitHub、Git LFS、共有フォルダ、NAS、DCC 管理システムを使いながら Blender で統合作業を行う制作者
- Link 参照の破損、取得忘れ、作業担当の混乱を避けたいリードモデラー

## スコープ

- 統合用 `.blend` と部位別作業 `.blend` の関係をレジストリとして管理する。
- 部位タグ、担当者、リンク元、取得バージョン、更新ポリシーを記録する。
- 任意実行または定期実行の sync plan を作り、実行前に更新対象と危険操作を表示する。
- Blender Link の参照状態を検出し、必要に応じて linked library / collection の reload を実行する。
- GitHub / Git CLI / ローカルファイル管理を adapter として扱い、MVP は Git とローカルフォルダから始める。

## Functional Requirements

- R1: 部位を `partTag` で管理し、初期タグとして `Hair`、`Body`、`Face`、`Accessories`、`Clothes`、`Rig`、`Props` を扱える。
- R2: 各部位に `blendPath`、`linkedCollection`、`owner`、`sourceType`、`versionRef`、`updatePolicy` を持たせる。
- R3: 統合 `.blend` からリンク済み library を読み取り、レジストリとの差分を検出する。
- R4: `pull` 相当の取得前に、更新される部位、未取得の部位、衝突候補、ローカル未保存状態を dry-run で表示する。
- R5: `push` 相当の作業公開前に、担当部位、変更対象ファイル、未検証項目、コミットメッセージ候補を確認する。
- R6: 自動 sync は既定で取得と reload までに限定し、push は明示実行だけにする。
- R7: 取得失敗、Link 破損、collection 名不一致、権限不足、外部ツール未検出を分類してレポートする。
- R8: バッチ実行は UI から分離し、途中失敗しても統合 `.blend` を保存しない dry-run モードを提供する。
- R9: registry と sync result は JSON として保存し、Issue、QCDS、release evidence へ転記できる形にする。
- R10: 文字化けした部位名、タグ、パス、説明文を検出し、正式成果物へ混入させない。

## Non Functional Requirements

- Blender UI の応答性を保つため、外部取得と差分確認は job / worker として分離する。
- GitHub token や認証情報は保存しない。利用する場合は既存の Git Credential Manager や環境変数に委譲する。
- Windows パス、相対パス、リポジトリ内パスを混在させず、registry では canonical path と表示用 path を分ける。
- Link reload の前に保存状態と更新対象を表示し、ユーザーが破壊的操作を避けられるようにする。
- 公開前の QCDS は Blender runtime gate を含め、Quality と Satisfaction を `A-` 以上にする。

## Out of Scope

- DCC 全体の production tracking 置き換え
- Git の競合解決そのものの自動化
- `.blend` バイナリ差分の完全マージ
- Blender 以外の DCC ホスト対応
