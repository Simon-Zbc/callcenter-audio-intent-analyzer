"""
Azure AI Speech service for Japanese transcription.
"""

import threading
import time
from typing import Optional

import azure.cognitiveservices.speech as speechsdk


def speech_to_text(audio_path: str, speech_key: str, speech_region: str) -> Optional[str]:
    """
    Convert audio file to text using Azure AI Speech.

    Args:
        audio_path: Path to the WAV file
        speech_key: Azure Speech API key
        speech_region: Azure Speech region

    Returns:
        Transcribed text or None if recognition failed
    """
    try:
        # Create a speech configuration
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region,
        )
        speech_config.speech_recognition_language = "ja-JP"

        # Create an audio configuration
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)

        # Create a recognizer
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        # Collect results
        results = []
        session_stopped_event = threading.Event()

        def on_recognized(evt):
            """Handle recognized event."""
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                results.append(evt.result.text)

        def on_session_stopped(evt):
            """Handle session stopped event."""
            session_stopped_event.set()

        def on_canceled(evt):
            """Handle cancellation event."""
            session_stopped_event.set()

        # Connect callbacks
        recognizer.recognized.connect(on_recognized)
        recognizer.session_stopped.connect(on_session_stopped)
        recognizer.canceled.connect(on_canceled)

        # Start continuous recognition
        recognizer.start_continuous_recognition()

        # Wait for completion (with timeout)
        timeout = 300  # 5 minutes max
        if not session_stopped_event.wait(timeout=timeout):
            # Timeout occurred
            recognizer.stop_continuous_recognition()

        # Combine all results
        if results:
            return "".join(results)
        else:
            return "音声が認識できませんでした。または無音でした。"

    except Exception as e:
        return f"音声認識エラー: {str(e)}"
