# 実装計画

## Phase 01 Requirements

- 既存案との重複確認を完了する。
- 部位別 Link 共同制作の対象ユーザー、スコープ、危険操作を要件化する。
- GitHub remote とローカル `origin` を設定する。

## Phase 02 Specification

- Part Registry schema を確定する。
- sync adapter contract と status classification を確定する。
- Blender Link 検出、reload、Link 追加候補の仕様を固める。

## Phase 03 Design

- Blender パネルの情報設計を固める。
- dry-run、risk 表示、disabled action のルールを定義する。
- scheduled pull を MVP に含めるか、post-MVP に送るかを決める。

## Phase 04 Implementation

- `core.registry` と JSON validator を実装する。
- `core.plan` で status classification と dry-run report を生成する。
- `adapters.git` と `adapters.local` の MVP を実装する。
- Blender アドオン shell、panel、operator、Link inspector、reload operator を実装する。

## Phase 05 Test

- Node または Python の unit test で registry / plan / adapter を検証する。
- Git fixture で remote-newer、local-dirty、conflict-risk を再現する。
- Blender runtime gate で Integration File が Part File を Link し、reload できることを確認する。
- 文字化け、JSON schema、docs completeness を `npm test` に含める。

## Phase 06 Release

- インストール手順、ユーザーガイド、manual test、QCDS、competitive benchmark を更新する。
- closed alpha prerelease 用の docs ZIP と release notes を作成する。
- GitHub Release は prerelease とし、手動テスト未実施項目を明記する。
