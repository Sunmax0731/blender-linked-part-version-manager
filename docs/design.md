# デザイン

## UI Goal

統合担当者が Blender を開いたまま、どの部位が誰の作業で、どの `.blend` から Link され、取得や reload が必要かを判断できる画面にする。

## Primary Panels

| Panel | 目的 | 主な情報 |
| --- | --- | --- |
| Part Registry | 部位一覧と担当者、タグ、リンク元を確認する。 | partTag、owner、blendPath、linkedCollection、status |
| Sync Preview | pull / reload 前の影響範囲を確認する。 | plannedActions、risk、missing/broken links |
| Link Health | 統合 `.blend` 内の library と registry の差分を見る。 | current、missing-link、broken-link、collection mismatch |
| Publish Part | 担当部位の push 前チェックを行う。 | dirty files、commit message candidate、manual checks |
| Windows Companion | Blender を起動せず registry と設定を確認する。 | registry path、parts count、settings path |

## Interaction Rules

- 危険操作は text button だけにせず、dry-run の結果を先に表示する。
- 部位タグは色付き chip として扱うが、色だけに依存せずタグ名も表示する。
- `Pull & Reload` は `local-dirty` または `conflict-risk` がある部位では無効化する。
- Auto Reload は保存済み linked `.blend` の mtime 監視に限定し、外部 sync / pull / push は実行しない。
- scheduled pull は状態表示と通知に留め、外部取得はユーザー確認を必要にする。
- Link 追加やパス修正は preview 画面で対象 library / collection を明示する。
- `Scan Current Links` は現在の linked library / collection から候補だけを作り、JSON 保存は `Save Registry` の明示操作に分ける。
- `Add File Candidate` は Explorer / Blender file selector から `.blend` を選んで候補化する。実 Link は `Preview Link` と `Link Candidate` に分け、自動保存しない。
- Link 候補化と Link 実行は `.blend` 内の available collection / object と object type を表示し、`ref` や camera / light / floor 系だけを先頭 fallback で Link しない。Reference 用画像、ライト、カメラは明示選択用の候補として扱い、floor / helper 系は除外理由を表示する。
- linked file 統合は `Preview Integrate` と `Integrate Link` に分ける。実行時は確認ダイアログで不可逆操作、対象 linked file、出力先 current file を表示し、cancel 時は何も変更しない。
- Part Registry の編集欄は `partId`、`partTag`、`displayName`、`blendPath`、`linkedCollection`、`owner`、`source`、`versionRef`、`updatePolicy` を 1 件ずつ確認できる密度にする。
- UI 文言は Blender の表示言語に従う。日本語環境では操作名と主要メッセージを日本語にし、schema field 名や JSON evidence のキーは英語のまま維持する。

## Character.blend Relationship Table

`Character.blend` を統合表示用 file とする運用では、素体、頭 / 表情、髪、服、アクセサリの参照方向と編集責務を [Character.blend 統合構成の関係表](character-blend-relationship.md) に分離して示す。UI は `Character.blend` が直接 Link している部位を操作対象にし、素体が各 Part File から参照される依存は preview / report の確認事項として扱う。

## Default Tags

| Tag | 用途 |
| --- | --- |
| Hair | 髪、眉、まつ毛など外観差分が大きい部位 |
| Body | 素体、手足、肌メッシュ |
| Face | 顔メッシュ、表情形状、口、目 |
| Clothes | 衣装、靴、手袋 |
| Accessories | 装飾、武器、小物 |
| Rig | Armature、constraint、driver |
| Props | キャラクター周辺の持ち物や台座 |

## Empty and Error States

- registry 未作成: `Create Registry from Current Links` を提示する。
- Link なし: Integration File と Part File の違いを短く表示し、Link 追加手順へ誘導する。
- 外部 sync 未設定: local-only registry として動かし、source adapter 追加を後回しにできる。
- Git 未検出: Git adapter を無効化し、local adapter と manual copy 手順を表示する。
- Windows launcher の Node.js 未検出: installer で Node.js 20 以降が必要であることを表示し、Blender アドオン ZIP の手動導入手順へ誘導する。
