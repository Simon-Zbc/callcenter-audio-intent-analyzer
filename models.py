"""
Data models for call center audio analysis.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalysisResult:
    """Represents the analysis result of a single audio file."""

    filename: str
    """The name of the audio file."""

    main_intent: str
    """The main intent extracted from the transcription."""

    summary: str
    """Summary of the entire call."""

    question: str
    """Customer's question or request."""

    answer: str
    """Operator's response (or 'None' if not available)."""

    details: str
    """Detailed analysis (raw LLM output)."""

    transcription: str
    """The full transcription text from Azure Speech."""

    audio_file: Optional[object] = None
    """The uploaded audio file object (Streamlit UploadedFile)."""

    error: Optional[str] = None
    """Error message if analysis failed."""

    def to_dict(self) -> dict:
        """Convert to dictionary for tabular display."""
        return {
            "ファイル名": self.filename,
            "主要インテント": self.main_intent,
            "分析結果": self.details[:100] + "..." if len(self.details) > 100 else self.details,
        }
