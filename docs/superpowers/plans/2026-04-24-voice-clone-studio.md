# Voice Clone Studio — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Livrer un outil de voice cloning TTS utilisable via Google Colab, permettant à un utilisateur non-technique de générer des audios TikTok avec une voix clonée à partir d'un échantillon audio et de texte français.

**Architecture:** Notebook Colab façade minimaliste (5 cellules) qui clone un repo GitHub public et importe un package Python `voice_studio/` contenant toute la logique. F5-TTS en singleton pour l'inférence, Gradio Blocks pour l'UI, Google Drive pour la persistence. Accès protégé par mot de passe lu depuis une variable d'environnement.

**Tech Stack:** Python 3.10+, F5-TTS (HuggingFace `SWivid/F5-TTS`), Gradio ≥ 5.0, soundfile, pytest, Google Colab runtime.

**Working directory:** `~/Bureau/voice-clone-studio/` (git initialisé, branch `main`)

**Spec source:** `docs/superpowers/specs/2026-04-24-voice-cloning-tiktok-design.md`

---

## Task 1: Project skeleton (gitignore, requirements, README stub)

Poser les fondations pour que les commits suivants soient propres.

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `README.md`

- [ ] **Step 1: Créer `.gitignore`**

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Secrets & local env
.env
.env.local

# Notebook outputs (on commit le .ipynb avec outputs vidés)
.ipynb_checkpoints/

