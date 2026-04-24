from pathlib import Path

import pytest

from voice_studio import voices
from tests.conftest import make_wav_bytes


def test_list_presets_returns_seeded_voices(tmp_presets):
    voices.load_presets()
    result = voices.list_presets()
    assert len(result) == 1
    assert result[0].name == "fake_preset"
    assert result[0].source == "preset"
    assert result[0].audio_path.endswith("fake_preset.wav")


def test_add_uploaded_creates_entry(tmp_drive, tmp_presets):
    voices.load_presets()
    wav_bytes = make_wav_bytes(duration_sec=5.0)

    v = voices.add_uploaded(wav_bytes, "mbappe")

    assert v.name == "mbappe"
    assert v.source == "uploaded"
    assert Path(v.audio_path).exists()
    assert v in voices.list_uploaded()


def test_duplicate_name_gets_suffix(tmp_drive, tmp_presets):
    voices.load_presets()
    wav = make_wav_bytes(5.0)

    v1 = voices.add_uploaded(wav, "mbappe")
    v2 = voices.add_uploaded(wav, "mbappe")

    assert v1.name == "mbappe"
    assert v2.name == "mbappe_2"


def test_reject_non_audio_file(tmp_drive, tmp_presets):
    voices.load_presets()
    with pytest.raises(ValueError, match="format audio"):
        voices.add_uploaded(b"not an audio file", "bogus")


def test_reject_too_short_audio(tmp_drive, tmp_presets):
    voices.load_presets()
    wav = make_wav_bytes(duration_sec=1.0)
    with pytest.raises(ValueError, match="trop court"):
        voices.add_uploaded(wav, "short")


def test_reject_too_large_upload(tmp_drive, tmp_presets, monkeypatch):
    voices.load_presets()
    monkeypatch.setattr("voice_studio.config.MAX_UPLOAD_BYTES", 100)
    wav = make_wav_bytes(5.0)
    with pytest.raises(ValueError, match="trop gros"):
        voices.add_uploaded(wav, "huge")


def test_get_by_id_returns_voice(tmp_drive, tmp_presets):
    voices.load_presets()
    v = voices.get_by_id("preset:fake_preset")
    assert v.name == "fake_preset"


def test_get_by_id_missing_raises(tmp_drive, tmp_presets):
    voices.load_presets()
    with pytest.raises(KeyError):
        voices.get_by_id("preset:does_not_exist")


def test_list_all_combines_presets_and_uploaded(tmp_drive, tmp_presets):
    voices.load_presets()
    voices.add_uploaded(make_wav_bytes(5.0), "mbappe")

    all_voices = voices.list_all()
    ids = {v.id for v in all_voices}
    assert "preset:fake_preset" in ids
    assert "uploaded:mbappe" in ids
