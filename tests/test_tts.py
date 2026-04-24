import io

import pytest
import soundfile as sf

from voice_studio import tts


pytestmark = pytest.mark.gpu


@pytest.fixture
def ref_audio(tmp_path):
    """Génère un ref audio bidon de 10s pour le test."""
    import numpy as np
    audio = np.random.randn(10 * 22050).astype(np.float32) * 0.1
    path = tmp_path / "ref.wav"
    sf.write(str(path), audio, 22050)
    return str(path)


def test_generate_returns_wav_bytes(ref_audio):
    result = tts.generate(ref_audio, "Bonjour tout le monde", language="fr")

    assert isinstance(result, bytes)
    info = sf.info(io.BytesIO(result))
    assert info.samplerate > 0
    assert info.frames > 0


def test_generate_respects_length(ref_audio):
    text = "Un deux trois quatre cinq six sept huit neuf dix"
    result = tts.generate(ref_audio, text, language="fr")

    info = sf.info(io.BytesIO(result))
    duration = info.frames / info.samplerate
    assert 2.0 <= duration <= 10.0
