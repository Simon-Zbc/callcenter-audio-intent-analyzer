# 📞 コールセンター音声 インテント抽出

複数のWAV形式の音声ファイルを一括でアップロードし、Azure AI Speechで日本語文字起こし、Azure OpenAIでインテント抽出・分析できるStreamlitアプリケーションです。

## 機能

- 📁 **複数WAVファイルの一括アップロード**  
  最大200MBのWAVファイルを複数選択してアップロード可能

- 🗣️ **Azure AI Speechによる日本語文字起こし**  
  音声を日本語（ja-JP）で自動認識

- 🤖 **Azure OpenAI によるインテント抽出**  
  以下の情報を自動抽出：
  - 主要インテント（解約、料金照会、クレーム、使い方への質問 など）
  - 通話全体の要約
  - 顧客の質問内容
  - オペレーターの対応内容
  - 詳細分析
  - オペレーターへのアドバイス

- 📊 **3つのビューで結果表示**
  - 📋 各音声の要約：ファイルごとの要点
  - 📊 インテント抽出結果一覧：表形式での比較
  - 📄 詳細分析：音声プレイヤー＋文字起こし＋分析結果

## 前提条件

- **OS**: Windows / macOS / Linux
- **Python**: 3.8以上
- **WAVファイル**: 最大200MB、拡張子`.wav`のみ対応
- **Azure リソース**:
  - Azure AI Speech リソース
  - Azure OpenAI リソース（対応するデプロイメント）

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd callcenter-audio-intent-analyzer
```

### 2. 環境変数ファイルの作成

`.env.example` をコピーして `.env` ファイルを作成します：

```bash
cp .env.example .env
```

`.env` を開いて、以下の値を入力してください：

```env
# Azure AI Speech Configuration
SPEECH_KEY=your_speech_key_here
SPEECH_REGION=japaneast  # 各自のSpeechリソースのリージョンを指定

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
AZURE_OPENAI_API_VERSION=2025-04-01-preview  # 必要に応じて変更
```

**各値の取得方法:**

- `SPEECH_KEY` → Azure Portal → Speech リソース → キーと エンドポイント → キー1 / キー2
- `SPEECH_REGION` → Speech リソースの場所（例：`japaneast`, `eastus` など）
- `AZURE_OPENAI_ENDPOINT` → Azure Portal → OpenAI リソース → キーとエンドポイント → エンドポイント
- `AZURE_OPENAI_API_KEY` → OpenAI リソース → キーと エンドポイント → キー1 / キー2
- `AZURE_OPENAI_DEPLOYMENT_NAME` → OpenAI スタジオ → デプロイメント → デプロイ名

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

または uv を使用:

```bash
uv pip install -r requirements.txt
```

### 4. アプリケーションの起動

```bash
streamlit run main.py
```

ブラウザが自動的に開き、`http://localhost:8501` でアプリが起動します。

## 使い方

### ステップ 1: ファイルのアップロード

1. 左側のサイドバーの「ファイルアップロード」セクションで、1つ以上の`.wav`ファイルを選択
2. 複数選択可能（Ctrl+Click または Cmd+Click）
3. 「N件のファイルが選択されています」と表示されたことを確認

### ステップ 2: 一括解析の実行

1. 「一括解析を実行する」ボタン（青色）をクリック
2. 処理中は進捗バーが表示されます：
   - ファイルごとに文字起こしと分析を実行
   - 「処理中 (i/N): filename」と状態が更新
3. 「✅ すべてのファイルの解析が完了しました！」メッセージを確認

### ステップ 3: 結果の確認

#### 📋 各音声の要約

- ファイルごとに3カラム表示：
  - **要約**: 通話全体の簡潔な要約
  - **質問内容**: 顧客の質問や要望
  - **回答内容**: オペレーターの対応

#### 📊 インテント抽出結果一覧

- テーブル形式で全ファイルを表示
- columns: ファイル名、主要インテント、分析結果（先頭100文字）
- ファイル間での比較に便利

#### 📄 各音声の詳細分析

- ファイルごとに展開可能な詳細情報を表示
- 見出し: 📁 ファイル名 (インテント: 〇〇)
- **機能**:
  - 🎵 オーディオプレイヤーで音声を再生
  - 📝 左側：文字起こし結果（全文）
  - 💡 右側：分析結果（LLMの生出力）

## 単体テストの実行

```bash
pytest
```

