"""Wrapper autour de F5-TTS (singleton + génération)."""
from __future__ import annotations

import io
import threading
from typing import Any

import soundfile as sf

from voice_studio import config


_model: Any = None
_lock = threading.Lock()


def _load_model() -> Any:
    """Charge F5-TTS une seule fois (thread-safe)."""
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is None:
            # API F5-TTS 1.1.x : F5TTS(model="F5TTS_v1_Base", ...)
            # Voir https://github.com/SWivid/F5-TTS/blob/main/src/f5_tts/api.py
            from f5_tts.api import F5TTS  # type: ignore
            _model = F5TTS(model="F5TTS_v1_Base")
    return _model


def generate(ref_audio_path: str, text: str, language: str = "fr") -> bytes:
    """Génère un WAV (bytes) avec la voix de ref_audio_path disant text.

    Raises
    ------
    RuntimeError
        Si l'inférence échoue (OOM, modèle indisponible, etc.)
    """
    if language != config.LANGUAGE:
        raise RuntimeError(f"Langue non supportée en v1: {language}")

    model = _load_model()
    try:
        wav, sample_rate, _ = model.infer(
            ref_file=ref_audio_path,
            ref_text="",  # F5-TTS détecte automatiquement
            gen_text=text,
            remove_silence=True,
        )
    except Exception as e:
        raise RuntimeError(f"Inférence TTS échouée: {e}") from e

    buf = io.BytesIO()
    sf.write(buf, wav, sample_rate, format="WAV")
    return buf.getvalue()
