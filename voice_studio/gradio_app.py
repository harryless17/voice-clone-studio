"""Construction de l'UI Gradio Voice Clone Studio."""
from __future__ import annotations

import gradio as gr

from voice_studio import config


CSS = """
.title { text-align: center; font-size: 2em; margin-bottom: 0.2em; }
.subtitle { text-align: center; color: #888; margin-bottom: 1em; }
#generate-btn { min-height: 60px; font-size: 1.1em; }
"""

# Référence vers le dernier .wav temporaire servi à Gradio.
# On ne garde qu'un seul fichier à la fois pour éviter l'accumulation en session Colab.
_last_tmp: dict = {"path": None}


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

            # Sanitization : stripping silencieux, warning si > 20%
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

            import os, tempfile
            # On ne garde qu'un seul fichier temporaire à la fois — supprime le précédent
            prev = _last_tmp.get("path")
            if prev and os.path.exists(prev):
                try:
                    os.remove(prev)
                except OSError:
                    pass
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_bytes)
            tmp.close()
            _last_tmp["path"] = tmp.name

            return (
                tmp.name,
                audio_bytes,
                voice.name,
                gr.DownloadButton(value=tmp.name, visible=True),
                gr.Button(visible=True),
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
