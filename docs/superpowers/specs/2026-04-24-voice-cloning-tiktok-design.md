# Voice Clone Studio — Design Doc

**Date** : 2026-04-24
**Auteur** : Aghiles Manseur
**Statut** : Design validé, en attente d'implémentation

## 1. Contexte

Un ami d'Aghiles, créateur de contenu TikTok non-technique, a besoin d'un outil pour générer des audios à partir de texte avec une voix clonée (ex : Zidane lisant un texte). L'outil doit être gratuit, utilisable sans compétences techniques, et produire des fichiers audio utilisables dans des montages TikTok (CapCut, InShot).

Plutôt que de développer un backend hébergé (qui coûterait en GPU), on s'appuie sur Google Colab pour exploiter la GPU gratuite et on distribue un notebook léger qui expose une interface Gradio.

## 2. Objectifs

**Principaux :**
- Cloner une voix française à partir d'un échantillon audio court (10-30s)
- Générer un audio TTS (≤ 500 caractères) avec la voix clonée
- Interface graphique accessible depuis un navigateur, sans installation
- Sauvegarde des outputs sur Google Drive
- Accès protégé par mot de passe

**Non-objectifs (hors scope) :**
- Multi-utilisateurs simultanés (outil mono-user)
- Support d'autres langues que le français (au moins en v1)
- Édition audio (bruit de fond, pitch, vitesse) → hors scope, à faire dans CapCut
- Persistence au-delà de Google Drive (pas de base de données)
- Application mobile / desktop native

## 3. Utilisateurs & flow

### 3.1 Acteurs

- **Le mainteneur** (Aghiles) : héberge le repo GitHub, maintient le code
- **L'utilisateur final** (l'ami) : non-technique, utilise le notebook via son navigateur

### 3.2 Setup initial (mainteneur, une fois)

1. Créer un repo GitHub public `voice-clone-studio`
2. Pusher le code depuis `~/Bureau/voice-clone-studio/`
3. Tester manuellement le notebook sur Colab
4. Partager avec l'ami :
   - Lien Colab : `https://colab.research.google.com/github/USER/voice-clone-studio/blob/main/notebook.ipynb`
   - Mot de passe d'accès Gradio
5. Onboarding en visio (10 min) recommandé le premier soir

### 3.3 Flow d'utilisation (utilisateur final, à chaque session)

1. **Ouvrir le bookmark Colab** (5s) — déjà connecté à son Google
2. **Cliquer "▶ Tout exécuter"** (30s à 2min selon cache) — autorise l'accès Drive au popup
3. **Cliquer sur l'URL Gradio** qui apparaît en sortie — format `https://xxx.gradio.live`
4. **Se login** avec user + mot de passe codés en dur
5. **Utiliser l'interface** (boucle) :
   - Choisir une voix (preset ou uploader)
   - Taper le texte (≤ 500 chars)
   - Générer → écouter → télécharger OU sauver sur Drive
6. **Fermer l'onglet** en fin de session — Colab se ferme seul après ~90 min d'inactivité

## 4. Architecture

### 4.1 Structure du repo

```
voice-clone-studio/
├── notebook.ipynb              # façade Colab (5 cellules)
├── requirements.txt            # F5-TTS, gradio, etc.
├── README.md                   # instructions mainteneur
├── voice_studio/               # package Python principal
│   ├── __init__.py
│   ├── config.py               # constantes (password, chemins Drive, limites)
│   ├── tts.py                  # wrapper F5-TTS
│   ├── voices.py               # gestion presets + upload
│   ├── drive.py                # mount + save Google Drive
│   └── gradio_app.py           # construction UI Gradio
├── voices/                     # samples audio préchargés
│   ├── zidane.wav              # 10-15s extrait interview publique
│   └── jamel.wav
├── tests/
│   ├── test_voices.py
│   └── test_tts.py
└── docs/
    └── superpowers/specs/
        └── 2026-04-24-voice-cloning-tiktok-design.md
```

### 4.2 Principe architectural

Le notebook est une **façade minimaliste** qui clone le repo, installe les dépendances, et importe les modules Python. Toute la logique vit dans `voice_studio/` → éditable dans VSCode en local, testable avec pytest, versionné dans Git sans les frictions habituelles d'un `.ipynb`.

Chaque module a une responsabilité unique et une interface publique claire. Pas de logique métier dans le notebook.

## 5. Composants

### 5.1 `voice_studio/config.py`

Constantes centralisées.

