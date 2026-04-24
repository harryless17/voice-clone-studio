"""Intégration Google Drive (mount + save)."""
from __future__ import annotations

from pathlib import Path

from voice_studio import config


def mount() -> None:
    """Mount /content/drive via google.colab. Idempotent.

    Ne fait rien hors Colab (utile pour les tests).
    """
    try:
        from google.colab import drive as colab_drive  # type: ignore
    except ImportError:
        return
    colab_drive.mount("/content/drive")
    ensure_dirs()


def ensure_dirs() -> None:
    """Crée OUTPUTS_DIR, VOICES_DIR, CACHE_DIR si absents."""
    for d in (config.OUTPUTS_DIR, config.VOICES_DIR, config.CACHE_DIR):
        Path(d).mkdir(parents=True, exist_ok=True)


def save_output(audio_bytes: bytes, filename: str) -> str:
    """Pousse audio_bytes dans OUTPUTS_DIR/filename, retourne le path."""
    ensure_dirs()
    target = Path(config.OUTPUTS_DIR) / filename
    target.write_bytes(audio_bytes)
    return str(target)
