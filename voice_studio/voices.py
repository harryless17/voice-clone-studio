"""Gestion de la banque de voix (presets + uploadées)."""
from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import soundfile as sf

from voice_studio import config


@dataclass(frozen=True)
class Voice:
    id: str
    name: str
    audio_path: str
    source: Literal["preset", "uploaded"]


_presets: list[Voice] = []


def load_presets() -> None:
    """Scanne config.PRESETS_DIR et remplit la liste des presets."""
    _presets.clear()
    presets_path = Path(config.PRESETS_DIR)
    if not presets_path.is_dir():
        return
    for wav in sorted(presets_path.glob("*.wav")):
        _presets.append(
            Voice(
                id=f"preset:{wav.stem}",
                name=wav.stem,
                audio_path=str(wav),
                source="preset",
            )
        )


def list_presets() -> list[Voice]:
    return list(_presets)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()).strip("_").lower()
    return slug or "voice"


def _unique_name(desired: str) -> str:
    existing = {v.name for v in list_uploaded()}
    if desired not in existing:
        return desired
    i = 2
    while f"{desired}_{i}" in existing:
        i += 1
    return f"{desired}_{i}"


def _format_size(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} Mo"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} Ko"
    return f"{num_bytes} o"


def add_uploaded(audio_bytes: bytes, name: str) -> Voice:
    """Valide et stocke une voix uploadée dans VOICES_DIR."""
    # Validation taille
    if len(audio_bytes) > config.MAX_UPLOAD_BYTES:
        raise ValueError(
            f"Fichier trop gros ({_format_size(len(audio_bytes))}), "
            f"max {_format_size(config.MAX_UPLOAD_BYTES)}"
        )

    # Validation format + durée via soundfile
    try:
        info = sf.info(io.BytesIO(audio_bytes))
    except Exception as e:
        raise ValueError(f"format audio non reconnu: {e}") from e

    duration = info.frames / info.samplerate
    if duration < config.MIN_VOICE_DURATION_SEC:
        raise ValueError(
            f"Audio trop court ({duration:.1f}s), "
            f"minimum {config.MIN_VOICE_DURATION_SEC}s"
        )

    # Résoudre nom unique
    slug = _slugify(name)
    final_name = _unique_name(slug)

    # Écrire
    voices_dir = Path(config.VOICES_DIR)
    voices_dir.mkdir(parents=True, exist_ok=True)
    target = voices_dir / f"{final_name}.wav"
    target.write_bytes(audio_bytes)

    return Voice(
        id=f"uploaded:{final_name}",
        name=final_name,
        audio_path=str(target),
        source="uploaded",
    )


def list_uploaded() -> list[Voice]:
    """Scanne VOICES_DIR et retourne la liste."""
    voices_dir = Path(config.VOICES_DIR)
    if not voices_dir.is_dir():
        return []
    return [
        Voice(
            id=f"uploaded:{wav.stem}",
            name=wav.stem,
            audio_path=str(wav),
            source="uploaded",
        )
        for wav in sorted(voices_dir.glob("*.wav"))
    ]