```python
GRADIO_USERNAME: str = "friend"
GRADIO_PASSWORD: str = "<injecté via env var ou literal>"
DRIVE_ROOT: str = "/content/drive/MyDrive/VoiceClone"
OUTPUTS_DIR: str = f"{DRIVE_ROOT}/outputs"
VOICES_DIR: str = f"{DRIVE_ROOT}/voices"      # voix uploadées
CACHE_DIR: str = f"{DRIVE_ROOT}/.cache"        # modèles F5-TTS
PRESETS_DIR: str = "voices"                    # dans le repo
MAX_TEXT_LENGTH: int = 500
MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024      # 50 Mo
MIN_VOICE_DURATION_SEC: float = 3.0
LANGUAGE: str = "fr"
```

### 5.2 `voice_studio/tts.py`

Wrapper autour de F5-TTS. Singleton pour éviter de recharger le modèle.

```python
def generate(ref_audio_path: str, text: str, language: str = "fr") -> bytes:
    """Génère un audio WAV (bytes) avec la voix de ref_audio_path disant text.

    Charge le modèle F5-TTS au premier appel (singleton).
    Lève RuntimeError si l'inférence échoue (OOM, etc.).
    """
```

### 5.3 `voice_studio/voices.py`

Gestion de la banque de voix. Modèle `Voice` :

```python
@dataclass
class Voice:
    id: str                  # slug unique
    name: str                # nom affichable
    audio_path: str          # chemin vers le .wav
    source: Literal["preset", "uploaded"]
```

Interface publique :

```python
def list_presets() -> list[Voice]
def list_uploaded() -> list[Voice]
def list_all() -> list[Voice]                     # presets + uploaded, triés
def add_uploaded(audio_bytes: bytes, name: str) -> Voice
def get_by_id(voice_id: str) -> Voice             # lève KeyError
def load_presets() -> None                         # appelé par la cellule 4 du notebook
```

Règles :
- `add_uploaded` valide : format audio, taille, durée ≥ `MIN_VOICE_DURATION_SEC`
- Nom dupliqué → suffixe auto (`mbappe`, `mbappe_2`)
- Les voix uploadées sont stockées dans `DRIVE_ROOT/voices/` → persistent entre sessions

### 5.4 `voice_studio/drive.py`

```python
def mount() -> None:
    """Mount /content/drive. Idempotent."""

def ensure_dirs() -> None:
    """Crée OUTPUTS_DIR, VOICES_DIR, CACHE_DIR s'ils n'existent pas."""

def save_output(audio_bytes: bytes, filename: str) -> str:
    """Pousse audio_bytes dans OUTPUTS_DIR/filename. Retourne le chemin complet."""
```

### 5.5 `voice_studio/gradio_app.py`

Construit l'UI Gradio (Blocks custom, pas Interface). Expose :

```python
def build_app() -> gr.Blocks
def launch(password: str) -> None:
    """Lance avec share=True, auth=(GRADIO_USERNAME, password)."""
```

### 5.6 `notebook.ipynb`

5 cellules :

```
[1] Markdown : "🎤 Voice Clone Studio — clique ▶ Tout exécuter"
[2] Clone + install    : git clone + pip install -q -r requirements.txt
[3] Mount Drive        : from voice_studio.drive import mount; mount()
[4] Load presets       : from voice_studio.voices import load_presets; load_presets()
[5] Launch UI          : from voice_studio.gradio_app import launch; launch(password=...)
```

## 6. Data flow

### 6.1 Génération

```
UI [voice_id, text] → gradio_app.on_generate()
    → voices.get_by_id(voice_id) → Voice
    → tts.generate(voice.audio_path, text, "fr") → bytes
    → UI affiche lecteur audio + stocke bytes en state
```

### 6.2 Sauvegarde Drive

```
UI [clic "💾 Sauver"] → gradio_app.on_save(audio_state, voice_name)
    → drive.save_output(bytes, f"{timestamp}_{voice}.wav")
    → UI affiche toast "✓ Sauvé : {filename}"
```

### 6.3 Upload d'une voix

```
UI [audio_file, name] → gradio_app.on_upload()
    → voices.add_uploaded(bytes, name) → Voice
    → UI refresh dropdown + sélectionne la nouvelle voix
```

## 7. Design UI

Une colonne, tient à l'écran sans scroll. Dark mode par défaut.

**Blocs de l'interface (de haut en bas) :**

1. **Header** — titre + sous-titre
2. **Bloc Voix** — radio `Préchargée / Uploader`, dropdown, preview audio 2s
3. **Bloc Texte** — textarea + compteur `0/500`
4. **Bouton Générer** — centré, état loading pendant inférence
5. **Bloc Résultat** — lecteur audio + boutons `⬇️ Télécharger` et `💾 Sauver Drive`

### 7.1 UX attendue

- **Preview 2s auto** de la voix sélectionnée (évite les surprises)
- **Compteur live** des caractères
- **Bouton Générer désactivé** si texte vide ou > 500 chars
- **Toasts non-bloquantes** pour les erreurs (rouge) et warnings (jaune)
- **État du dernier fichier sauvé** affiché sous les boutons
- **Pas de modal popup** pour les erreurs

