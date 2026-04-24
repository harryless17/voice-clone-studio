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
