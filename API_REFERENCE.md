# API リファレンス & 実装詳細

## モジュール: services.parser

### `parse_analysis_result(text: str) -> Dict[str, str]`

LLM の出力テキストから構造化フィールドを抽出します。

#### パラメータ

| 名前 | 型  | 説明                     |
| ---- | --- | ------------------------ |
| text | str | LLM から返されたテキスト |

#### 戻り値

```python
{
    "main_intent": str,      # 主要インテント（例：解約、料金照会）
    "summary": str,          # 通話要約
    "question": str,         # 顧客の質問
    "answer": str,           # オペレーターの回答
    "details": str,          # 詳細分析
    "advice": str,           # オペレーターへのアドバイス
}
```

#### ロジック

1. テキストを行で分割
2. 各行で以下の行頭パターンをマッチング：
   - `- インテント:` または `インテント:`
   - `- 要約:` または `要約:`
   - `- 質問内容:` または `質問内容:`
   - `- 回答内容:` または `回答内容:`
   - `- 詳細:` または `詳細:`
   - `- オペレーターへのアドバイス:` または `オペレーターへのアドバイス:`

3. マッチしたら `:` の後の値を strip して抽出
4. 取得できないフィールドは `"不明"` でフォールバック

#### 使用例

```python
from services.parser import parse_analysis_result

llm_output = """
- インテント: 解約
- 要約: 顧客が料金に不満で解約希望
- 質問内容: どうしたら解約できるか
- 回答内容: 解約手続きを説明した
- 詳細: 長期契約の割高感が解約理由
- オペレーターへのアドバイス: 料金プラン見直しを提案
"""

result = parse_analysis_result(llm_output)
print(result["main_intent"])  # "解約"
print(result["summary"])      # "顧客が料金に不満で解約希望"
```

---

## モジュール: services.speech

### `speech_to_text(audio_path: str, speech_key: str, speech_region: str) -> Optional[str]`

Azure AI Speech で音声ファイルを日本語テキストに変換します。

#### パラメータ

| 名前          | 型  | 説明                                           |
| ------------- | --- | ---------------------------------------------- |
| audio_path    | str | WAV ファイルのパス（絶対パス推奨）             |
| speech_key    | str | Azure Speech API キー                          |
| speech_region | str | Speech リソースのリージョン（例：`japaneast`） |

#### 戻り値

```python
str | None
```

- **成功時:** 文字起こしテキスト
- **失敗時:** エラーメッセージ（`"音声認識エラー: ..."` 形式）

#### 処理フロー

```
1. SpeechConfig 作成
   speech_recognition_language = "ja-JP"

2. AudioConfig で WAV ファイルを指定

3. SpeechRecognizer 初期化

4. イベントハンドラ設定
   - on_recognized: テキストをリストに追加
   - on_session_stopped: 完了イベント設定
   - on_canceled: 完了イベント設定

5. start_continuous_recognition() 開始

6. session_stopped_event.wait(timeout=300) で完了待機

7. 結果テキストを結合して返却
```

#### 例外処理

| 例外パターン           | 返却値                                             |
| ---------------------- | -------------------------------------------------- |
| 認識できない/無音      | `"音声が認識できませんでした。または無音でした。"` |
| API接続エラー          | `"音声認識エラー: <詳細>"`                         |
| その他予期しないエラー | `"音声認識エラー: <詳細>"`                         |

#### 使用例

```python
from services.speech import speech_to_text

result = speech_to_text(
    audio_path="sample.wav",
    speech_key="your-speech-key",
    speech_region="japaneast"
)

if result.startswith("音声認識エラー"):
    print("エラー:", result)
else:
    print("文字起こし:", result)
```

#### パフォーマンス

- タイムアウト: 300秒（5分）
- 1分間の音声: 約2-5秒で完了
- メモリ: WAVファイルサイズ程度

---

## モジュール: services.llm

### `create_analysis_prompt(transcription: str) -> str`

Azure OpenAI に送送するプロンプトを生成します。

#### パラメータ

| 名前          | 型  | 説明                     |
| ------------- | --- | ------------------------ |
| transcription | str | 音声認識から得たテキスト |

#### 戻り値

```python
str
```

構造化外出形式を指定した日本語プロンプト

#### プロンプト構造

```markdown
以下はコールセンターの通話内容です。...

通話内容:
{transcription}

以下のフォーマットで必ず返してください:

- インテント: [...]
- 要約: [...]
- 質問内容: [...]
- 回答内容: [...]
- 詳細: [...]
- オペレーターへのアドバイス: [...]
```

#### 使用例

```python
from services.llm import create_analysis_prompt

transcription = "お世話になっています。..."
prompt = create_analysis_prompt(transcription)
print(prompt)
```

---

### `analyze_with_openai(transcription: str, azure_endpoint: str, api_key: str, deployment_name: str, api_version: str = "2025-04-01-preview") -> Optional[str]`

Azure OpenAI API を呼び出して音声分析を実行します。

#### パラメータ

| 名前            | 型  | デフォルト             | 説明                            |
| --------------- | --- | ---------------------- | ------------------------------- |
| transcription   | str | -                      | 分析対象の文字起こしテキスト    |
| azure_endpoint  | str | -                      | Azure OpenAI エンドポイント URL |
| api_key         | str | -                      | Azure OpenAI API キー           |
| deployment_name | str | -                      | デプロイメント名（モデル名）    |
| api_version     | str | `"2025-04-01-preview"` | API版                           |

#### 戻り値

```python
str | None
```

- **成功時:** LLM からの分析結果テキスト
- **失敗時:** エラーメッセージ（`"OpenAI APIエラー: ..."` 形式）