## 8. Gestion d'erreurs

| Situation | Comportement |
|-----------|--------------|
| Texte vide / > 500 chars | Bouton Générer désactivé + message inline |
| Inférence TTS échoue | Toast rouge avec action suggérée (ex: "relance cellule 4") |
| Upload format invalide | Toast rouge, bloc upload reste prêt à retry |
| Upload audio < 3s | Toast jaune non-bloquante (warning) |
| Drive non monté au save | Remount + retry une fois, puis échoue proprement |
| Session Colab expirée | Erreur réseau Gradio → UI affiche message explicite |

**Principe** : jamais de stack trace exposée, toujours un message actionnable.

## 9. Edge cases

- **Premier lancement** : download F5-TTS (~2 Go), cache dans `DRIVE_ROOT/.cache/`. Les relances suivantes sont rapides (30s).
- **Nom de voix dupliqué** à l'upload : suffixe auto, pas d'erreur.
- **Caractères spéciaux / emojis** dans le texte : strippés silencieusement, warning si > 20% du texte.
- **Langue forcée** : `fr` en dur, pas de détection auto.
- **Concurrent requests** : queue gérée nativement par Gradio.

## 10. Stratégie de tests

Tests minimalistes mais présents, lancés via `pytest tests/` en local.

### `tests/test_voices.py` (sans GPU)

- `test_list_presets_returns_seeded_voices` — la liste n'est pas vide après `load_presets()`
- `test_add_uploaded_creates_entry` — upload d'un wav dummy apparaît dans `list_uploaded()`
- `test_duplicate_name_gets_suffix` — deux "mbappe" → `mbappe` et `mbappe_2`
- `test_reject_non_audio_file` — upload d'un `.txt` lève `ValueError`
- `test_reject_too_short_audio` — upload d'un audio de 1s lève `ValueError`

### `tests/test_tts.py` (avec GPU, skip si indisponible)

- `test_generate_returns_wav_bytes` — génération courte, headers WAV valides dans les bytes
- `test_generate_respects_length` — texte de 10 mots → audio entre 2 et 10s

### Pas de test UI

Gradio est déclaratif ; les tests end-to-end coûtent plus qu'ils n'apportent sur ce périmètre.

## 11. Stack technique

| Composant | Techno | Version min |
|-----------|--------|-------------|
| Runtime | Google Colab (GPU T4) | — |
| Python | 3.10+ | — |
| TTS | F5-TTS (`SWivid/F5-TTS` sur HuggingFace) | dernière stable |
| UI | Gradio | ≥ 5.0 |
| Persistence | Google Drive via `google.colab.drive` | — |
| Tests | pytest | ≥ 8.0 |
| VCS | GitHub (public) | — |

## 12. Sécurité & éthique

**Sécurité :**
- Accès Gradio protégé par user/password basique (niveau "garage door", suffisant pour du partage entre potes)
- URL Gradio publique (`xxx.gradio.live`) éphémère (~72h), renouvelée à chaque relance
- Aucun secret dans le repo public ; le mot de passe est soit injecté via variable d'environnement Colab, soit modifié localement dans `config.py` avant le premier partage
- Pas de données persistées hors du Drive de l'utilisateur

**Éthique :**
- L'utilisateur final est responsable des usages du clone vocal (ne pas diffamer, ne pas usurper l'identité à des fins frauduleuses)
- Le README précise l'obligation morale/légale de ne cloner que des voix pour lesquelles l'usage est autorisé ou sur le terrain du fair-use (parodie, satire)
- Les voix préchargées sont limitées à des extraits courts d'interviews publiques, à usage de démo uniquement

## 13. Critères de succès

Le projet est considéré comme réussi si :

1. L'ami peut, seul, générer un audio depuis son navigateur en < 5 min (installation exclue) à partir du moment où il ouvre le bookmark Colab
2. La qualité du clone est suffisante pour un usage TikTok (la voix est reconnaissable, pas robotique)
3. Les fichiers sauvés sur son Drive sont directement utilisables dans CapCut/InShot sans conversion
4. Il peut ajouter ses propres voix sans aide du mainteneur
5. En cas d'erreur, il sait quelle action entreprendre (sans contacter le mainteneur) dans au moins 80% des cas

## 14. Étapes hors scope / futurs

Ne pas implémenter en v1, à considérer plus tard si l'usage le justifie :

- Historique des générations précédentes (replay, re-download)
- Preset de textes fréquents ("Salut les gars, aujourd'hui...")
- Support multilingue (EN / AR)
- Export MP3 en plus du WAV (pour réduire taille fichier)
- Partage direct vers TikTok (API)
- Dashboard d'usage (nombre de générations, quota GPU restant)
