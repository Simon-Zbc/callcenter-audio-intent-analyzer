"""
Tests for LLM module.
"""

import pytest
from unittest.mock import patch, MagicMock

from services.llm import create_analysis_prompt, analyze_with_openai


class TestCreateAnalysisPrompt:
    """Test cases for create_analysis_prompt function."""

    def test_prompt_contains_required_fields(self):
        """Test that prompt includes all required output fields."""
        transcription = "お忙しいところありがとうございます。"
        prompt = create_analysis_prompt(transcription)

        # Check that output format fields are mentioned
        assert "インテント:" in prompt
        assert "要約:" in prompt
        assert "質問内容:" in prompt
        assert "回答内容:" in prompt
        assert "詳細:" in prompt
        assert "オペレーターへのアドバイス:" in prompt

    def test_prompt_includes_transcription(self):
        """Test that prompt includes the transcription."""
        transcription = "これはテスト通話です"
        prompt = create_analysis_prompt(transcription)

        assert transcription in prompt

    def test_prompt_has_system_context(self):
        """Test that prompt includes system context for analysis."""
        transcription = "テスト通話"
        prompt = create_analysis_prompt(transcription)

        # Check for context markers
        assert "コールセンター" in prompt or "通話内容" in prompt
        assert "分析" in prompt

    def test_prompt_is_not_empty(self):
        """Test that prompt is generated and not empty."""
        transcription = ""
        prompt = create_analysis_prompt(transcription)

        assert prompt is not None
        assert len(prompt) > 0

    def test_prompt_format_is_structured(self):
        """Test that prompt output format is structured with dashes."""
        transcription = "テスト"
        prompt = create_analysis_prompt(transcription)

        # Check for structured format with dashes
        assert "- " in prompt


class TestAnalyzeWithOpenAI:
    """Test cases for analyze_with_openai function."""

    @patch("services.llm.AzureOpenAI")
    def test_successful_analysis(self, mock_azure_openai):
        """Test successful analysis with mocked API."""
        # Setup mock
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "- インテント: テスト\n"
            "- 要約: テスト要約\n"
            "- 質問内容: テスト質問\n"
            "- 回答内容: テスト回答"
        )
        mock_client.chat.completions.create.return_value = mock_response

        # Call function
        result = analyze_with_openai(
            "テスト通話",
            "https://test.openai.azure.com/",
            "test-key",
            "test-deployment",
        )

        # Verify
        assert result is not None
        assert "インテント" in result
        assert mock_client.chat.completions.create.called

    @patch("services.llm.AzureOpenAI")
    def test_api_error_handling(self, mock_azure_openai):
        """Test error handling when API fails."""
        # Setup mock to raise exception
        mock_azure_openai.side_effect = Exception("API Error")

        # Call function
        result = analyze_with_openai(
            "テスト通話",
            "https://test.openai.azure.com/",
            "test-key",
            "test-deployment",
        )

        # Verify error handling
        assert result is not None
        assert "エラー" in result

    @patch("services.llm.AzureOpenAI")
    def test_endpoint_stripping(self, mock_azure_openai):
        """Test that endpoint trailing slash is stripped."""
        # Setup mock
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "テスト"
        mock_client.chat.completions.create.return_value = mock_response

        # Call with trailing slash
        analyze_with_openai(
            "テスト",
            "https://test.openai.azure.com/",
            "test-key",
            "test-deployment",
        )

        # Verify endpoint was stripped
        call_args = mock_azure_openai.call_args
        assert call_args.kwargs["azure_endpoint"] == "https://test.openai.azure.com"

    @patch("services.llm.AzureOpenAI")
    def test_default_api_version(self, mock_azure_openai):
        """Test that default API version is used."""
        # Setup mock
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "テスト"
        mock_client.chat.completions.create.return_value = mock_response

        # Call without api_version
        analyze_with_openai(
            "テスト",
            "https://test.openai.azure.com",
            "test-key",
            "test-deployment",
        )

        # Verify default api_version was used
        call_args = mock_azure_openai.call_args
        assert call_args.kwargs["api_version"] == "2025-04-01-preview"

    @patch("services.llm.AzureOpenAI")
    def test_max_completion_tokens_set(self, mock_azure_openai):
        """Test that max_completion_tokens is set to sufficient value."""
        # Setup mock
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "テスト"
        mock_client.chat.completions.create.return_value = mock_response

        # Call function
        analyze_with_openai(
            "テスト通話",
            "https://test.openai.azure.com",
            "test-key",
            "test-deployment",
        )

        # Verify max_completion_tokens
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["max_completion_tokens"] >= 16384

    @patch("services.llm.AzureOpenAI")
    def test_empty_response_handling(self, mock_azure_openai):
        """Test handling when API returns empty choices."""
        # Setup mock with empty choices
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        # Call function
        result = analyze_with_openai(
            "テスト通話",
            "https://test.openai.azure.com",
            "test-key",
            "test-deployment",
        )

        # Verify fallback behavior
        assert result is not None
        assert "取得できません" in result or len(result) > 0