#### API 呼び出し仕様

```python
client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "system",
            "content": "あなたはコールセンターの優秀なアナリスト..."
        },
        {
            "role": "user",
            "content": prompt  # create_analysis_prompt() の出力
        }
    ],
    temperature=0.7,
    max_completion_tokens=16384,
)
```

#### 前処理

- `azure_endpoint` の末尾 `/` は自動的に削除

#### 例外処理

| エラー         | 返却値                       |
| -------------- | ---------------------------- |
| 認証失敗       | `"OpenAI APIエラー: <詳細>"` |
| API制限        | `"OpenAI APIエラー: <詳細>"` |
| デプロイ名不正 | `"OpenAI APIエラー: <詳細>"` |
| 内部エラー     | `"OpenAI APIエラー: <詳細>"` |

#### 使用例

```python
from services.llm import analyze_with_openai

result = analyze_with_openai(
    transcription="お客様のご質問は...",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-api-key",
    deployment_name="gpt-4",
)

if result.startswith("OpenAI APIエラー"):
    print("エラー:", result)
else:
    print("分析結果:\n", result)
```

---

## モデル: AnalysisResult

### クラス定義

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AnalysisResult:
    filename: str
    main_intent: str
    summary: str
    question: str
    answer: str
    details: str
    transcription: str
    audio_file: Optional[object] = None
    error: Optional[str] = None
```

### フィールド説明

| フィールド名    | 型     | 説明                                                          |
| --------------- | ------ | ------------------------------------------------------------- |
| `filename`      | str    | オリジナルのファイル名                                        |
| `main_intent`   | str    | 主要インテント（前処理結果から抽出）                          |
| `summary`       | str    | 通話要約                                                      |
| `question`      | str    | 顧客の質問内容                                                |
| `answer`        | str    | オペレーターの回答内容                                        |
| `details`       | str    | LLM 出力の全文（詳細分析）                                    |
| `transcription` | str    | Azure Speech の文字起こし全文                                 |
| `audio_file`    | object | Streamlit 成上書UploadedFile オブジェクト（音声プレイヤー用） |
| `error`         | str    | エラーメッセージ（成功時は None）                             |

### メソッド

#### `to_dict() -> dict`

テーブル表示用に辞書に変換

```python
result = AnalysisResult(...)
table_data = result.to_dict()
# {
#     "ファイル名": "sample.wav",
#     "主要インテント": "解約",
#     "分析結果": "料金に不満があるため... (先頭100文字)"
# }
```

### 使用例

```python
from models import AnalysisResult

analysis = AnalysisResult(
    filename="call_001.wav",
    main_intent="料金照会",
    summary="顧客が月額料金を確認したい",
    question="今月の料金はいくらですか",
    answer="本日の課金は¥1,000です",
    details="全文のLLM分析結果...",
    transcription="お忙しいところ...",
    audio_file=uploaded_file_object,
)

# テーブル表示用
print(analysis.to_dict())

# エラー情報
if analysis.error:
    print(f"❌ {analysis.error}")
else:
    print(f"✅ {analysis.main_intent}")
```

---

## UI Streamlit 関数

### `get_env_variables() -> dict`

環境変数を取得・検証

#### 検証項目

- `SPEECH_KEY`
- `SPEECH_REGION`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`

欠落時は `st.error()` で표示して実行止止

#### 戻り値

```python
{
    "speech_key": str,
    "speech_region": str,
    "azure_endpoint": str,
    "api_key": str,
    "deployment_name": str,
    "api_version": str,  # デフォルト: "2025-04-01-preview"
}
```

---

### `validate_files(uploaded_files: List) -> List`

アップロード されたファイルを検証

#### チェック内容

1. **拡張子**: `.wav` のみ
2. **ファイルサイズ**: 最大 200MB

#### 戻り値

```python
List[UploadedFile]  # 有効なファイルのみ
```

#### 副作用

- `st.warning()` で不正ファイルの理由を表示

---

### `analyze_audio_file(...) -> AnalysisResult`

単一ファイルの完全分析パイプライン

#### パラメータ

```python
uploaded_file       # Streamlit UploadedFile
env_vars            # get_env_variables() の戻り値
progress_placeholder  # st.progress()
status_placeholder   # st.empty()
index               # ファイル番号
total               # 総ファイル数
```

#### 処理

1. 一時ファイルに保存
2. `speech_to_text()` 呼び出し
3. `analyze_with_openai()` 呼び出し
4. `parse_analysis_result()` で結果構造化
5. `AnalysisResult` オブジェクト生成
6. 一時ファイル削除（finally）

#### 戻り値

```python
AnalysisResult
```

エラーがあれば `error` フィールドに格納

---

## 環境変数リファレンス

### 必須

| 変数名                         | 例                              | 説明                        |
| ------------------------------ | ------------------------------- | --------------------------- |
| `SPEECH_KEY`                   | `abcd1234...`                   | Azure Speech API キー       |
| `SPEECH_REGION`                | `japaneast`                     | Speech リソースのリージョン |
| `AZURE_OPENAI_ENDPOINT`        | `https://res.openai.azure.com/` | OpenAI エンドポイント       |
| `AZURE_OPENAI_API_KEY`         | `xyz789...`                     | OpenAI API キー             |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4-turbo`                   | デプロイ名                  |

### オプション

| 変数名                     | デフォルト           | 説明          |
| -------------------------- | -------------------- | ------------- |
| `AZURE_OPENAI_API_VERSION` | `2025-04-01-preview` | OpenAI API 版 |

---

**最終更新:** 2026年4月
