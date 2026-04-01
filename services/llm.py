"""
Azure OpenAI service for intent extraction and analysis.
"""

from typing import Optional

from openai import AzureOpenAI


def create_analysis_prompt(transcription: str) -> str:
    """
    Create the prompt for analyzing call transcription.

    Args:
        transcription: The transcribed text from the audio

    Returns:
        The formatted prompt for the LLM
    """
    prompt = f"""以下はコールセンターの通話内容です。客観的かつ簡潔に分析してください。

通話内容:
{transcription}

以下のフォーマットで必ず返してください:

- インテント: [主要インテント（例：解約、料金照会、クレーム、使い方への質問など）]
- 要約: [通話全体の簡単な要約（1-2文）]
- 質問内容: [顧客の質問や要望]
- 回答内容: [オペレーターの対応・回答内容。オペレーターの発言がない場合は「なし」]
- 詳細: [顧客が具体的に何を求めているか、背景情報]
- オペレーターへのアドバイス: [対応時の心構えや提案内容]
"""
    return prompt


def analyze_with_openai(
    transcription: str,
    azure_endpoint: str,
    api_key: str,
    deployment_name: str,
    api_version: str = "2025-04-01-preview",
) -> Optional[str]:
    """
    Analyze transcription using Azure OpenAI.

    Args:
        transcription: The transcribed text
        azure_endpoint: Azure OpenAI endpoint URL
        api_key: Azure OpenAI API key
        deployment_name: Deployment name
        api_version: API version (default: 2025-04-01-preview)

    Returns:
        Analysis result text or None if failed
    """
    try:
        # Ensure endpoint does not end with /
        endpoint = azure_endpoint.rstrip("/")

        # Create Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

        # Create system message
        system_message = "あなたはコールセンターの優秀なアナリスト。客観的かつ簡潔に分析してください。"

        # Create user message
        user_message = create_analysis_prompt(transcription)

        # Call the API
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_completion_tokens=16384,
        )

        # Extract content
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "分析結果が取得できませんでした。"

    except Exception as e:
        return f"OpenAI APIエラー: {str(e)}"
