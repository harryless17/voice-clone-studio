from pathlib import Path

import pytest

from voice_studio import drive


def test_save_output_writes_to_outputs_dir(tmp_drive):
    drive.ensure_dirs()
    path = drive.save_output(b"\x00" * 100, "test.wav")
    assert Path(path).exists()
    assert Path(path).read_bytes() == b"\x00" * 100
    assert "outputs" in path


def test_ensure_dirs_creates_all(tmp_drive):
    drive.ensure_dirs()
    assert (tmp_drive / "outputs").is_dir()
    assert (tmp_drive / "voices").is_dir()
    assert (tmp_drive / ".cache").is_dir()
