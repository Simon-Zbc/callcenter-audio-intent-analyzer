# システムアーキテクチャ

## 概要

コールセンター音声インテント抽出 は、Streamlit を UI フレームワークとし、Azure のマネージドサービスを活用した音声分析システムです。

## システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                    ユーザー（ブラウザ）                        │
│              http://localhost:8501                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │      Streamlit アプリケーション      │
        │        (main.py)                 │
        ├────────────────────────────────┤
        │ • ファイルアップロード処理      │
        │ • セッション管理                │
        │ • UI レンダリング              │
        └────────────┬──────────┬────────┘
                     │          │
        ┌────────────▼──┐  ┌───▼──────────────┐
        │   services/   │  │  models.py       │
        │   モジュール   │  │  (AnalysisResult)│
        └───┬──┬───┬────┘  └──────────────────┘
            │  │   │
    ┌───────▼┐ │   └─────────┬──────────────────────┐
    │speech. │ │            │                       │
    │py      │ │   ┌────────▼────────┐   ┌────────▼──────┐
    │        │ │   │llm.py           │   │parser.py       │
    │        │ │   │(Azure OpenAI)   │   │(結果パース)     │
    └───┬────┘ │   └────────┬────────┘   └────────┬───────┘
        │      │            │                      │
        │      └────────────┬──────────────────────┘
        │                   │
        ▼                   ▼
   ┌─────────────────┐  ┌────────────────────┐
   │Azure AI Speech  │  │Azure OpenAI        │
   │(ja-JP STT)      │  │(GPT-4 等)          │
   └─────────────────┘  └────────────────────┘
        ▲                        ▲
        │                        │
        └────────────┬───────────┘
                     │
          ┌──────────▼──────────┐
          │  Azure 認証情報      │
          │  (.env 環境変数)    │
          │  SPEECH_KEY         │
          │  AZURE_OPENAI_*     │
          └─────────────────────┘
```

## コンポーネント詳細

### 1. UI層（main.py）

**責務：**

- ファイルアップロード UI
- 進捗表示と状態管理
- 結果表示の3セクションレンダリング

**主要関数：**

```python
get_env_variables()        # 環境変数の取得・検証
validate_files()           # ファイル検証（拡張子・サイズ）
analyze_audio_file()       # 単一ファイル分析オーケストレーション
```

### 2. ビジネスロジック層（services/）

#### `speech.py` - 音声認識

```python
speech_to_text(audio_path, speech_key, speech_region)
  → Azure AI Speech で日本語文字起こし
  → イベント駆動による非同期的完了検知
```

**特徴：**

- `threading.Event()` でセッション完了を同期
- 音声の長さに応じた自動タイムアウト（300秒）
- エラーハンドリング（無音検知など）

#### `llm.py` - インテント抽出

```python
create_analysis_prompt(transcription)
  → プロンプト生成（日本語指定フォーマット）

analyze_with_openai(transcription, ...)
  → Azure OpenAI API 呼び出し
  → max_completion_tokens: 16384（充分な出力）
```

**特徴：**

- エンドポイント自動正規化（末尾/削除）
- API版のデフォルト値：2025-04-01-preview
- システムプロンプトによる品質向上

#### `parser.py` - 結果パース

```python
parse_analysis_result(text)
  → LLM 出力から構造化フィールド抽出
  → 欠落時に "不明" でフォールバック
```

**抽出フィールド：**

- main_intent / summary / question / answer / details / advice

### 3. データモデル（models.py）

```python
@dataclass
class AnalysisResult:
    filename: str
    main_intent: str
    summary: str
    question: str
    answer: str
    details: str
    transcription: str
    audio_file: Optional[object]
    error: Optional[str]
```

## データフロー

### 処理フロー図

```
1. ユーザーが WAV ファイルを複数選択
                ↓
2. validate_files() で検証
   • .wav 拡張子チェック
   • 200MB 制限チェック
                ↓
3. 「一括解析を実行する」ボタン クリック
                ↓
4. ファイルごとにループ処理
   ┌─────────────────────────────────────┐
   │ analyze_audio_file(file, i, total)  │ ← 各ファイル
   ├─────────────────────────────────────┤
   │ • tempfile.NamedTemporaryFile()      │
   │ • speech_to_text() 呼び出し         │
   │   └→ Azure AI Speech                │
   │ • analyze_with_openai() 呼び出し   │
   │   └→ Azure OpenAI (GPT-4等)        │
   │ • parse_analysis_result() 呼び出し  │
   │   └→ 構造化データ化                 │
   │ • AnalysisResult オブジェクト生成  │
   └─────────────────────────────────────┘
                ↓
5. 結果をリスト格納
   analysis_results: List[AnalysisResult]
                ↓
