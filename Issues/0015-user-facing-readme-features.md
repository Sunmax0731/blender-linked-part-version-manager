# GitHub トップ README を利用者向けに整理し、機能一覧ドキュメントを追加する

- Status: done
- Priority: P2
- Type: docs
- Source: user
- Phase: 06-release
- Created: 2026-05-15
- QCDS: Quality, Satisfaction

## Context

GitHub リポジトリのトップに表示される `README.md` が開発準備や内部情報寄りで、利用者がアドオンの目的、代表機能、導入方法、使い方を把握しづらい。トップ README を利用者向けに整理し、詳細な機能一覧は専用 docs として分離する。

## Acceptance Criteria

- [x] `README.md` の冒頭でアドオンの目的と対象ユーザーが分かる。
- [x] 代表的な機能が GitHub トップで把握できる。
- [x] 導入方法と基本的な使い方が README から分かる。
- [x] README から機能一覧へリンクしている。
- [x] `docs/features.md` に各機能の内容と利用目的を記載している。
- [x] TODO、Issues、repo guidance、docs check が同期されている。

## Notes

- Added `docs/features.md`.
- Rewrote `README.md` as a user-facing GitHub top page.
- Kept development details behind the `開発者向け` section.
