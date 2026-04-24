"""Wrapper autour de Chatterbox Multilingual TTS (singleton + génération).

Chatterbox (Resemble AI) est le modèle TTS SOTA open-source en 2026,
classé 9-10/10 en qualité FR, license MIT, zero-shot voice cloning.
Doc : https://github.com/resemble-ai/chatterbox
"""
from __future__ import annotations

import io
import threading
from typing import Any

import soundfile as sf

from voice_studio import config


_model: Any = None
_lock = threading.Lock()


def _load_model() -> Any:
    """Charge Chatterbox Multilingual une seule fois (thread-safe)."""
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is None:
            import torch
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # type: ignore
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    return _model


def generate(
    ref_audio_path: str,
    text: str,
    language: str = "fr",
    speed: float = 1.0,
) -> bytes:
    """Génère un WAV (bytes) avec la voix de ref_audio_path disant text.

    Parameters
    ----------
    speed : float
        Multiplicateur de vitesse appliqué en post-process. 1.0 = naturel,
        < 1.0 = ralenti, > 1.0 = accéléré. Préserve le pitch (time-stretch).

    Raises
    ------
    RuntimeError
        Si l'inférence échoue (OOM, modèle indisponible, etc.)
    """
    if language != config.LANGUAGE:
        raise RuntimeError(f"Langue non supportée en v1: {language}")

    model = _load_model()
    try:
        wav = model.generate(
            text,
            language_id=language,
            audio_prompt_path=ref_audio_path,
        )
    except Exception as e:
        raise RuntimeError(f"Inférence TTS échouée: {e}") from e

    # Tensor PyTorch → numpy mono 1D
    wav_np = wav.squeeze().detach().cpu().numpy()

    # Time-stretch : `rate > 1` accélère, `rate < 1` ralentit
    # librosa utilise un phase vocoder qui préserve le pitch
    if speed != 1.0 and 0.1 < speed < 3.0:
        import librosa  # import lazy (gros package)
        wav_np = librosa.effects.time_stretch(wav_np, rate=speed)

    buf = io.BytesIO()
    sf.write(buf, wav_np, model.sr, format="WAV")
    return buf.getvalue()
