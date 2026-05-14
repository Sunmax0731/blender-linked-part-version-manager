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

- [x] `core.registry` と JSON validator を実装する。
- [x] `core.plan` で status classification と dry-run report を生成する。
- [x] `adapters.git` と `adapters.local` の MVP を実装する。
- [x] Blender アドオン shell、panel、operator、Link inspector、reload operator を実装する。
- [x] 保存済み linked `.blend` の Auto Reload を実装する。
- [x] Blender GUI で Part Registry 候補を scan / edit / save できる導線を実装する。
- [x] Explorer / Blender file selector から `.blend` を候補追加し、明示操作で Blender tree へ Link できる導線を実装する。
- [x] Blender 表示言語が日本語の場合にパネル、ボタン、主要メッセージが日本語で表示される `ja_JP` UI 翻訳を実装する。
- [x] Windows companion launcher、settings 保存、installer dry-run を実装する。

## Phase 05 Test

- [x] Python unit test で registry / plan / adapter を検証する。
- [x] Git runner fixture で remote-newer、local-dirty、conflict-risk を再現する。
- [x] Windows runtime gate で local executable、installer dry-run、settings 保存を確認する。
- [x] 指定 Blender 実体パスで Blender CLI smoke と add-on import を確認する。
- [x] Blender runtime gate で Integration File が Part File を Link し、reload できることを確認する。
- [x] 文字化け、JSON schema、docs completeness を `npm test` に含める。

## Phase 06 Release

- [x] インストール手順、ユーザーガイド、manual test、QCDS、competitive benchmark を更新する。
- [x] alpha prerelease 用の add-on ZIP、docs ZIP、release notes を作成する。
- [x] GitHub Release は prerelease とし、Blender 手動テスト未実施項目を明記する。
- [x] MVP 後 P2 backlog の GUI registry / release prep 項目を TODO、Issues、docs、tests、QCDS evidence と同期して完了する。
