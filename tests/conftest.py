"""Fixtures partagées entre tests."""
import numpy as np
import pytest
import soundfile as sf


@pytest.fixture
def tmp_drive(monkeypatch, tmp_path):
    """Redirige DRIVE_ROOT vers un dossier temporaire pour les tests."""
    drive_root = tmp_path / "drive"
    drive_root.mkdir()
    monkeypatch.setattr("voice_studio.config.DRIVE_ROOT", str(drive_root))
    monkeypatch.setattr("voice_studio.config.OUTPUTS_DIR", str(drive_root / "outputs"))
    monkeypatch.setattr("voice_studio.config.VOICES_DIR", str(drive_root / "voices"))
    monkeypatch.setattr("voice_studio.config.CACHE_DIR", str(drive_root / ".cache"))
    return drive_root


@pytest.fixture
def tmp_presets(monkeypatch, tmp_path):
    """Dossier de presets temporaire avec 1 sample généré."""
    presets = tmp_path / "voices"
    presets.mkdir()
    # génère 5s de silence comme fake preset
    sample_rate = 22050
    audio = np.zeros(5 * sample_rate, dtype=np.float32)
    sf.write(str(presets / "fake_preset.wav"), audio, sample_rate)
    monkeypatch.setattr("voice_studio.config.PRESETS_DIR", str(presets))
    return presets


def make_wav_bytes(duration_sec: float = 5.0, sample_rate: int = 22050) -> bytes:
    """Génère des bytes WAV valides pour les tests d'upload."""
    import io
    audio = np.zeros(int(duration_sec * sample_rate), dtype=np.float32)
    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV")
    return buf.getvalue()


def pytest_collection_modifyitems(config, items):
    """Skip les tests GPU si torch.cuda n'est pas dispo."""
    try:
        import torch
        has_gpu = torch.cuda.is_available()
    except ImportError:
        has_gpu = False

    if not has_gpu:
        skip_gpu = pytest.mark.skip(reason="GPU non disponible")
        for item in items:
            if "gpu" in item.keywords:
                item.add_marker(skip_gpu)
