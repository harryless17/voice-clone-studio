# 🎤 Voice Clone Studio

Outil de text-to-speech avec voice cloning français, pensé pour un usage TikTok.
Tourne dans Google Colab (GPU gratuite), interface web Gradio, aucune installation locale.

![Demo](https://img.shields.io/badge/demo-colab-orange)

## Lancer le notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/harryless17/voice-clone-studio/blob/main/notebook.ipynb)


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
git clone https://github.com/harryless17/voice-clone-studio.git
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
