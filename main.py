"""
Streamlit app for call center audio intent analysis.
"""

import os
import tempfile
from typing import List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from models import AnalysisResult
from services.llm import analyze_with_openai
from services.parser import parse_analysis_result
from services.speech import speech_to_text

# Load environment variables
load_dotenv()

# Configuration
MAX_FILE_SIZE_MB = 200
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Set page config
st.set_page_config(
    page_title="コールセンター音声インテント抽出",
    page_icon="📞",
    layout="wide",
)


def get_env_variables():
    """Get and validate required environment variables."""
    required_vars = [
        "SPEECH_KEY",
        "SPEECH_REGION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        st.error(
            f"❌ 環境変数が不足しています: {', '.join(missing_vars)}\n"
            f".env ファイルを確認してください。"
        )
        st.stop()

    return {
        "speech_key": os.getenv("SPEECH_KEY"),
        "speech_region": os.getenv("SPEECH_REGION"),
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    }


def validate_files(uploaded_files: List) -> List:
    """Validate uploaded files and filter invalid ones."""
    valid_files = []
    errors = []

    for file in uploaded_files:
        # Check file extension
        if not file.name.lower().endswith(".wav"):
            errors.append(f"❌ {file.name}: .wav ファイルのみ対応しています")
            continue

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE_BYTES:
            errors.append(
                f"❌ {file.name}: ファイルサイズが大きすぎます "
                f"(最大{MAX_FILE_SIZE_MB}MB, 実際: {file_size / (1024*1024):.1f}MB)"
            )
            continue

        valid_files.append(file)

    for error in errors:
        st.warning(error)

    return valid_files


def analyze_audio_file(
    uploaded_file,
    env_vars: dict,
    progress_placeholder,
    status_placeholder,
    index: int,
    total: int,
) -> AnalysisResult:
    """Analyze a single audio file."""
    filename = uploaded_file.name

    # Update status
    status_placeholder.text(f"処理中 ({index}/{total}): {filename}")
    progress_placeholder.progress(index / total)

    # Save to temporary file
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_file = tmp.name

        # Speech to text
        transcription = speech_to_text(
            temp_file,
            env_vars["speech_key"],
            env_vars["speech_region"],
        )

        if not transcription or transcription.startswith("音声認識エラー") or transcription.startswith("音声が認識できません"):
            return AnalysisResult(
                filename=filename,
                main_intent="不明",
                summary="不明",
                question="不明",
                answer="不明",
                details="不明",
                transcription=transcription or "不明",
                audio_file=uploaded_file,
                error=transcription or "音声認識に失敗しました",
            )

        # Analyze with OpenAI
        analysis_text = analyze_with_openai(
            transcription,
            env_vars["azure_endpoint"],
            env_vars["api_key"],
            env_vars["deployment_name"],
            env_vars["api_version"],
        )

        if not analysis_text or analysis_text.startswith("OpenAI APIエラー"):
            return AnalysisResult(
                filename=filename,
                main_intent="不明",
                summary="不明",
                question="不明",
                answer="不明",
                details="不明",
                transcription=transcription,
                audio_file=uploaded_file,
                error=analysis_text or "分析に失敗しました",
            )

        # Parse results
        parsed = parse_analysis_result(analysis_text)

        return AnalysisResult(
            filename=filename,
            main_intent=parsed["main_intent"],
            summary=parsed["summary"],
            question=parsed["question"],
            answer=parsed["answer"],
            details=analysis_text,
            transcription=transcription,
            audio_file=uploaded_file,
        )

    except Exception as e:
        return AnalysisResult(
            filename=filename,
            main_intent="不明",
            summary="不明",
            question="不明",
            answer="不明",
            details="不明",
            transcription="不明",
            audio_file=uploaded_file,
            error=f"予期しないエラー: {str(e)}",
        )
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass


def main():
    """Main Streamlit app."""

    # Header
    st.markdown("# 📞 コールセンター音声 インテント抽出")
    st.markdown(
        "複数のWAV形式の音声ファイルを一括でアップロードし、分析・比較できます。"
    )

    # Get environment variables
    env_vars = get_env_variables()

    # File uploader
    st.markdown("## ファイルアップロード")
    uploaded_files = st.file_uploader(
        "音声ファイル（.wav）をアップロードしてください（複数選択可）",
        type=["wav"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        # Validate files
        valid_files = validate_files(uploaded_files)

        if valid_files:
            st.info(f"✅ {len(valid_files)}件のファイルが選択されています。")
        else:
            st.warning("有効なファイルがありません。")
            st.stop()
    else:
        st.info("ファイルを選択してください。")
        st.stop()

    # Analysis button
    if st.button("一括解析を実行する", type="primary", use_container_width=True):
        # Initialize progress placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Analyze all files
        analysis_results: List[AnalysisResult] = []

        for idx, uploaded_file in enumerate(valid_files, 1):
            result = analyze_audio_file(
                uploaded_file,
                env_vars,
                progress_bar,
                status_text,
                idx,
                len(valid_files),
            )
            analysis_results.append(result)

        # Complete
        progress_bar.progress(1.0)
        st.success("✅ すべてのファイルの解析が完了しました！")

        # Store results in session state
        st.session_state.analysis_results = analysis_results

    # Display results if available
    if hasattr(st.session_state, "analysis_results") and st.session_state.analysis_results:
        results = st.session_state.analysis_results

        # Section 1: Summary
        st.markdown("## 📋 各音声の要約")
        for result in results:
            with st.container():
                st.markdown(f"### {result.filename}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**要約**")
                    st.write(result.summary)
                with col2:
                    st.markdown("**質問内容**")
                    st.write(result.question)
                with col3:
                    st.markdown("**回答内容**")
                    st.write(result.answer)

                if result.error:
                    st.error(f"⚠️ {result.error}")

        # Section 2: Intent list
        st.markdown("## 📊 インテント抽出結果一覧")

        df_data = [result.to_dict() for result in results]
        df = pd.DataFrame(df_data)

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
        )

        # Section 3: Detailed analysis
        st.markdown("## 📄 各音声の詳細分析")

        for result in results:
            with st.expander(
                f"📁 {result.filename} (インテント: {result.main_intent})"
            ):
                # Audio player
                if result.audio_file:
                    st.audio(result.audio_file)

                # Two columns: Transcription and Analysis
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown("### 📝 文字起こし結果")
                    st.text_area(
                        "文字起こし",
                        value=result.transcription,
                        height=300,
                        disabled=True,
                        label_visibility="collapsed",
                    )

                with col_right:
                    st.markdown("### 💡 分析結果")
                    st.text_area(
                        "分析結果",
                        value=result.details,
                        height=300,
                        disabled=True,
                        label_visibility="collapsed",
                    )


if __name__ == "__main__":
    main()
