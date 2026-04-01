"""
Parser for LLM analysis results.
Extracts intent, summary, question, answer from LLM output text.
"""

from typing import Dict


def parse_analysis_result(text: str) -> Dict[str, str]:
    """
    Parse the LLM analysis result text and extract structured fields.

    Expected format:
    - インテント: [intent]
    - 要約: [summary]
    - 質問内容: [question]
    - 回答内容: [answer]
    - 詳細: [details]
    - オペレーターへのアドバイス: [advice]

    Args:
        text: Raw text from LLM output

    Returns:
        Dictionary with keys: main_intent, summary, question, answer, details, advice
        Missing fields default to "不明"
    """
    result = {
        "main_intent": "不明",
        "summary": "不明",
        "question": "不明",
        "answer": "不明",
        "details": "不明",
        "advice": "不明",
    }

    lines = text.split("\n")

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        if line_stripped.startswith("- インテント:") or line_stripped.startswith("インテント:"):
            value = line_stripped.replace(
                "- インテント:", "").replace("インテント:", "").strip()
            if value:
                result["main_intent"] = value

        elif line_stripped.startswith("- 要約:") or line_stripped.startswith("要約:"):
            value = line_stripped.replace(
                "- 要約:", "").replace("要約:", "").strip()
            if value:
                result["summary"] = value

        elif line_stripped.startswith("- 質問内容:") or line_stripped.startswith("質問内容:"):
            value = line_stripped.replace(
                "- 質問内容:", "").replace("質問内容:", "").strip()
            if value:
                result["question"] = value

        elif line_stripped.startswith("- 回答内容:") or line_stripped.startswith("回答内容:"):
            value = line_stripped.replace(
                "- 回答内容:", "").replace("回答内容:", "").strip()
            if value:
                result["answer"] = value

        elif line_stripped.startswith("- 詳細:") or line_stripped.startswith("詳細:"):
            value = line_stripped.replace(
                "- 詳細:", "").replace("詳細:", "").strip()
            if value:
                result["details"] = value

        elif line_stripped.startswith("- オペレーターへのアドバイス:") or line_stripped.startswith("オペレーターへのアドバイス:"):
            value = line_stripped.replace(
                "- オペレーターへのアドバイス:", "").replace("オペレーターへのアドバイス:", "").strip()
            if value:
                result["advice"] = value

    return result
