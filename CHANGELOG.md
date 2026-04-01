# CHANGELOG.md

すべての重要な変更をこのファイルに記録します。

形式は [Keep a Changelog](https://keepachangelog.com/) に従います。

## [1.0.0] - 2026-04-01

### Added

- ✨ **Initial Release**
- 複数 WAV ファイルの一括アップロード機能
- Azure AI Speech による日本語文字起こし機能
- Azure OpenAI によるインテント抽出・分析機能
- 3セクション結果表示（要約、一覧、詳細）
- 音声プレイヤー統合
- ファイルサイズ検証（最大200MB）
- エラーハンドリング

### Dependencies

- streamlit>=1.55.0
- azure-cognitiveservices-speech>=1.48.2
- openai>=2.26.0
- pandas>=2.3.3
- python-dotenv>=1.2.2
- pytest>=7.4.0
- pytest-mock>=3.12.0

### Documentation

- README.md: セットアップ & 使い方
- ARCHITECTURE.md: システム設計書
- API_REFERENCE.md: API 仕様
- IMPLEMENTATION_GUIDE.md: 実装ガイド
- CONTRIBUTING.md: 貢献ガイド

### Testing

- 18個のユニットテスト（すべて PASS）
- parser.py: 7 tests
- llm.py: 11 tests

### Known Issues

- なし（初版リリース）

---

## リリースノートのテンプレート

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added

- 新機能 A
- 新機能 B

### Changed

- 既存機能 A を修正
- 動作改善

### Fixed

- バグ 1 を修正
- バグ 2 を修正

### Deprecated

- 将来廃止予定の機能

### Removed

- 廃止機能

### Security

- セキュリティ脆弱性対応

### Performance

- パフォーマンス向上
```

---

## 今後の予定

### Phase 2 (計画中)

- [ ] 多言語対応（英語、中国語）
- [ ] キーワード抽出機能
- [ ] 感情分析機能
- [ ] 結果のエクスポート（CSV / Excel）
- [ ] 履歴管理機能

### Phase 3 (計画中)

- [ ] REST API 化（FastAPI）
- [ ] 非同期処理（Celery）
- [ ] データベース永続化（PostgreSQL）
- [ ] 並列処理対応
- [ ] Web デプロイメント

### Phase 4 (計画中)

- [ ] 機械学習による精度向上
- [ ] カスタムインテント定義
- [ ] リアルタイム処理
- [ ] ダッシボード機能
- [ ] アラート機能

---

**最終更新:** 2026年4月
