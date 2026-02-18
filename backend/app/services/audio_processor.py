"""Audio processing pipeline using WhisperX for transcription + speaker diarization."""

import logging

import whisperx

from app.config import settings

logger = logging.getLogger(__name__)


def process_audio(audio_path: str) -> list[dict]:
    """Process an audio file: transcribe and perform speaker diarization.

    Returns a list of segments:
    [
        {
            "speaker": "SPEAKER_00",
            "start": 0.5,
            "end": 3.2,
            "text": "Merhaba, toplantıya başlayalım.",
        },
        ...
    ]
    """
    device = "cuda" if _cuda_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    logger.info("Loading Whisper model: %s (device=%s)", settings.whisper_model, device)
    model = whisperx.load_model(
        settings.whisper_model,
        device,
        compute_type=compute_type,
        language=settings.whisper_language,
    )

    # 1. Transcribe
    logger.info("Transcribing audio: %s", audio_path)
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=16, language=settings.whisper_language)

    # 2. Align whisper output for word-level timestamps
    logger.info("Aligning transcript...")
    model_a, metadata = whisperx.load_align_model(
        language_code=settings.whisper_language, device=device
    )
    result = whisperx.align(
        result["segments"], model_a, metadata, audio, device, return_char_alignments=False
    )

    # 3. Speaker diarization
    logger.info("Performing speaker diarization...")
    diarize_model = whisperx.DiarizationPipeline(
        use_auth_token=settings.hf_token, device=device
    )
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    # 4. Build output segments
    segments = []
    for i, seg in enumerate(result["segments"]):
        segments.append(
            {
                "speaker": seg.get("speaker", f"SPEAKER_{i:02d}"),
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
        )

    logger.info("Processed %d segments", len(segments))
    return segments


def _cuda_available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False
