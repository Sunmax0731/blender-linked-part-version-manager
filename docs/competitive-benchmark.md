# 競合・参考比較

## 比較対象

| 対象 | 強み | 弱み | 採用する基準 |
| --- | --- | --- | --- |
| Blender Library Link | Blender 標準で外部 `.blend` を参照できる。 | 取得元更新、担当者、部位タグ、衝突確認は別管理になる。 | Link 状態検出と reload は標準機能に寄せる。 |
| Blender Asset Browser | asset 化と検索に強い。 | 共同制作中の部位別作業ファイルの pull / push 管理は薄い。 | tag、preview、catalog の考え方を参考にする。 |
| Git / Git LFS | ファイル履歴とリモート共有に強い。 | `.blend` の意味的差分や Link 状態は理解しない。 | adapter として扱い、Blender UI で status を翻訳する。 |
| ShotGrid / ftrack | production tracking と承認フローに強い。 | 小規模個人制作には重い。 | 担当者、状態、レビューコメントの概念を軽量化して取り込む。 |
| Plastic SCM / Unity Version Control | 大容量バイナリとアーティスト向け workflow に強い。 | Blender Link 専用の部位 UI はない。 | conflict-risk と file locking の考え方を参考にする。 |

## Differentiation

- Link された library / collection と part registry を同じ画面で扱う。
- Hair、Body、Face、Accessories などのキャラクター部位タグを初期概念として持つ。
- GitHub / Git / ローカル共有フォルダを adapter として扱い、将来の production system に拡張できる。
- pull / reload 前の dry-run を必須にし、統合 `.blend` を壊す操作を避ける。