または詳細表示:

```bash
pytest -v
```

特定のテストモジュールのみ実行:

```bash
# パーサーのテスト
pytest tests/test_parser.py -v

# プロンプト生成のテスト
pytest tests/test_prompt.py -v
```

## ファイル構成

```
callcenter-audio-intent-analyzer/
├── main.py                 # Streamlit メインアプリケーション
├── models.py               # データクラス定義（AnalysisResult）
├── requirements.txt        # Pythonパッケージ依存関係
├── .env.example            # 環境変数のテンプレート
├── .gitignore              # Git無視ファイル設定
├── README.md               # このファイル
├── LICENSE                 # ライセンス
│
├── services/
│   ├── __init__.py
│   ├── speech.py           # Azure AI Speech統合（文字起こし）
│   ├── llm.py              # Azure OpenAI統合（インテント抽出）
│   └── parser.py           # LLM出力のパース
│
└── tests/
    ├── __init__.py
    ├── test_parser.py      # パーサーの単体テスト
    └── test_prompt.py      # プロンプト生成・LLM呼び出しのテスト
```

## 技術スタック

| 用途       | 技術                                | バージョン |
| ---------- | ----------------------------------- | ---------- |
| UI         | Streamlit                           | ≥1.55.0    |
| 音声認識   | Azure Cognitive Services Speech SDK | ≥1.48.2    |
| LLM/分析   | OpenAI (Azure)                      | ≥2.26.0    |
| データ処理 | Pandas                              | ≥2.3.3     |
| 環境管理   | python-dotenv                       | ≥1.2.2     |
| テスト     | pytest                              | ≥7.4.0     |
| テスト補助 | pytest-mock                         | ≥3.12.0    |

## 注意事項・セキュリティ

### ⚠️ 個人情報の取り扱い

- **重要**: コールセンターの音声には顧客の個人情報（氏名、電話番号、住所など）が含まれる場合があります
- 本ツールを使用する際は、適切な情報セキュリティポリシーに準拠してください
- データは本番環境での使用前に匿名化・マスキングを検討してください

### 🔐 Secrets管理

- **`.env` ファイルをコミットしないこと**  
  `.gitignore` に記載されているため、自動的に無視されます
- **API キーは絶対にコード内に記載しないこと**  
  環境変数またはAzure Key Vaultなどで管理してください
- CI/CD パイプラインでは、マスク変数を使用してキーを保護してください

### 📝 ファイルサイズと処理時間

- 1ファイルあたり最大200MB
- 音声の長さが長いほど処理時間が増加します
- 複数ファイルの場合、順序に処理されます

### 🌐 ネットワーク

- Azure Speechおよび Azure OpenAI へのインターネット接続が必要です
- ファイアウォール/プロキシを使用する環境では適切に設定してください

## トラブルシューティング

### 環境変数が見つからない

```
❌ 環境変数が不足しています: SPEECH_KEY, ...
```

→ `.env` ファイルが正しく作成されているか確認してください

### 音声が認識できない

```
音声が認識できませんでした。または無音でした。
```

→ ファイルが有効なWAVファイルか確認してください  
→ 音声に余白（無音区間）が多くないか確認してください

### OpenAI APIエラー

```
OpenAI APIエラー: ...
```

→ Azure OpenAI のデプロイ名が正しいか確認してください  
→ API キーが有効か確認してください  
→ リージョン/エンドポイントが正しいか確認してください

### パッケージインストールエラー

```
ModuleNotFoundError: No module named 'xxx'
```

→ `pip install -r requirements.txt` を実行してください

## ライセンス

[LICENSE](LICENSE) ファイルを参照してください

## 今後の拡張機能（案）

- [ ] 複数ファイルの履歴管理
- [ ] 分析結果のCSV/Excel エクスポート
- [ ] カスタマイズ可能なインテント分類
- [ ] 音声+テキストの入力対応
- [ ] バッチ処理用CLI ツール
- [ ] データベース連携（MySQL/PostgreSQL）
- [ ] REST API化（FastAPI）

## サポート

問題が発生した場合は、以下を確認してください：

1. `.env` の設定が正しいか
2. 依存パッケージが全てインストールされているか（`pip list`）
3. WAVファイルが有効か（オーディオプレイヤーで再生確認）
4. Azureの各リソースのステータスが正常か

---

**作成日**: 2026年4月  
**対応Python**: 3.8+
