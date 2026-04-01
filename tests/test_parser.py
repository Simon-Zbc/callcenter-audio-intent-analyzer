"""
Tests for parser module.
"""

import pytest

from services.parser import parse_analysis_result


class TestParseAnalysisResult:
    """Test cases for parse_analysis_result function."""

    def test_parse_full_format(self):
        """Test parsing when all fields are present."""
        text = """- インテント: 解約
- 要約: 顧客が契約の解約を希望している
- 質問内容: どうしたら契約を解約できるか
- 回答内容: 解約手続きについて説明した
- 詳細: 顧客は料金に不満があるため、契約を解約したいと考えている
- オペレーターへのアドバイス: 解約理由をヒアリングして、改善案を提案することが重要
"""
        result = parse_analysis_result(text)

        assert result["main_intent"] == "解約"
        assert result["summary"] == "顧客が契約の解約を希望している"
        assert result["question"] == "どうしたら契約を解約できるか"
        assert result["answer"] == "解約手続きについて説明した"
        assert result["details"] == "顧客は料金に不満があるため、契約を解約したいと考えている"
        assert result["advice"] == "解約理由をヒアリングして、改善案を提案することが重要"

    def test_parse_partial_format(self):
        """Test parsing when some fields are missing."""
        text = """- インテント: 料金照会
- 要約: 顧客が料金について質問している
- 質問内容: 今月の料金はいくらか
"""
        result = parse_analysis_result(text)

        assert result["main_intent"] == "料金照会"
        assert result["summary"] == "顧客が料金について質問している"
        assert result["question"] == "今月の料金はいくらか"
        assert result["answer"] == "不明"
        assert result["details"] == "不明"
        assert result["advice"] == "不明"

    def test_parse_without_dashes(self):
        """Test parsing when dashes are missing."""
        text = """インテント: クレーム
要約: 顧客から製品についてのクレームがある
質問内容: 製品の品質について
回答内容: 品質について説明をした
"""
        result = parse_analysis_result(text)

        assert result["main_intent"] == "クレーム"
        assert result["summary"] == "顧客から製品についてのクレームがある"
        assert result["question"] == "製品の品質について"
        assert result["answer"] == "品質について説明をした"

    def test_parse_empty_values(self):
        """Test parsing with empty values."""
        text = """- インテント: 
- 要約: 
- 質問内容: 使い方について
"""
        result = parse_analysis_result(text)

        assert result["main_intent"] == "不明"
        assert result["summary"] == "不明"
        assert result["question"] == "使い方について"

    def test_parse_empty_string(self):
        """Test parsing with empty string."""
        result = parse_analysis_result("")

        assert result["main_intent"] == "不明"
        assert result["summary"] == "不明"
        assert result["question"] == "不明"
        assert result["answer"] == "不明"

    def test_parse_multiline_values(self):
        """Test parsing when values span multiple lines."""
        text = """- インテント: 技術サポート
- 要約: 顧客がシステムの不具合について報告した
多行の値の例です
- 質問内容: システムが起動しない
"""
        result = parse_analysis_result(text)

        # Should extract the first line value
        assert result["main_intent"] == "技術サポート"
        assert result["question"] == "システムが起動しない"

    def test_parse_with_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        text = """  - インテント:   解約  
  - 要約:   顧客が契約解約を希望  
  - 質問内容:   解約方法  
"""
        result = parse_analysis_result(text)

        assert result["main_intent"] == "解約"
        assert result["summary"] == "顧客が契約解約を希望"
        assert result["question"] == "解約方法"
