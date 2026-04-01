# 実装ガイド & ベストプラクティス

## プロジェクト構造の理由

### なぜモジュール分割したのか?

```
✅ services/ による関心事の分離
  • speech.py      → Azure 音声認識の詳細
  • llm.py         → Azure LLM インテグレーション
  • parser.py      → データ処理ロジック

✅ tests/ による品質保証
  • テストが実装と並行して検討される
  • モックの使用で外部依存を排除

✅ models.py によるデータ構造
  • dataclass で型安全性
  • to_dict() でシリアライズ対応
```

## 実装時の設計判断

### 1. **スレッド安全性** (services/speech.py)

#### 問題

```python
# ❌ 未対応: recognizer.running というプロパティない
while recognizer.running and timeout_check:
    time.sleep(0.1)
```

#### 解決策

```python
# ✅ threading.Event で同期
session_stopped_event = threading.Event()

def on_session_stopped(evt):
    session_stopped_event.set()

recognizer.session_stopped.connect(on_session_stopped)
recognizer.start_continuous_recognition()
session_stopped_event.wait(timeout=300)  # ブロッキング待機
```

#### 学び

- Azure SDK のイベントドリブン設計
- Python の threading.Event はシンプルで効果的
- タイムアウトを組み込むことで無限待機を防止

---

### 2. **エラーハンドリング** (services/)

#### 戦略

```python
# レイヤー別エラー処理

# 1. API 層（speech.py, llm.py）
try:
    result = api_call()
except Exception as e:
    return f"エラーメッセージ: {str(e)}"

# 2. パース層（parser.py）
def parse_analysis_result(text):
    # 欠落時は "不明" でフォールバック
    result = {
        "main_intent": "不明",
        ...
    }

# 3. UI 層（main.py）
if result.error:
    st.error(f"❌ {result.error}")
else:
    # 表示処理
```

#### メリット

- ユーザーにわかりやすいエラー情報
- APIエラーとパースエラーを区別
- 部分的な成功を許容 (グレースフルデグラデーション)

---

### 3. **環境変数管理** (.env.example)

#### パターン

```bash
# ✅ 構造化: サービスごとにグループ化
# Azure AI Speech Configuration
SPEECH_KEY=...
SPEECH_REGION=...

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_NAME=...
```

#### 利点

-設定の検索が容易

- 新しい開発者も直感的に理解
- .env.example で実装者の意図が伝わる

---

### 4. **テストの設計** (tests/)

#### モック戦略

```python
# ❌ 避けるべき
def test_analyze():
    result = analyze_with_openai(...)  # 実API呼び出し
    # → 遅い、信頼性なし、費用発生

# ✅ 推奨パターン
@patch("services.llm.AzureOpenAI")
def test_analyze(mock_azure_openai):
    mock_client = MagicMock()
    mock_azure_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "テスト出力"
    mock_client.chat.completions.create.return_value = mock_response

    # 実装テスト
    result = analyze_with_openai(...)

    # assert ...
```

#### テスト対象の選別

```
✅ パース処理（純粋関数）
  → 外部依存なし、最もテストしやすい

✅ プロンプト生成
  → 出力形式の整合性を確認

✅ エラーハンドリング
  → 例外時の挙動を明確化

❌ AudioConfig（Azure SDK）
  → 外部ライブラリ、テスト不要
```

---

## コーディングスタイル

### Python PEP 8 準拠

```python
# ✅ 変数名: snake_case
speech_key = "abc"

# ✅ 関数名: snake_case
def speech_to_text(...):
    pass

# ✅ クラス名: PascalCase
class AnalysisResult:
    pass

# ✅ 定数: UPPER_SNAKE_CASE
MAX_FILE_SIZE_MB = 200

# ✅ ドックストリング
def analyze_audio_file(...):
    """
    単一ファイルの分析パイプライン.

    Args:
        uploaded_file: Streamlit UploadedFile
        ...

    Returns:
        AnalysisResult オブジェクト
    """
    pass
```

### Type Hints

```python
# ✅ 型を明記
def speech_to_text(
    audio_path: str,
    speech_key: str,
    speech_region: str
) -> Optional[str]:
    pass

# ✅ 複合型
def validate_files(uploaded_files: List) -> List:
    pass

# ✅ Dict の型
def get_env_variables() -> dict:
    pass
```

---

## デバッグのコツ

### 1. **音声認識がうまくいかない**

```python
# ログの有効化
speech_config = speechsdk.SpeechConfig(...)
import logging
logging.basicConfig(level=logging.DEBUG)

# 認識結果を確認
def on_recognized(evt):
    print(f"DEBUG: reason={evt.result.reason}")
    print(f"DEBUG: text={evt.result.text}")
```

