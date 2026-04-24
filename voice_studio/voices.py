"""Gestion de la banque de voix (presets + uploadées)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

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