# Samples audio lourds stockés en local (les petits samples < 5 Mo restent versionnés)
*.mp3
*.m4a
voices/*.large.wav

# Caches F5-TTS locaux
.cache/
models/
```

- [ ] **Step 2: Créer `requirements.txt`**

```txt
# Core
gradio>=5.0
soundfile>=0.12
numpy>=1.26

# TTS
f5-tts>=0.3

# Testing (dev only, mais pas grave de l'avoir dans Colab)
pytest>=8.0
```

- [ ] **Step 3: Créer un `README.md` stub**

```markdown
# Voice Clone Studio

Outil de TTS avec voice cloning français, pensé pour un usage TikTok.
Tourne dans Google Colab, interface Gradio, aucune installation locale nécessaire.

## Lancer le notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/USER/voice-clone-studio/blob/main/notebook.ipynb)

La doc complète sera ajoutée en Task 14.
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore requirements.txt README.md
git commit -m "chore: project skeleton (gitignore, requirements, readme stub)"
```

---

## Task 2: Package `voice_studio/` + `config.py`

Constantes centralisées, point d'entrée du package.

**Files:**
- Create: `voice_studio/__init__.py`
- Create: `voice_studio/config.py`

- [ ] **Step 1: Créer `voice_studio/__init__.py` (vide)**

```python
"""Voice Clone Studio — package principal."""
```

- [ ] **Step 2: Créer `voice_studio/config.py`**

```python
"""Constantes centralisées pour Voice Clone Studio."""
import os

# --- Auth ---
GRADIO_USERNAME: str = "friend"
GRADIO_PASSWORD: str = os.environ.get("VOICE_STUDIO_PASSWORD", "")

# --- Chemins Drive (valides quand le Drive est monté dans Colab) ---
DRIVE_ROOT: str = "/content/drive/MyDrive/VoiceClone"
OUTPUTS_DIR: str = f"{DRIVE_ROOT}/outputs"
VOICES_DIR: str = f"{DRIVE_ROOT}/voices"
CACHE_DIR: str = f"{DRIVE_ROOT}/.cache"

# --- Chemins repo ---
PRESETS_DIR: str = "voices"  # relatif au working dir du notebook

# --- Limites ---
MAX_TEXT_LENGTH: int = 500
MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024  # 50 Mo
MIN_VOICE_DURATION_SEC: float = 3.0

# --- Config TTS ---
LANGUAGE: str = "fr"
```

- [ ] **Step 3: Smoke test local**

```bash
cd ~/Bureau/voice-clone-studio
python -c "from voice_studio import config; print(config.MAX_TEXT_LENGTH)"
```

Expected: `500`

- [ ] **Step 4: Commit**

```bash
git add voice_studio/__init__.py voice_studio/config.py
git commit -m "feat(config): package skeleton + constantes centralisées"
```

---

## Task 3: Infra tests

Poser pytest avec des fixtures partagées.

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `pytest.ini`

- [ ] **Step 1: Créer `tests/__init__.py` (vide)**

- [ ] **Step 2: Créer `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    gpu: marque les tests qui requièrent une GPU (F5-TTS)
```

- [ ] **Step 3: Créer `tests/conftest.py`**

```python
"""Fixtures partagées entre tests."""
import os
import tempfile
from pathlib import Path

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
```

- [ ] **Step 4: Vérifier que pytest démarre sans tests**

```bash
cd ~/Bureau/voice-clone-studio
pip install -q pytest soundfile numpy
pytest
```

Expected: `no tests ran in 0.Xs` (pas d'erreur de collection)

- [ ] **Step 5: Commit**

```bash
git add tests/__init__.py tests/conftest.py pytest.ini
git commit -m "test: infra pytest (fixtures tmp_drive, tmp_presets)"
```

---

## Task 4: `voices.py` — data model + `list_presets()` (TDD)

Dataclass `Voice` et chargement des presets depuis le repo.

**Files:**
- Create: `voice_studio/voices.py`
- Create: `tests/test_voices.py`

- [ ] **Step 1: Écrire le test qui échoue**

Dans `tests/test_voices.py` :

```python
from voice_studio import voices


def test_list_presets_returns_seeded_voices(tmp_presets):
    voices.load_presets()
    result = voices.list_presets()
    assert len(result) == 1
    assert result[0].name == "fake_preset"
    assert result[0].source == "preset"
    assert result[0].audio_path.endswith("fake_preset.wav")
```

- [ ] **Step 2: Run, verify failure**

```bash
pytest tests/test_voices.py::test_list_presets_returns_seeded_voices
```

Expected: FAIL (`ModuleNotFoundError` ou `AttributeError: load_presets`)

- [ ] **Step 3: Implémenter minimum viable**

Dans `voice_studio/voices.py` :

```python
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
```

- [ ] **Step 4: Run, verify pass**

```bash
pytest tests/test_voices.py::test_list_presets_returns_seeded_voices
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add voice_studio/voices.py tests/test_voices.py
git commit -m "feat(voices): Voice dataclass + load_presets() + list_presets()"
```

---

## Task 5: `voices.py` — `add_uploaded()` + validations (TDD)

Upload d'une nouvelle voix avec toutes les règles de validation.

**Files:**
- Modify: `voice_studio/voices.py`
- Modify: `tests/test_voices.py`

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `tests/test_voices.py` :

```python
import pytest
from tests.conftest import make_wav_bytes


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
    wav = make_wav_bytes(duration_sec=1.0)  # < MIN_VOICE_DURATION_SEC (3.0)
    with pytest.raises(ValueError, match="trop court"):
        voices.add_uploaded(wav, "short")


def test_reject_too_large_upload(tmp_drive, tmp_presets, monkeypatch):
    voices.load_presets()
    monkeypatch.setattr("voice_studio.config.MAX_UPLOAD_BYTES", 100)
    wav = make_wav_bytes(5.0)
    with pytest.raises(ValueError, match="trop gros"):
        voices.add_uploaded(wav, "huge")
```

- [ ] **Step 2: Run, verify failures**

```bash
pytest tests/test_voices.py
```

Expected: 5 nouveaux tests FAIL (`add_uploaded` / `list_uploaded` n'existent pas)

- [ ] **Step 3: Implémenter `add_uploaded` + `list_uploaded`**

Ajouter dans `voice_studio/voices.py` :

```python
import io
import re

import soundfile as sf


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


def add_uploaded(audio_bytes: bytes, name: str) -> Voice:
    """Valide et stocke une voix uploadée dans VOICES_DIR."""
    # Validation taille
    if len(audio_bytes) > config.MAX_UPLOAD_BYTES:
        raise ValueError(
            f"Fichier trop gros ({len(audio_bytes) // 1024 // 1024} Mo), "
            f"max {config.MAX_UPLOAD_BYTES // 1024 // 1024} Mo"
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
```

- [ ] **Step 4: Run, verify pass**

```bash
pytest tests/test_voices.py
```

Expected: tous les tests PASS

- [ ] **Step 5: Commit**

```bash
git add voice_studio/voices.py tests/test_voices.py
git commit -m "feat(voices): add_uploaded() + list_uploaded() avec validations"
```

---

## Task 6: `voices.py` — `get_by_id()` + `list_all()` (TDD)

Résolution par ID + liste combinée triée.

**Files:**
- Modify: `voice_studio/voices.py`
- Modify: `tests/test_voices.py`

- [ ] **Step 1: Tests qui échouent**

```python
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
```

- [ ] **Step 2: Run, verify fail**

```bash
pytest tests/test_voices.py
```

- [ ] **Step 3: Implémenter**

Ajouter dans `voice_studio/voices.py` :

```python
def list_all() -> list[Voice]:
    """Presets + uploaded, triés par name."""
    return sorted(list_presets() + list_uploaded(), key=lambda v: v.name)


def get_by_id(voice_id: str) -> Voice:
    for v in list_all():
        if v.id == voice_id:
            return v
    raise KeyError(f"Voice inconnue: {voice_id}")
```

- [ ] **Step 4: Run, verify pass**

```bash
pytest tests/test_voices.py
```

- [ ] **Step 5: Commit**

```bash
git add voice_studio/voices.py tests/test_voices.py
git commit -m "feat(voices): get_by_id() + list_all()"
```

---

## Task 7: `drive.py` — mount + ensure_dirs + save_output

Le mount ne peut pas être testé hors Colab, mais `save_output` est testable.

**Files:**
- Create: `voice_studio/drive.py`
- Modify: `tests/test_voices.py` (ou créer `tests/test_drive.py`)

- [ ] **Step 1: Créer `tests/test_drive.py` avec le test qui échoue**

```python
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
```

- [ ] **Step 2: Run, verify fail**

```bash
pytest tests/test_drive.py
```

- [ ] **Step 3: Implémenter `voice_studio/drive.py`**

```python
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
```

- [ ] **Step 4: Run, verify pass**

```bash
pytest tests/test_drive.py
```

- [ ] **Step 5: Commit**

```bash
git add voice_studio/drive.py tests/test_drive.py
git commit -m "feat(drive): mount + ensure_dirs + save_output"
```

---

## Task 8: `tts.py` — wrapper F5-TTS (skeleton + test GPU-gated)

Wrapper singleton. Le test réel est marqué `@pytest.mark.gpu` et sera skip hors Colab.

**Files:**
- Create: `voice_studio/tts.py`
- Create: `tests/test_tts.py`

- [ ] **Step 1: Ajouter le hook de skip GPU dans `tests/conftest.py`**

Ajouter à la fin de `tests/conftest.py` :

```python
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
```

- [ ] **Step 2: Écrire le test GPU qui échoue**

```python
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
    text = "Un deux trois quatre cinq six sept huit neuf dix"  # ~10 mots
    result = tts.generate(ref_audio, text, language="fr")

    info = sf.info(io.BytesIO(result))
    duration = info.frames / info.samplerate
    assert 2.0 <= duration <= 10.0
```

- [ ] **Step 3: Run — SKIPPED attendu hors Colab**

```bash
pytest tests/test_tts.py
```

Expected hors GPU : les 2 tests sont collectés et marqués `SKIPPED` (GPU non disponible). Sur Colab avec GPU, ils vont FAIL (`tts.generate` pas encore implémenté).

- [ ] **Step 4: Implémenter `voice_studio/tts.py`**

```python
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
            # F5-TTS expose une API simple via l'objet F5TTS
            from f5_tts.api import F5TTS  # type: ignore
            _model = F5TTS(model_type="F5-TTS", vocoder_name="vocos")
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
```

- [ ] **Step 5: Run — la suite complète**

```bash
pytest
```

Expected: `test_tts.py` SKIPPED (2 tests), tous les autres PASS.

- [ ] **Step 6: Commit**

```bash
git add voice_studio/tts.py tests/test_tts.py tests/conftest.py
git commit -m "feat(tts): wrapper F5-TTS singleton + tests GPU-gated"
```

---

## Task 9: `gradio_app.py` — build_app (UI structure, events stub)

Construction de l'UI Gradio, sans logique métier encore câblée.

**Files:**
- Create: `voice_studio/gradio_app.py`

- [ ] **Step 1: Créer `voice_studio/gradio_app.py` — structure UI**

```python
"""Construction de l'UI Gradio Voice Clone Studio."""
from __future__ import annotations

import gradio as gr

from voice_studio import config


CSS = """
.title { text-align: center; font-size: 2em; margin-bottom: 0.2em; }
.subtitle { text-align: center; color: #888; margin-bottom: 1em; }
#generate-btn { min-height: 60px; font-size: 1.1em; }
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="Voice Clone Studio",
        theme=gr.themes.Base(
            primary_hue="rose",
            neutral_hue="slate",
        ),
        css=CSS,
    ) as app:
        gr.HTML("<div class='title'>🎤 Voice Clone Studio</div>")
        gr.HTML("<div class='subtitle'>Génère des audios TikTok avec n'importe quelle voix</div>")

        # --- Bloc Voix ---
        with gr.Group():
            voice_mode = gr.Radio(
                choices=["Préchargée", "Uploader une nouvelle"],
                value="Préchargée",
                label="Voix",
            )
            voice_dropdown = gr.Dropdown(
                choices=[],
                label="Choisir une voix",
                visible=True,
            )
            voice_preview = gr.Audio(
                label="Aperçu (2s)",
                interactive=False,
                visible=True,
            )
            with gr.Group(visible=False) as upload_group:
                upload_name = gr.Textbox(label="Nom de la voix", placeholder="mbappe")
                upload_file = gr.File(label="Fichier audio (10-30s)", file_types=[".wav", ".mp3"])
                gr.Markdown(
                    "ℹ️ **Conseils** : une seule personne, pas de musique/bruit, 10-30 secondes."
                )
                upload_btn = gr.Button("Ajouter à ma banque")
                upload_status = gr.Markdown(visible=False)

        # --- Bloc Texte ---
        with gr.Group():
            text_input = gr.Textbox(
                label=f"Texte à générer (max {config.MAX_TEXT_LENGTH} caractères)",
                lines=4,
                max_lines=8,
                placeholder="Salut les gars, aujourd'hui on va...",
            )
            char_count = gr.Markdown(f"0/{config.MAX_TEXT_LENGTH} caractères")

        # --- Bouton Générer ---
        generate_btn = gr.Button("🎙️ Générer l'audio", variant="primary", elem_id="generate-btn")

        # --- Bloc Résultat ---
        with gr.Group():
            output_audio = gr.Audio(label="Résultat", interactive=False)
            with gr.Row():
                download_btn = gr.DownloadButton("⬇️ Télécharger", visible=False)
                save_drive_btn = gr.Button("💾 Sauver dans Drive", visible=False)
            save_status = gr.Markdown(visible=False)

        # State pour garder les bytes du dernier audio généré
        last_audio_state = gr.State(value=None)
        last_voice_state = gr.State(value=None)

        # Events seront câblés dans Task 10
        app._components = {
            "voice_mode": voice_mode,
            "voice_dropdown": voice_dropdown,
            "voice_preview": voice_preview,
            "upload_group": upload_group,
            "upload_name": upload_name,
            "upload_file": upload_file,
            "upload_btn": upload_btn,
            "upload_status": upload_status,
            "text_input": text_input,
            "char_count": char_count,
            "generate_btn": generate_btn,
            "output_audio": output_audio,
            "download_btn": download_btn,
            "save_drive_btn": save_drive_btn,
            "save_status": save_status,
            "last_audio_state": last_audio_state,
            "last_voice_state": last_voice_state,
        }

    return app


def launch(password: str | None = None) -> None:
    """Lance l'app Gradio avec auth + share public."""
    effective_password = password or config.GRADIO_PASSWORD
    if not effective_password:
        raise RuntimeError(
            "VOICE_STUDIO_PASSWORD non défini. "
            "Ajoute-le via `os.environ['VOICE_STUDIO_PASSWORD'] = '...'` "
            "dans une cellule Colab avant de lancer."
        )

    app = build_app()
    app.launch(
        share=True,
        auth=(config.GRADIO_USERNAME, effective_password),
        auth_message="Entre tes identifiants pour accéder à Voice Clone Studio",
    )
```

- [ ] **Step 2: Smoke test local (pas de launch, juste import)**

```bash
pip install -q gradio
python -c "from voice_studio.gradio_app import build_app; build_app(); print('OK')"
```

Expected: `OK` sans erreur

- [ ] **Step 3: Commit**

```bash
git add voice_studio/gradio_app.py
git commit -m "feat(ui): squelette Gradio Blocks (UI sans events)"
```

---

## Task 10: `gradio_app.py` — câblage des events

Brancher les handlers sur les composants créés en Task 9.

**Files:**
- Modify: `voice_studio/gradio_app.py`

- [ ] **Step 1: Ajouter les handlers**

Remplacer la section `# Events seront câblés dans Task 10` et `app._components = {...}` par :

```python
        # --- Helpers ---
        def _refresh_voice_list():
            from voice_studio import voices as voices_mod
            all_voices = voices_mod.list_all()
            return gr.Dropdown(
                choices=[(v.name, v.id) for v in all_voices],
                value=all_voices[0].id if all_voices else None,
            )

        # --- Event: toggle preset vs upload ---
        def on_mode_change(mode):
            if mode == "Préchargée":
                return gr.Group(visible=False), gr.Dropdown(visible=True), gr.Audio(visible=True)
            return gr.Group(visible=True), gr.Dropdown(visible=False), gr.Audio(visible=False)

        voice_mode.change(
            on_mode_change,
            inputs=[voice_mode],
            outputs=[upload_group, voice_dropdown, voice_preview],
        )

        # --- Event: voice selection → preview ---
        def on_voice_selected(voice_id):
            if not voice_id:
                return None
            from voice_studio import voices as voices_mod
            try:
                v = voices_mod.get_by_id(voice_id)
                return v.audio_path
            except KeyError:
                return None

        voice_dropdown.change(
            on_voice_selected,
            inputs=[voice_dropdown],
            outputs=[voice_preview],
        )

        # --- Event: char count live ---
        def on_text_change(text):
            count = len(text or "")
            color = "red" if count > config.MAX_TEXT_LENGTH else "inherit"
            return f"<span style='color:{color}'>{count}/{config.MAX_TEXT_LENGTH} caractères</span>"

        text_input.change(on_text_change, inputs=[text_input], outputs=[char_count])

        # --- Event: upload ---
        def on_upload(file_obj, name):
            from voice_studio import voices as voices_mod
            if not file_obj:
                return gr.Markdown("⚠️ Choisis un fichier", visible=True), gr.Dropdown()
            if not name or not name.strip():
                return gr.Markdown("⚠️ Donne un nom à la voix", visible=True), gr.Dropdown()
            try:
                with open(file_obj.name, "rb") as f:
                    audio_bytes = f.read()
                v = voices_mod.add_uploaded(audio_bytes, name)
                return (
                    gr.Markdown(f"✅ Voix **{v.name}** ajoutée", visible=True),
                    _refresh_voice_list(),
                )
            except ValueError as e:
                return gr.Markdown(f"❌ {e}", visible=True), gr.Dropdown()

        upload_btn.click(
            on_upload,
            inputs=[upload_file, upload_name],
            outputs=[upload_status, voice_dropdown],
        )

        # --- Event: generate ---
        import re as _re

        def _sanitize_text(text: str) -> tuple[str, float]:
            """Strippe emojis et caractères non-TTS-friendly.

            Retourne (texte_nettoyé, ratio_strippé).
            """
            # Garde lettres (accentuées incl.), chiffres, ponctuation FR courante, espaces
            cleaned = _re.sub(r"[^\w\s.,;:!?'\"\-–—()«»À-ɏ]", "", text, flags=_re.UNICODE)
            original_len = max(len(text), 1)
            stripped = (original_len - len(cleaned)) / original_len
            return cleaned.strip(), stripped

        def on_generate(voice_id, text):
            from voice_studio import tts, voices as voices_mod
            if not text or not text.strip():
                raise gr.Error("Le texte ne peut pas être vide")
            if len(text) > config.MAX_TEXT_LENGTH:
                raise gr.Error(f"Texte trop long ({len(text)}/{config.MAX_TEXT_LENGTH})")
            if not voice_id:
                raise gr.Error("Sélectionne une voix")

            # Sanitization (spec §9 : stripping silencieux, warning si > 20%)
            cleaned_text, stripped_ratio = _sanitize_text(text)
            if not cleaned_text:
                raise gr.Error("Le texte ne contient aucun caractère supporté")
            if stripped_ratio > 0.2:
                gr.Warning(f"⚠️ {int(stripped_ratio * 100)}% du texte a été strippé (emojis / caractères spéciaux)")

            voice = voices_mod.get_by_id(voice_id)
            try:
                audio_bytes = tts.generate(voice.audio_path, cleaned_text, language=config.LANGUAGE)
            except RuntimeError as e:
                raise gr.Error(f"Génération échouée : {e}")

            # Écrit dans un fichier temporaire pour que Gradio puisse le servir
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_bytes)
            tmp.close()

            return (
                tmp.name,                                             # output_audio
                audio_bytes,                                          # last_audio_state
                voice.name,                                           # last_voice_state
                gr.DownloadButton(value=tmp.name, visible=True),      # download_btn
                gr.Button(visible=True),                              # save_drive_btn
            )

        generate_btn.click(
            on_generate,
            inputs=[voice_dropdown, text_input],
            outputs=[
                output_audio,
                last_audio_state,
                last_voice_state,
                download_btn,
                save_drive_btn,
            ],
        )

        # --- Event: save drive ---
        def on_save_drive(audio_bytes, voice_name):
            from datetime import datetime
            from voice_studio import drive as drive_mod

            if not audio_bytes:
                return gr.Markdown("⚠️ Aucun audio à sauver", visible=True)

            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{ts}_{voice_name}.wav"
            # Spec §8 : si le save échoue, remount + retry une fois
            for attempt in (1, 2):
                try:
                    drive_mod.save_output(audio_bytes, filename)
                    return gr.Markdown(f"✅ Sauvé dans Drive : `{filename}`", visible=True)
                except Exception as e:
                    if attempt == 1:
                        try:
                            drive_mod.mount()
                            continue
                        except Exception:
                            pass
                    return gr.Markdown(f"❌ Sauvegarde échouée : {e}", visible=True)

        save_drive_btn.click(
            on_save_drive,
            inputs=[last_audio_state, last_voice_state],
            outputs=[save_status],
        )

        # --- Load initial ---
        app.load(_refresh_voice_list, outputs=[voice_dropdown])
```

Retirer le bloc `app._components = {...}` (plus utile).

- [ ] **Step 2: Smoke test — l'app doit pouvoir se construire**

```bash
python -c "from voice_studio.gradio_app import build_app; build_app(); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Lancer toute la suite de tests (non-régression)**

```bash
pytest
```

Expected: tous PASS (sauf `test_tts` SKIP).

- [ ] **Step 4: Commit**

```bash
git add voice_studio/gradio_app.py
git commit -m "feat(ui): câblage des events Gradio (generate, upload, save drive)"
```

---

## Task 11: `notebook.ipynb` — façade Colab 5 cellules

Le notebook que l'ami va ouvrir.

**Files:**
- Create: `notebook.ipynb`

- [ ] **Step 1: Créer le notebook à la main**

Écrire `notebook.ipynb` avec la structure JSON Jupyter — 5 cellules dans l'ordre :

**Cell 1 — Markdown :**
```markdown
# 🎤 Voice Clone Studio

**Mode d'emploi :**
1. Clique sur **Exécution → Tout exécuter** (ou `Ctrl+F9`)
2. Autorise l'accès à Google Drive quand c'est demandé
3. Attends ~2 minutes la première fois (30s les fois suivantes)
4. Un lien **`https://xxx.gradio.live`** apparaît en bas → clique dessus
5. Entre tes identifiants → utilise l'interface

⚠️ **Important** : ne ferme pas cet onglet tant que tu utilises l'interface.
```

**Cell 2 — Code (install + clone) :**
```python
# Clone + installation des dépendances (~1-2 min la première fois)
import os, subprocess, sys
REPO_URL = "https://github.com/USER/voice-clone-studio.git"
REPO_DIR = "/content/voice-clone-studio"

if not os.path.isdir(REPO_DIR):
    subprocess.run(["git", "clone", REPO_URL, REPO_DIR], check=True)
else:
    subprocess.run(["git", "-C", REPO_DIR, "pull", "--quiet"], check=True)

os.chdir(REPO_DIR)
sys.path.insert(0, REPO_DIR)

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
    check=True,
)
print("✅ Dépendances installées")
```

**Cell 3 — Code (password + mount Drive) :**
```python
# ⚠️ CHANGE CE MOT DE PASSE avant de partager le notebook
import os
os.environ["VOICE_STUDIO_PASSWORD"] = "CHANGE_ME"

# Mount Drive
from voice_studio.drive import mount
mount()
print("✅ Drive monté")
```

**Cell 4 — Code (load presets) :**
```python
from voice_studio.voices import load_presets
load_presets()
print("✅ Voix préchargées chargées")
```

**Cell 5 — Code (launch) :**
```python
from voice_studio.gradio_app import launch
launch()
```

- [ ] **Step 2: Vider les outputs avant commit**

```bash
cd ~/Bureau/voice-clone-studio
# si jupyter installé localement
jupyter nbconvert --clear-output --inplace notebook.ipynb 2>/dev/null || true
```

- [ ] **Step 3: Valider le JSON du notebook**

```bash
python -c "import json; json.load(open('notebook.ipynb')); print('notebook JSON valide')"
```

Expected: `notebook JSON valide`

- [ ] **Step 4: Commit**

```bash
git add notebook.ipynb
git commit -m "feat(notebook): façade Colab 5 cellules"
```

---

## Task 12: Sourcer et ajouter les voix préchargées

Étape manuelle avec instructions claires.

**Files:**
- Create: `voices/README.md`
- Create: `voices/zidane.wav` (manuel)
- Create: `voices/jamel.wav` (manuel)

- [ ] **Step 1: Créer `voices/README.md`**

```markdown
# Voix préchargées

Ce dossier contient les échantillons audio utilisés comme presets par défaut au premier lancement.

## Ajouter un preset

1. Trouver un extrait public (interview YouTube, conférence de presse, émission TV) de 10-30 secondes
2. Extraire l'audio en mono 22050 Hz WAV (outil : `ffmpeg -i input.mp4 -ac 1 -ar 22050 output.wav`)
3. S'assurer : une seule personne parle, pas de musique, pas de bruit de fond
4. Nommer le fichier `<slug>.wav` (minuscules, underscores, pas d'espaces)
5. Committer le fichier dans ce dossier

## Presets actuels

- `zidane.wav` — extrait d'interview post-match (10s)
- `jamel.wav` — extrait de stand-up (12s)

## Considérations légales

Ces échantillons sont inclus à des fins de démonstration (fair-use). L'utilisateur final est responsable de l'usage qu'il fait des clones générés.
```

- [ ] **Step 2: Commit le README sans les audios (à sourcer manuellement)**

```bash
git add voices/README.md
git commit -m "docs(voices): guide pour sourcer les presets"
```

- [ ] **Step 3: [MANUEL — hors plan automatique] Sourcer les 2 fichiers audio**

À faire à la main :
1. Télécharger un extrait YouTube via `yt-dlp`
2. Couper 10-15s avec `ffmpeg -ss 00:01:00 -t 10 -i input.wav -ac 1 -ar 22050 zidane.wav`
3. Vérifier qualité à l'écoute
4. Placer dans `voices/`

```bash
# Exemple commande à adapter
yt-dlp -x --audio-format wav "URL_INTERVIEW"
ffmpeg -ss 00:00:30 -t 12 -i extract.wav -ac 1 -ar 22050 voices/zidane.wav
git add voices/zidane.wav voices/jamel.wav
git commit -m "chore(voices): ajoute presets zidane + jamel"
```

---

## Task 13: README.md final + badge Colab

Documentation utilisateur + mainteneur complète.

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Remplacer le stub par un README complet**

```markdown
# 🎤 Voice Clone Studio

Outil de text-to-speech avec voice cloning français, pensé pour un usage TikTok.
Tourne dans Google Colab (GPU gratuite), interface web Gradio, aucune installation locale.

![Demo](https://img.shields.io/badge/demo-colab-orange)

## Lancer le notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/USER/voice-clone-studio/blob/main/notebook.ipynb)

## Pour l'utilisateur final

1. Clique sur le badge "Open in Colab" ci-dessus
2. Connecte-toi avec ton compte Google
3. Clique sur **Exécution → Tout exécuter** (`Ctrl+F9`)
4. Autorise l'accès Drive au popup
5. Attends le message **"✅ Interface prête → https://xxx.gradio.live"**
6. Clique sur le lien, entre tes identifiants, utilise l'interface

Les audios générés peuvent être téléchargés directement ou sauvés sur ton Drive (`MyDrive/VoiceClone/outputs/`).

## Pour le mainteneur

### Setup initial

```bash
git clone https://github.com/USER/voice-clone-studio.git
cd voice-clone-studio
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest  # tests locaux (les tests GPU sont skip sans Nvidia)
```

### Changer le mot de passe d'accès

Dans `notebook.ipynb` cellule 3, remplacer la valeur de `VOICE_STUDIO_PASSWORD`.
Committer + pusher, le notebook se met à jour automatiquement au prochain `Tout exécuter`.

### Architecture

```
voice-clone-studio/
├── notebook.ipynb         # façade Colab (5 cellules)
├── voice_studio/          # package Python principal
│   ├── config.py          # constantes
│   ├── tts.py             # wrapper F5-TTS
│   ├── voices.py          # gestion banque de voix
│   ├── drive.py           # mount + save Drive
│   └── gradio_app.py      # UI Gradio
├── voices/                # samples préchargés (fair-use démo)
└── tests/                 # pytest (GPU-gated où nécessaire)
```

### Ajouter une voix préchargée

Voir `voices/README.md`.

## Tech stack

- Python 3.10+
- [F5-TTS](https://github.com/SWivid/F5-TTS) — voice cloning zero-shot
- [Gradio](https://www.gradio.app/) 5.x — interface web
- Google Colab — runtime gratuit avec GPU T4
- Google Drive — persistence des outputs

## Limites connues

- Seulement le français en v1
- Max 500 caractères par génération
- URL Gradio éphémère (nouvelle à chaque relance du notebook)
- Session Colab gratuite limitée à ~12h de GPU par jour

## Légal

Cet outil est fourni à des fins personnelles et de démonstration. L'utilisateur final est responsable de l'usage des clones vocaux générés. Ne pas utiliser pour de la diffamation, usurpation d'identité, ou fraude.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README final (user + mainteneur)"
```

---

## Task 14: Suite finale — lancer la suite complète de tests + checklist d'intégration

Valider que tout tient ensemble avant le premier push GitHub.

- [ ] **Step 1: Lancer toute la suite de tests**

```bash
cd ~/Bureau/voice-clone-studio
pytest -v
```

Expected : tous PASS (les 2 tests GPU skip hors Colab).

- [ ] **Step 2: Linter smoke check**

```bash
python -m py_compile voice_studio/*.py
python -c "from voice_studio import config, voices, drive, tts, gradio_app; print('all imports OK')"
```

Expected: `all imports OK`

- [ ] **Step 3: Vérifier que le notebook est valide**

```bash
python -c "import json, sys; nb=json.load(open('notebook.ipynb')); print(f'notebook OK, {len(nb[\"cells\"])} cellules')"
```

Expected: `notebook OK, 5 cellules`

- [ ] **Step 4: Checklist manuelle avant push**

- [ ] Remplacer `USER` par le vrai username GitHub dans `README.md`, `notebook.ipynb` cell 2, et le badge
- [ ] Sourcer les 2 audios presets (Task 12 Step 3)
- [ ] Changer le mot de passe par défaut dans `notebook.ipynb` cell 3
- [ ] Créer le repo GitHub public `voice-clone-studio` via le UI ou `gh repo create`
- [ ] `git remote add origin <url>` + `git push -u origin main`
- [ ] Ouvrir le badge Colab dans un navigateur en mode incognito → faire un tour complet (exécuter, générer 1 audio, sauver sur Drive)

- [ ] **Step 5: Commit final de cleanup si besoin**

```bash
git status  # il ne devrait rien rester d'unstaged
# Si nécessaire, tag la v1
git tag -a v0.1.0 -m "v0.1.0 — MVP fonctionnel"
```

---

## Récap du plan

| Task | Sujet | Tests TDD ? | GPU requis ? |
|------|-------|-------------|--------------|
| 1 | Skeleton | Non | Non |
| 2 | Package + config | Smoke | Non |
| 3 | Infra tests | — | Non |
| 4 | `voices.load_presets` | Oui | Non |
| 5 | `voices.add_uploaded` + validations | Oui | Non |
| 6 | `voices.get_by_id` + `list_all` | Oui | Non |
| 7 | `drive.save_output` | Oui | Non |
| 8 | `tts.generate` | Oui (skippé hors GPU) | Oui pour test réel |
| 9 | Gradio UI structure | Smoke import | Non |
| 10 | Gradio events wiring | Smoke import + suite | Non |
| 11 | `notebook.ipynb` | Validation JSON | Non |
| 12 | Voix préchargées | Manuel | Non |
| 13 | README final | — | Non |
| 14 | Validation finale | Suite complète | Non |

Total : **14 tasks**, majorité sans GPU donc reproductibles localement. Task 8 partielle sur GPU (testable uniquement dans Colab).