### 2. **LLM の出力形式がパースできない**

```python
# パース前に出力を確認
raw_output = analyze_with_openai(...)
print("=== RAW OUTPUT ===")
print(raw_output)
print("==================")

# parse_analysis_result の出力
parsed = parse_analysis_result(raw_output)
print("=== PARSED ===")
print(parsed)
```

### 3. **環境変数が読み込めない**

```python
import os
from dotenv import load_dotenv

# 明示的なロード
load_dotenv()

# デバッグ出力
for var in ["SPEECH_KEY", "SPEECH_REGION", ...]:
    value = os.getenv(var)
    is_set = "✓" if value else "✗"
    print(f"{is_set} {var}: {value[:10] if value else 'UNSET'}...")
```

---

## パフォーマンス最適化

### メモリ使用量削減

```python
# ❌ 全ファイルをメモリ上に展開
files_data = [file.read() for file in uploaded_files]

# ✅ ストリーミング処理（一時ファイル使用）
with tempfile.NamedTemporaryFile(...) as tmp:
    tmp.write(file.getbuffer())
    # 処理
```

### 処理時間短縮

```python
# ❌ 複数ファイルの順序実行（現在）
for file in files:
    result1 = speech_to_text(file)
    result2 = analyze_with_openai(result1)
    # 総時間 = N × (5s + 10s) = N × 15s

# ✅ 将来: 並列処理
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process, file) for file in files]
    # 総時間 ≈ 15s (固定)
```

---

## セキュリティチェックリスト

- [ ] `.env` が `.gitignore` に記載されている
- [ ] APIキーがコード内にハードコードされていない
- [ ] ユーザー入力（ファイルアップロード）が検証されている
- [ ] 一時ファイルが必ず削除される（finally）
- [ ] エラーメッセージに機密情報が含まれていない
- [ ] `python-dotenv` で環境変数を安全に読み込み

---

## トラブルシューティング ガイド

### 問題: `SpeechRecognizer' object has no attribute 'running'`

```
原因: Azure SDK API の誤解
解決: threading.Event による待機に変更
  → イベント駆動で確実に完了を検知
```

### 問題: `ModuleNotFoundError: No module named 'azure'`

```
原因: azure-cognitiveservices-speech パッケージ未インストール
解決: pip install -r requirements.txt
```

### 問題: 音声認識が完了しない（タイムアウト）

```
原因:
  1. オーディオファイルが破損している
  2. Azure リージョンが非対応
  3. ネットワーク遅延

解決:
  1. ffmpeg で WAV 形式を確認: ffprobe file.wav
  2. Azure UI で Speechリソースのヘルスチェック
  3. ローカルから Azure への接続確認
```

### 問題: OpenAI API で 429 エラー（レート制限）

```
原因: API の呼び出し回数が制限を超過
解決:
  1. リトライロジックを追加
  2. API版の変更を検討
  3. Azure のクォータ確認
```

---

## 将来の拡張案

### Phase 2: 機能拡張

```python
# 1. 多言語対応
speech_config.speech_recognition_language = "en-US"  # 英語

# 2. カスタムインテント定義
CUSTOM_INTENTS = {
    "解約": ["解約したい", "辞めたい"],
    "クレーム": ["怒っている", "問題がある"],
}

# 3. キーワード抽出
from services.keyword_extractor import extract_keywords
keywords = extract_keywords(transcription)

# 4. 感情分析
from services.sentiment import analyze_sentiment
sentiment = analyze_sentiment(transcription)
```

### Phase 3: インフラ統合

```python
# REST API 化
from fastapi import FastAPI
app = FastAPI()

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile):
    result = analyze_audio_file(file, env_vars)
    return result.to_dict()

# データベース連携
from sqlalchemy import create_engine
engine = create_engine("postgresql://...")
session = Session(engine)
session.add(analysis_result_to_model(result))
session.commit()

# キューシステム
from celery import Celery
app = Celery("tasks")

@app.task
def async_analyze(file_path):
    # 非同期処理
    pass
```

---

## まとめ: 実装の工夫点

| 項目               | 工夫                             |
| ------------------ | -------------------------------- |
| **モジュール設計** | サービスごとに関心事を分離       |
| **エラー処理**     | ユーザーフレンドリーなメッセージ |
| **テスト戦略**     | モック使用で外部依存を排除       |
| **環境管理**       | .env で安全に認証情報を管理      |
| **パフォーマンス** | 一時ファイル使用でメモリ節約     |
| **セキュリティ**   | .gitignore、APIキー非表示        |

---

**最終更新:** 2026年4月
