from voice_studio import voices


def test_list_presets_returns_seeded_voices(tmp_presets):
    voices.load_presets()
    result = voices.list_presets()
    assert len(result) == 1
    assert result[0].name == "fake_preset"
    assert result[0].source == "preset"
    assert result[0].audio_path.endswith("fake_preset.wav")
