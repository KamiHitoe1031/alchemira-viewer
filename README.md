# 残響のアルケミラ シナリオビューワー

ギャルゲーシナリオ「残響のアルケミラ」共通ルートのテキストレビュー用ビューワー。

## 機能

- **シーンリーダー**: 全16章89シーンのシナリオテキストを閲覧
- **メモ機能**: 段落をクリックしてメモを残せる（サーバー同期・端末間共有）
- **メモエクスポート**: 全メモを場所+対象テキスト+メモ内容でMarkdown出力

## Cloudflare Pages デプロイ手順

### 1. Pages プロジェクト作成

1. Cloudflare ダッシュボード → Workers & Pages → 「作成」
2. 「Pagesに接続」→ GitHubリポジトリ `alchemira-viewer` を選択
3. ビルド設定:
   - ビルドコマンド: (空欄)
   - 出力ディレクトリ: `/`
4. デプロイ

### 2. KV 名前空間の作成（メモ同期用）

1. Cloudflare ダッシュボード → Workers & Pages → KV
2. 「名前空間を作成」→ 名前: `alchemira-memos`

### 3. KV バインディングの設定

1. Pages プロジェクト → 設定 → Functions → KV名前空間バインディング
2. 追加:
   - **変数名**: `MEMOS`
   - **KV名前空間**: `alchemira-memos`（さっき作ったもの）
3. 保存 → 再デプロイ（設定 → デプロイ → 「デプロイを再試行」）

これでスマホ・PCどちらからでもメモが同期されます。

## ファイル構成

```
├── index.html          ビューワー本体
├── scenes.js           シナリオデータ（build.pyで生成）
├── functions/
│   └── api/
│       └── memos.js    メモ同期API（CF Pages Functions）
├── build.py            MDファイル→scenes.js変換スクリプト
└── README.md
```

## シーンデータの更新方法

シナリオのMDファイルを編集した後:

```bash
python build.py
git add scenes.js && git commit -m "シーンデータ更新" && git push
```

Cloudflare Pages が自動で再デプロイします。