6. 3セクションで結果表示
   • 📋 各音声の要約
   • 📊 インテント一覧表
   • 📄 詳細分析（音声+2カラム）
```

## エラーハンドリング戦略

### レイヤー別エラー処理

| レイヤー | エラー種別       | 対応                                     |
| -------- | ---------------- | ---------------------------------------- |
| UI       | 環境変数不足     | 起動時に st.error()で停止                |
| 検証     | ファイル不正     | st.warning()で除外、続行                 |
| 音声認識 | 無音/未対応形式  | 分かやすいメッセージを返却               |
| LLM      | API クォータ超過 | エラーメッセージを AnalysisResult に格納 |
| パース   | 形式不一致       | "不明" でフォールバック                  |

### 例外安全性

```python
try:
    # 処理
except Exception as e:
    # エラーメッセージをユーザーに見えやすく
    return AnalysisResult(..., error=str(e))
finally:
    # 一時ファイル絶対削除
    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)
```

## セッション状態管理

Streamlit のセッション機能を活用：

```python
st.session_state.analysis_results = [...]
```

- ページ再レンダリング時も結果を保持
- 複数回の分析結果を独立管理

## 環境設定

### 環境変数の依存関係

```
SPEECH_KEY ──┐
SPEECH_REGION├──→ Azure AI Speech API


AZURE_OPENAI_ENDPOINT ──┐
AZURE_OPENAI_API_KEY ────├──→ Azure OpenAI API
AZURE_OPENAI_DEPLOYMENT_NAME ┤
AZURE_OPENAI_API_VERSION ────┘
```

### 認証フロー

```
.env ファイル読み込み
        ↓
python-dotenv で環境変数ロード
        ↓
get_env_variables() で検証
        ↓
各サービスの API クライアント初期化
  • SpeechConfig (subscription=SPEECH_KEY, region=...)
  • AzureOpenAI (azure_endpoint=..., api_key=...)
```

## スケーラビリティ考慮

### 現在の制限

- ブラウザ単一セッション処理（複数クライアント非対応）
- 複数ファイルは順序実行（並列化なし）
- メモリ上のセッション管理

### 将来の拡張案

| 機能         | 実装方法                                |
| ------------ | --------------------------------------- |
| バッチ処理   | CLI ツール化（Typer等）                 |
| 並列化       | `concurrent.futures.ThreadPoolExecutor` |
| 永続化       | PostgreSQL/MongoDB 連携                 |
| REST API化   | FastAPI ラッパー                        |
| キューイング | Celery + Redis                          |

## テスト戦略

### ユニットテスト

```
services/parser.py
  ├─ 正常系（全フィールド抽出）
  ├─ 異常系（部分的な入力）
  └─ エッジケース（空値、余白）

services/llm.py
  ├─ プロンプト生成検証
  ├─ API エラーハンドリング
  └─ エンドポイント正規化
```

### モック戦略

```python
@patch("services.llm.AzureOpenAI")
def test_api_call(mock_azure_openai):
    # 実外部 API へ接続しない
    mock_client = MagicMock()
    mock_azure_openai.return_value = mock_client
    # テスト実行
```

### 統合テスト（手動）

1. 有効な WAV + 有効な Azure 認証情報
   → 全フロー成功パス確認

2. 無音 WAV
   → 音声認識エラー処理確認

3. 不正な認証情報
   → API エラーハンドリング確認

## パフォーマンス特性

### 処理時間の目安

| 処理                  | 時間        |
| --------------------- | ----------- |
| 音声認識（1分音声）   | 2-5秒       |
| LLM 分析              | 5-15秒      |
| パース処理            | <1秒        |
| **合計（1ファイル）** | **10-30秒** |

### メモリ使用量

- 音声ファイル（200MB上限）
- テンポラリファイル（使用後削除）
- アナライシスリザルト（JSON相当、数KB/ファイル）

**総推定量：** 200MB + 数MB

## セキュリティ設計

### 認証情報保護

```
❌ コード内にハードコード
✅ .env ファイル（.gitignore記載）
✅ Azure Key Vault（本番環境）
```

### 入力検証

```python
# ファイルサイズ検証
if file_size > MAX_FILE_SIZE_BYTES:
    reject()

# ファイル拡張子検証
if not file.name.lower().endswith(".wav"):
    reject()
```

### 出力サニタイズ

- LLM の出力はそのまま表示（信頼性は LLM に依存）
- ユーザー入力なし（UI でアップロードのみ）

## デプロイメント考慮事項

### ローカル開発

```bash
streamlit run main.py
# localhost:8501
```

### クラウドデプロイ（例：Heroku/Azure App Service）

```bash
# requirements.txt を pip install
# streamlit config.toml で headless モード
# environment variables を設定
```

---

**最終更新:** 2026年4月
