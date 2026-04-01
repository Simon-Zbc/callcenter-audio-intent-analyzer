# DEVELOPMENT_SETUP.md

開発環境のセットアップ手順を詳細に説明します。

## 前提条件

- **OS**: Windows / macOS / Linux
- **Python**: 3.8 以上（推奨: 3.10+）
- **Git**: インストール済み
- **エディタ**: VS Code / PyCharm など

## ステップ 1: リポジトリのクローン

### SSH キー設定済みの場合

```bash
git clone git@github.com:YOUR_USERNAME/callcenter-audio-intent-analyzer.git
cd callcenter-audio-intent-analyzer
```

### 初回の場合（HTTPS）

```bash
git clone https://github.com/YOUR_USERNAME/callcenter-audio-intent-analyzer.git
cd callcenter-audio-intent-analyzer
```

## ステップ 2: Python 環境構築

### 2.1 Python バージョン確認

```bash
python --version
# 期待: Python 3.8 以上
```

### 2.2 仮想環境を作成

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.3 pip をアップグレード

```bash
pip install --upgrade pip setuptools wheel
```

## ステップ 3: 依存パッケージのインストール

### 本パッケージ

```bash
pip install -r requirements.txt
```

### 開発用パッケージ（推奨）

```bash
pip install pytest pytest-mock black flake8 isort
```

### 全インストール確認

```bash
pip list
```

## ステップ 4: 環境変数の設定

### 4.1 .env ファイル作成

```bash
cp .env.example .env
```

### 4.2 認証情報を入記入

```bash
# エディタで .env を開く
nano .env  # macOS/Linux
# または
notepad .env  # Windows
```

**以下の値を入記入:**

```env
SPEECH_KEY=<Azure Portal から取得>
SPEECH_REGION=japaneast  # 各自のリージョン
AZURE_OPENAI_ENDPOINT=<Azure Portal から取得>
AZURE_OPENAI_API_KEY=<Azure Portal から取得>
AZURE_OPENAI_DEPLOYMENT_NAME=<デプロイ名>
AZURE_OPENAI_API_VERSION=2025-04-01-preview
```

### 4.3 環境変数のロード確認

```python
# Python REPL で確認
python
>>> from dotenv import load_dotenv
>>> import os
>>> load_dotenv()
>>> os.getenv("SPEECH_KEY")
# 出力: your_key_value
```

## ステップ 5: コード品質ツール設定

### 5.1 Black（自動フォーマット）

```bash
# プロジェクト全体をフォーマット
black . --line-length=100

# 特定ファイル
black main.py
```

### 5.2 Flake8（スタイルチェック）

```bash
# チェック実行
flake8 . --max-line-length=100

# 詳細表示
flake8 . --max-line-length=100 --show-source
```

### 5.3 isort（import 整理）

```bash
# import を自動整理
isort . --profile black
```

## ステップ 6: テスト実行

### 6.1 すべてのテスト

```bash
pytest tests/ -v
```

**期待結果:**

```
============================= test session starts =============================
...
============================= 18 passed in X.XXs =============================
```

### 6.2 特定のテストファイル

```bash
pytest tests/test_parser.py -v
pytest tests/test_prompt.py -v
```

### 6.3 カバレッジ確認（オプション）

```bash
pip install pytest-cov
pytest --cov=services tests/
```

## ステップ 7: ローカルで実行

### 7.1 Streamlit アプリ起動

```bash
streamlit run main.py
```

**期待:**

```
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

### 7.2 ブラウザ確認

- `http://localhost:8501` を開く
- UI が表示されることを確認
- ファイルアップロード UI が動作することを確認

### 7.3 テスト実行

1. テスト WAV ファイルを用意（または無音 WAV を生成）
2. ファイルをアップロード
3. 「一括解析を実行する」をクリック
4. 進捗が表示され、結果が出ることを確認

## ステップ 8: IDE 設定（オプション）

### VS Code

#### 拡張機能推奨

```
- Python (Microsoft)
- Pylance
- Black Formatter
- Flake8
```

#### settings.json

```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "linting.flake8Enabled": true,
    "linting.flake8Args": ["--max-line-length=100"]
  }
}
```

### PyCharm

#### コード style 設定

```
Preferences → Editor → Code Style → Python
  • Indent: 4 spaces
  • Line length: 100
  • Wrapping: auto
```

#### テスト実行

```
右クリック → Run pytest in '...'
```

## 常用コマンド

```bash
# 環境有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows

# 環境終了
deactivate

# パッケージ追加
pip install package_name

# 依存関係をロック
pip freeze > requirements.txt

# テスト実行
pytest tests/ -v

# フォーマット
black . && isort .

# Lint チェック
flake8 .

# アプリ起動
streamlit run main.py
```

## トラブルシューティング

### 問題: `ModuleNotFoundError: No module named 'xxx'`

```bash
# 虫環境を確認
pip list

# 再インストール
pip install -r requirements.txt
```

### 問題: `SPEECH_KEY not found`

```bash
# .env ファイルの場所確認
ls -la | grep .env

# .env の内容確認
cat .env

# .env.example と比較
diff .env .env.example
```

### 問題: 仮想環境が有効化されていない

```bash
# 確認方法
which python  # macOS/Linux

# 正: /path/to/venv/bin/python
# 誤: /usr/bin/python

# 再有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

### 問題: Qt/GUI エラー（Streamlit）

```bash
# 回避方法
streamlit run main.py --client.showErrorDetails=false

# または logger 設定
export PYTHONUNBUFFERED=1
streamlit run main.py
```

## デバッグのコツ

### Python REPL でテスト

```python
python
>>> from services.parser import parse_analysis_result
>>> text = "- インテント: テスト\n- 要約: 要約テスト"
>>> result = parse_analysis_result(text)
>>> print(result)
```

### ログ出力

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"DEBUG: value = {value}")
logger.info(f"INFO: processing {file}")
logger.warning(f"WARNING: {message}")
logger.error(f"ERROR: {error}")
```

### デバッガ（PyCharm）

```python
def my_function(param):
    breakpoint()  # ここで停止
    # デバッガで値を確認
    return result
```

## CI/CD セットアップ（将来）

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

---

## まとめ: 開発フロー

```
1. リポジトリクローン
   ↓
2. 仮想環境作成 & 有効化
   ↓
3. 依存パッケージインストール
   ↓
4. .env 設定
   ↓
5. テスト実行（確認）
   ↓
6. ローカル実行
   ↓
7. コード修正・機能開発
   ↓
8. テスト追加・実行
   ↓
9. フォーマット & Lint
   ↓
10. コミット & PR
```

---

**最終更新:** 2026年4月

困ったときは CONTRIBUTING.md も参照してください。
