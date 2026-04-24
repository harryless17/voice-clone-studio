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
