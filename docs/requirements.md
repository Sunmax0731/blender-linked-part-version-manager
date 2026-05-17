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
- Windows companion launcher で registry 検証、状態 preview、設定保存、installer dry-run を実行できる。

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
- R11: Windows companion launcher は `%APPDATA%\BlenderLinkedPartVersionManager\settings.json` に設定を保存し、認証情報や `.blend` 本体を保存しない。
- R12: alpha release では local executable / installer dry-run の platform runtime gate を必須にし、Blender Link reload 実機確認はリリース後の手動確認として追跡する。
- R13: Blender GUI から現在の linked library / collection を scan し、Part Registry 候補を編集して保存できる。
- R14: Blender GUI から Explorer / Blender file selector で部位 `.blend` を選び、dry-run 確認後の明示操作で現在の Blender tree へ Link できる。Link 対象は `.blend` 内の production collection を優先し、collection がない場合は production object を対象にできる。
- R15: Blender の表示言語が日本語の場合、アドオンのパネル、ボタン、operator 名、主要メッセージを日本語で表示し、日本語以外の環境では既存の英語表示を維持する。
- R16: Blender GUI から選択中の linked `.blend` を現在の Blender file へ統合する前に、対象ファイル、出力先、不可逆性を確認し、結果と warning を report として確認できる。
- R17: `Character.blend` を統合表示用 file として使うユーザー向けに、素体、頭 / 表情、髪、服、アクセサリの参照関係、編集責務、Link 管理対象、検証レポート上の扱いを関係表で確認できる。
- R18: Link 候補の object 種別を report に出し、Reference 用画像、ライト、カメラなど 3D モデル以外の object はユーザーが明示選択した場合だけ Link 対象にできる。floor / helper 系などサポート対象外は除外理由を report に残す。
- R19: Blender GUI で読み込んだ `.blend` の collection 一覧をチェックボックス表示し、チェック済み collection だけを `Preview Link` / `Link Candidate` の対象にできる。

## Non Functional Requirements

- Blender UI の応答性を保つため、外部取得と差分確認は job / worker として分離する。
- GitHub token や認証情報は保存しない。利用する場合は既存の Git Credential Manager や環境変数に委譲する。
- Windows パス、相対パス、リポジトリ内パスを混在させず、registry では canonical path と表示用 path を分ける。
- Link reload の前に保存状態と更新対象を表示し、ユーザーが破壊的操作を避けられるようにする。
- GUI からの Link 追加は現在の Blender session に限定し、`.blend` 本体を自動保存しない。
- GUI からの Link 追加は `ref` / `reference` / camera / light / floor 系だけを先頭 fallback で Link せず、候補一覧と推奨対象を dry-run report に残す。
- collection checkbox がある場合、チェックされていない collection は Link 対象にしない。チェックがない場合は誤 Link を止め、既存の object 名明示 Link だけを fallback として残す。
- 3D モデル以外の Link 候補は object type / category / selection policy を report に残し、Reference 用画像やライトを暗黙 Link しない。
- linked file 統合は linked datablock を local data に変える操作であるため、confirmation cancel 時は `.blend` 本体、Link 状態、Part Registry を変更しない。
- alpha 公開前の QCDS は Windows platform runtime gate と自動テストを含め、Blender 実機確認の未実施を明記する。

## Out of Scope

- DCC 全体の production tracking 置き換え
- Git の競合解決そのものの自動化
- `.blend` バイナリ差分の完全マージ
- Blender 以外の DCC ホスト対応
