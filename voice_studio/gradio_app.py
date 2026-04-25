"""Construction de l'UI Gradio Voice Clone Studio.

Thème visuel : "Vintage Amber Console" — inspiré des consoles de mixage
analogiques. Palette warm-dark, typographie éditoriale (Fraunces + JetBrains
Mono), accents ambre/terracotta, grain subtil.
"""
from __future__ import annotations

import functools
import os
import time
import traceback

import gradio as gr

from voice_studio import config


def _log_errors(fn):
    """Imprime la traceback complète sur stdout + re-raise. Gradio renvoie
    souvent juste 'Erreur' sans détails, ce wrapper garantit qu'on voit
    la vraie cause dans la cellule Colab."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except gr.Error:
            raise
        except Exception:
            print(f"\n[ERROR] handler {fn.__name__} a crashé :")
            traceback.print_exc()
            print("")
            raise

    return wrapper


# ============================================================================
# THÈME "VINTAGE AMBER CONSOLE"
# ============================================================================

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..900,0..100,0..1;1,9..144,300..900,0..100,0..1&family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root, .gradio-container {
    --bg-black: #0d0a07;
    --bg-card: #17110b;
    --bg-elevated: #211810;
    --bg-input: #1c140d;
    --amber: #e8a54a;
    --amber-glow: #f5c878;
    --amber-dim: #8e6a2f;
    --crimson: #c94e33;
    --rose: #e76f6f;
    --text-primary: #f2ebe0;
    --text-secondary: #c9a47a;
    --text-dim: #7d674a;
    --border: #2a1f14;
    --border-hot: rgba(232, 165, 74, 0.35);

    /* --- Gradio overrides --- */
    --body-background-fill: var(--bg-black) !important;
    --background-fill-primary: var(--bg-card) !important;
    --background-fill-secondary: var(--bg-elevated) !important;
    --border-color-primary: var(--border) !important;
    --body-text-color: var(--text-primary) !important;
    --body-text-color-subdued: var(--text-secondary) !important;
    --color-accent: var(--amber) !important;
    --color-accent-soft: var(--amber-glow) !important;
    --block-background-fill: var(--bg-card) !important;
    --block-border-width: 1px !important;
    --block-border-color: var(--border) !important;
    --block-label-background-fill: transparent !important;
    --block-label-text-color: var(--text-secondary) !important;
    --block-title-text-color: var(--text-primary) !important;
    --input-background-fill: var(--bg-input) !important;
    --input-border-color: var(--border) !important;
    --input-border-color-focus: var(--amber) !important;
    --radius-sm: 8px !important;
    --radius-md: 12px !important;
    --radius-lg: 14px !important;
    --radius-xl: 18px !important;
}

/* --- RESET & OVERFLOW CONTROL --- */
html, body {
    background: var(--bg-black) !important;
    font-family: 'Instrument Sans', system-ui, sans-serif !important;
    overflow-x: hidden !important;
    max-width: 100vw !important;
    margin: 0 !important;
}
*, *::before, *::after { box-sizing: border-box; }

/* Grain noise overlay — ambiance "tape" */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 99;
    opacity: 0.035;
    mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Ambient glow — halo ambré diffus en haut */
body::after {
    content: '';
    position: fixed;
    top: -200px;
    left: 50%;
    transform: translateX(-50%);
    width: min(600px, 90vw);
    height: min(600px, 90vw);
    background: radial-gradient(circle, rgba(232, 165, 74, 0.12) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

.gradio-container {
    max-width: min(780px, 100%) !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 2.5rem 1.25rem 3rem !important;
    position: relative;
    z-index: 1;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}
.gradio-container > *, .gradio-container .main {
    max-width: 100% !important;
}

/* --- HEADER --- */
.studio-header { text-align: center; margin-bottom: 2rem; position: relative; }
.studio-title {
    font-family: 'Fraunces', serif !important;
    font-weight: 700 !important;
    font-size: clamp(2.2rem, 7vw, 3.6rem) !important;
    line-height: 1 !important;
    letter-spacing: -0.03em !important;
    font-variation-settings: "SOFT" 50, "WONK" 1;
    background: linear-gradient(135deg, #f5c878 0%, #e8a54a 40%, #c94e33 90%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent !important;
    margin: 0 !important;
}
.studio-title em {
    font-style: italic;
    font-weight: 400;
    font-variation-settings: "SOFT" 100, "WONK" 1;
}
.studio-sub {
    font-family: 'Fraunces', serif !important;
    font-style: italic !important;
    font-weight: 300 !important;
    font-size: clamp(0.95rem, 2.2vw, 1.2rem) !important;
    color: var(--text-secondary) !important;
    margin-top: 0.5rem !important;
    letter-spacing: 0.01em;
}
.studio-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--amber-dim);
    padding: 0.3rem 0.9rem;
    border: 1px solid var(--border);
    border-radius: 100px;
    margin-bottom: 1.2rem;
    background: var(--bg-card);
}

/* --- BLOCKS / CARDS --- */
.gradio-container > .main .block,
.gradio-container .form {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.02) inset !important;
}

/* Labels — mono micro-caps, façon rack de studio */
label > span,
label > .label-wrap,
.block-info {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* Inputs */
input[type="text"], textarea, .input-container input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    font-size: 15px !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px rgba(232, 165, 74, 0.08) !important;
    outline: none !important;
}

/* Primary button — bouton cuivre lumineux */
button.primary, #generate-btn {
    background: linear-gradient(135deg, var(--amber) 0%, var(--crimson) 100%) !important;
    color: #1a0f04 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 58px !important;
    box-shadow: 0 4px 20px -4px rgba(232, 165, 74, 0.25),
                0 1px 0 rgba(255, 220, 170, 0.4) inset !important;
    transition: all 0.25s ease !important;
    position: relative;
    overflow: hidden;
}
button.primary:hover:not(:disabled), #generate-btn:hover:not(:disabled) {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px -2px rgba(232, 165, 74, 0.4),
                0 1px 0 rgba(255, 220, 170, 0.4) inset !important;
}
button.primary:active:not(:disabled), #generate-btn:active:not(:disabled) {
    transform: translateY(0) !important;
}
button.primary:disabled, #generate-btn:disabled {
    background: var(--bg-elevated) !important;
    color: var(--text-dim) !important;
    cursor: not-allowed !important;
    box-shadow: inset 0 0 0 1px var(--border) !important;
    border: none !important;
    opacity: 1 !important;
}
button.primary:disabled::before, #generate-btn:disabled::before {
    content: '↓ ';
    color: var(--text-dim);
    margin-right: 0.4em;
}

/* Secondary buttons */
button.secondary, .gradio-container button:not(.primary):not(#generate-btn) {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
button.secondary:hover:not(:disabled) {
    border-color: var(--border-hot) !important;
    color: var(--amber-glow) !important;
}

/* Radio buttons — "switch de console" plus discrets en selected */
.gradio-container input[type="radio"] + span,
fieldset label {
    padding: 0.5rem 1rem !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
fieldset label.selected, fieldset label:has(input:checked) {
    background: rgba(232, 165, 74, 0.08) !important;
    border-color: var(--amber-dim) !important;
    color: var(--amber-glow) !important;
}
fieldset label.selected input[type="radio"],
fieldset label:has(input:checked) input[type="radio"] {
    accent-color: var(--amber) !important;
}

/* --- Dropdown : hide the native chevron (Gradio en dessine déjà une) --- */
.gradio-container select {
    background-image: none !important;
    appearance: none !important;
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
}
.gradio-container [data-testid="dropdown"] .wrap-inner {
    padding-right: 2.5rem !important;
}

/* --- Slider : champ numérique visible, reset button caché --- */
.gradio-container .slider_input input[type="number"] {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    color: var(--amber) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.3rem 0.5rem !important;
    border-radius: 6px !important;
    min-width: 60px !important;
}
.gradio-container .reset-button, .gradio-container button[aria-label*="reset"] {
    display: none !important;
}
/* Valeurs min/max du slider : formatage propre */
.gradio-container .slider-display, .gradio-container .min-max {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--text-dim) !important;
}

/* --- Audio : cacher la mini-flèche download du composant preview --- */
.gradio-container #voice-preview button[aria-label*="Download"],
.gradio-container #voice-preview a[download],
.gradio-container .preview-audio button[aria-label*="Download"],
.gradio-container .preview-audio a[download] {
    display: none !important;
}

/* --- Audio players : responsive width --- */
.gradio-container audio, .gradio-container .audio {
    width: 100% !important;
    max-width: 100% !important;
}

/* Accordions */
.gradio-container .label-wrap, details > summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
}

/* Slider */
.slider_input input[type="number"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--amber) !important;
}

/* --- TEMPLATES chips : grid 2x2 sur mobile, ligne sur desktop --- */
.templates-row {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)) !important;
    gap: 0.5rem !important;
    margin-bottom: 0.8rem !important;
    width: 100% !important;
}
.template-chip, .template-chip button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 0.6rem !important;
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 100px !important;
    color: var(--text-secondary) !important;
    cursor: pointer;
    transition: all 0.2s ease !important;
    min-height: auto !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    font-weight: 500 !important;
    width: 100% !important;
}
.template-chip:hover, .template-chip button:hover {
    border-color: var(--border-hot) !important;
    color: var(--amber) !important;
    background: var(--bg-card) !important;
    transform: translateY(-1px);
}

/* --- HISTORY --- */
.history-title {
    font-family: 'Fraunces', serif;
    font-size: 1.3rem;
    font-weight: 400;
    font-style: italic;
    color: var(--amber);
    margin: 2.5rem 0 1rem;
    display: flex;
    align-items: baseline;
    gap: 0.8rem;
    font-variation-settings: "SOFT" 100, "WONK" 1;
}
.history-title .ornament {
    color: var(--amber-dim);
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    font-style: normal;
}
.history-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-hot) 0%, transparent 100%);
    align-self: center;
}
.history-empty {
    text-align: center;
    padding: 2.5rem 1rem;
    color: var(--text-dim);
    font-family: 'Fraunces', serif;
    font-size: 1rem;
    line-height: 1.5;
    border: 1px dashed var(--border);
    border-radius: 14px;
    background: rgba(232, 165, 74, 0.02);
}
.history-empty em {
    font-style: italic;
    color: var(--amber-dim);
}
.history-list {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}
.history-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    transition: border-color 0.2s ease;
}
.history-item:hover { border-color: var(--border-hot); }
.history-meta {
    display: flex;
    gap: 0.8rem;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    color: var(--text-dim);
}
.history-time { color: var(--amber-dim); }
.history-voice { color: var(--amber); font-weight: 600; }
.history-speed {
    margin-left: auto;
    padding: 0.1rem 0.5rem;
    background: var(--bg-elevated);
    border-radius: 4px;
}
.history-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 0.92rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    line-height: 1.4;
}
.history-audio { width: 100%; height: 36px; }
.history-audio::-webkit-media-controls-panel {
    background: var(--bg-elevated);
}

/* --- RESULT area --- */
.result-wrap { position: relative; }
.result-wrap audio { filter: sepia(0.25) saturate(1.1); }

/* Empty state audio : icône ♪ par défaut trop triste, on la rehausse */
.gradio-container .audio-container .empty {
    font-family: 'Fraunces', serif !important;
    font-style: italic !important;
    color: var(--text-dim) !important;
    padding: 2rem 1rem !important;
}

/* Row des boutons d'action sous le résultat : wrap propre sur mobile */
.result-wrap .form-container + div > .button,
.result-wrap button {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

/* Info text */
.block-info, [class*="info"] {
    color: var(--text-dim) !important;
    font-size: 0.78rem !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-style: italic;
}

/* --- SPLASH SCREEN --- */
.splash-overlay {
    position: fixed;
    inset: 0;
    background: var(--bg-black);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    z-index: 99999;
    animation: splash-fade 3.2s forwards ease-out;
    pointer-events: none;
    opacity: 0;
}
.splash-overlay::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(232, 165, 74, 0.18) 0%, transparent 55%);
}
.splash-hearts {
    font-size: 3em;
    margin-bottom: 0.5em;
    animation: splash-heartbeat 1.4s ease-in-out infinite;
    position: relative;
}
.splash-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 1.15em;
    color: var(--text-secondary);
    margin-bottom: 0.3em;
    letter-spacing: 0.02em;
    position: relative;
}
.splash-name {
    font-family: 'Fraunces', serif;
    font-size: clamp(1.8em, 6vw, 3em);
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #f5c878 0%, #e8a54a 40%, #e76f6f 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    position: relative;
    font-variation-settings: "SOFT" 50, "WONK" 1;
}
@keyframes splash-fade {
    0%   { opacity: 0; }
    12%  { opacity: 1; }
    78%  { opacity: 1; }
    100% { opacity: 0; visibility: hidden; }
}
@keyframes splash-heartbeat {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.15); }
}

/* --- MOBILE --- */
@media (max-width: 640px) {
    .gradio-container {
        padding: 1.5rem 0.85rem 2.5rem !important;
    }
    body::after { width: 400px; height: 400px; top: -150px; }
    .history-meta { flex-wrap: wrap; gap: 0.4rem; }
    .history-speed { margin-left: 0; }
    button.primary, #generate-btn {
        font-size: 0.85rem !important;
        min-height: 52px !important;
    }
}

/* Footer Gradio natif — on le masque, on a notre custom */
footer { display: none !important; }

/* --- Custom footer --- */
.custom-footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    text-align: center;
    position: relative;
}
.footer-ornament {
    color: var(--amber-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.5em;
    margin-bottom: 0.8rem;
    opacity: 0.7;
}
.footer-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 0.85rem;
    color: var(--text-dim);
    letter-spacing: 0.01em;
}
.footer-text strong {
    color: var(--text-secondary);
    font-weight: 600;
    font-style: normal;
    letter-spacing: 0.02em;
}
.footer-heart {
    display: inline-block;
    animation: splash-heartbeat 1.8s ease-in-out infinite;
}
"""


# ============================================================================
# TEMPLATES DE TEXTES
# ============================================================================

TEMPLATES = [
    ("🎬 Intro", "Salut tout le monde, bienvenue sur ma chaîne ! Aujourd'hui on va parler de "),
    ("🔚 Outro", "Voilà pour aujourd'hui. N'oubliez pas de liker et de vous abonner. À très vite !"),
    ("😂 Réaction", "Attendez attendez, j'ai vu ça sur internet et je peux pas, faut que je vous le raconte."),
    ("🎙️ Présentation", "Bonjour, je m'appelle Nordine et aujourd'hui je vais vous présenter "),
]


# ============================================================================
# STATE utilitaire (tmp files alive pour l'historique)
# ============================================================================

_history_paths: list = []  # paths des tmp files en vie, cap à 5


def _prune_history_tmps(active_paths: list[str]) -> None:
    """Supprime les tmp qui ne sont plus référencés dans active_paths."""
    global _history_paths
    to_delete = [p for p in _history_paths if p not in active_paths]
    for p in to_delete:
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass
    _history_paths = list(active_paths)


_HISTORY_HEADING = (
    "<div class='history-title'>"
    "<span class='ornament'>mixtape</span>"
    "Dernières pistes"
    "</div>"
)


def _render_history_html(history: list[dict]) -> str:
    """Rend la liste d'historique en HTML avec <audio> players natifs."""
    if not history:
        return (
            _HISTORY_HEADING
            + "<div class='history-empty'>"
              "Rien dans la mixtape pour le moment.<br>"
              "<em>Tes pistes s'accumuleront ici au fur et à mesure.</em>"
              "</div>"
        )
    items = []
    for entry in history:
        items.append(
            f"""
            <div class='history-item'>
              <div class='history-meta'>
                <span class='history-time'>{entry['time']}</span>
                <span class='history-voice'>{entry['voice']}</span>
                <span class='history-speed'>{entry['speed']:.2f}x</span>
              </div>
              <div class='history-text'>« {entry['text_preview']} »</div>
              <audio controls preload='none' class='history-audio'
                     src='/gradio_api/file={entry['path']}'></audio>
            </div>
            """
        )
    return (
        _HISTORY_HEADING
        + f"<div class='history-list'>{''.join(items)}</div>"
    )


# ============================================================================
# BUILD APP
# ============================================================================


def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="Le Studio Vocal de Nordine",
        theme=gr.themes.Base(
            primary_hue="orange",
            neutral_hue="stone",
            font=[gr.themes.GoogleFont("Instrument Sans"), "ui-sans-serif", "sans-serif"],
        ),
        css=CSS,
    ) as app:
        # --- Splash ---
        gr.HTML(
            """
            <div class='splash-overlay'>
              <div class='splash-hearts'>❤️</div>
              <div class='splash-text'>Fait avec amour par</div>
              <div class='splash-name'>Aghiles A MANSEUR</div>
            </div>
            """
        )

        # --- Header ---
        gr.HTML(
            """
            <div class='studio-header'>
              <div class='studio-badge'>· voice studio ·</div>
              <h1 class='studio-title'>Le Studio Vocal<br><em>de Nordine</em></h1>
              <div class='studio-sub'>Clone n'importe quelle voix, dis ce que tu veux.</div>
            </div>
            """
        )

        # ----- Voix -----
        with gr.Group():
            voice_mode = gr.Radio(
                choices=["Préchargée", "Uploader une nouvelle"],
                value="Préchargée",
                label="La voix",
            )
            voice_dropdown = gr.Dropdown(
                choices=[],
                label="Choisir dans ta banque",
                visible=True,
            )
            voice_preview = gr.Audio(
                label="Aperçu",
                interactive=False,
                visible=True,
                elem_id="voice-preview",
                elem_classes=["preview-audio"],
                show_download_button=False,
                show_share_button=False,
            )
            with gr.Group(visible=False) as upload_group:
                upload_name = gr.Textbox(label="Nom de la voix", placeholder="ex: mbappe")
                upload_file = gr.File(label="Fichier audio", file_types=[".wav", ".mp3"])
                gr.Markdown(
                    "*Une seule personne, pas de musique/bruit, 10-30 secondes suffisent.*"
                )
                upload_btn = gr.Button("Ajouter à la banque", interactive=False)
                upload_status = gr.Markdown(visible=False)

        # ----- Texte + templates -----
        with gr.Group():
            gr.HTML("<div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--text-secondary);margin-bottom:0.5rem;'>Inspirations rapides</div>")
            with gr.Row(elem_classes=["templates-row"]):
                template_btns = [
                    gr.Button(label, elem_classes=["template-chip"], size="sm")
                    for label, _ in TEMPLATES
                ]

            text_input = gr.Textbox(
                label=f"Ton texte (max {config.MAX_TEXT_LENGTH})",
                lines=4,
                max_lines=8,
                placeholder="Salut les gars, aujourd'hui on va...",
            )
            char_count = gr.Markdown(f"<code>0/{config.MAX_TEXT_LENGTH}</code>")

        # ----- Réglages avancés -----
        with gr.Accordion("Réglages avancés", open=False):
            speed_slider = gr.Slider(
                minimum=0.7,
                maximum=1.3,
                value=1.0,
                step=0.05,
                label="Vitesse de lecture",
                info="1.0 = naturel · < 1 = ralenti · > 1 = accéléré",
            )

        # ----- Bouton générer -----
        generate_btn = gr.Button(
            "Générer la piste",
            variant="primary",
            elem_id="generate-btn",
            interactive=False,
        )

        # ----- Résultat -----
        with gr.Group(elem_classes=["result-wrap"]):
            output_audio = gr.Audio(label="La dernière piste", interactive=False)
            with gr.Row():
                regenerate_btn = gr.Button("🔄 Regénérer", visible=False, size="sm")
                download_btn = gr.DownloadButton("⬇️ Télécharger", visible=False, size="sm")
                save_drive_btn = gr.Button("💾 Sauver dans Drive", visible=False, size="sm")
            save_status = gr.Markdown(visible=False)

        # ----- Historique -----
        history_html = gr.HTML(_render_history_html([]))

        # States
        last_audio_state = gr.State(value=None)
        last_voice_state = gr.State(value=None)
        last_voice_id_state = gr.State(value=None)
        last_text_state = gr.State(value=None)
        last_speed_state = gr.State(value=1.0)
        history_state = gr.State(value=[])

        # ====================================================================
        # HANDLERS
        # ====================================================================

        @_log_errors
        def _refresh_voice_list():
            from voice_studio import voices as voices_mod
            all_voices = voices_mod.list_all()
            return gr.Dropdown(
                choices=[(v.name, v.id) for v in all_voices],
                value=all_voices[0].id if all_voices else None,
            )

        @_log_errors
        def on_mode_change(mode):
            if mode == "Préchargée":
                return gr.Group(visible=False), gr.Dropdown(visible=True), gr.Audio(visible=True)
            return gr.Group(visible=True), gr.Dropdown(visible=False), gr.Audio(visible=False)

        voice_mode.change(
            on_mode_change,
            inputs=[voice_mode],
            outputs=[upload_group, voice_dropdown, voice_preview],
        )

        def _is_text_valid(text: str) -> bool:
            count = len(text or "")
            return 0 < count <= config.MAX_TEXT_LENGTH and bool((text or "").strip())

        def _generate_btn_state(voice_id, text):
            """Activé uniquement si une voix est sélectionnée ET le texte valide."""
            return gr.Button(interactive=bool(voice_id) and _is_text_valid(text))

        @_log_errors
        def on_voice_selected(voice_id, text):
            """Update preview audio + état bouton Générer."""
            from voice_studio import voices as voices_mod
            preview_path = None
            if voice_id:
                try:
                    preview_path = voices_mod.get_by_id(voice_id).audio_path
                except KeyError:
                    pass
            return preview_path, _generate_btn_state(voice_id, text)

        voice_dropdown.change(
            on_voice_selected,
            inputs=[voice_dropdown, text_input],
            outputs=[voice_preview, generate_btn],
        )

        @_log_errors
        def on_text_change(text, voice_id):
            """Update char counter + état bouton Générer."""
            count = len(text or "")
            over = count > config.MAX_TEXT_LENGTH
            color = "var(--crimson)" if over else "var(--text-secondary)"
            md = (
                f"<code style='color:{color};font-size:0.75rem;"
                f"letter-spacing:0.1em;'>{count}/{config.MAX_TEXT_LENGTH}</code>"
            )
            return md, _generate_btn_state(voice_id, text)

        text_input.change(
            on_text_change,
            inputs=[text_input, voice_dropdown],
            outputs=[char_count, generate_btn],
        )

        # Template chips → injectent le texte
        for btn, (label, template_text) in zip(template_btns, TEMPLATES):
            btn.click(
                lambda tpl=template_text: tpl,
                inputs=[],
                outputs=[text_input],
            )

        # Upload button n'est cliquable que si fichier + nom fournis
        @_log_errors
        def _upload_btn_state(file_obj, name):
            has_file = file_obj is not None
            has_name = bool(name and name.strip())
            return gr.Button(interactive=has_file and has_name)

        upload_file.change(
            _upload_btn_state,
            inputs=[upload_file, upload_name],
            outputs=[upload_btn],
        )
        upload_name.change(
            _upload_btn_state,
            inputs=[upload_file, upload_name],
            outputs=[upload_btn],
        )

        @_log_errors
        def on_upload(file_obj, name, current_text):
            from voice_studio import voices as voices_mod
            try:
                with open(file_obj.name, "rb") as f:
                    audio_bytes = f.read()
                v = voices_mod.add_uploaded(audio_bytes, name)
            except ValueError as e:
                return (
                    gr.Markdown(f"❌ {e}", visible=True),
                    gr.update(),       # dropdown inchangé
                    gr.update(),       # preview inchangé
                    gr.update(),       # generate_btn inchangé
                    gr.update(),       # upload_btn inchangé
                )
            # Succès : refresh dropdown + sélectionne la nouvelle voix
            all_voices = voices_mod.list_all()
            new_dropdown = gr.Dropdown(
                choices=[(voice.name, voice.id) for voice in all_voices],
                value=v.id,
            )
            return (
                gr.Markdown(f"✅ Voix **{v.name}** ajoutée", visible=True),
                new_dropdown,
                v.audio_path,                                  # preview maj
                _generate_btn_state(v.id, current_text),       # generate_btn réévalué
                gr.Button(interactive=False),                  # upload_btn re-disabled
            )

        upload_btn.click(
            on_upload,
            inputs=[upload_file, upload_name, text_input],
            outputs=[upload_status, voice_dropdown, voice_preview, generate_btn, upload_btn],
        )

        # Sanitization (strippe emojis, garde la ponctuation FR)
        import re as _re

        def _sanitize_text(text: str) -> tuple[str, float]:
            cleaned = _re.sub(r"[^\w\s.,;:!?'\"\-–—…()«»‘’“”]", "", text, flags=_re.UNICODE)
            original_len = max(len(text), 1)
            stripped = (original_len - len(cleaned)) / original_len
            return cleaned.strip(), stripped

        @_log_errors
        def on_generate(voice_id, text, speed, history):
            from voice_studio import tts, voices as voices_mod
            if not text or not text.strip():
                raise gr.Error("Le texte ne peut pas être vide")
            if len(text) > config.MAX_TEXT_LENGTH:
                raise gr.Error(f"Texte trop long ({len(text)}/{config.MAX_TEXT_LENGTH})")
            if not voice_id:
                raise gr.Error("Sélectionne une voix")

            cleaned_text, stripped_ratio = _sanitize_text(text)
            if not cleaned_text:
                raise gr.Error("Le texte ne contient aucun caractère supporté")
            if stripped_ratio > 0.2:
                gr.Warning(f"⚠️ {int(stripped_ratio * 100)}% du texte a été strippé")

            voice = voices_mod.get_by_id(voice_id)
            try:
                audio_bytes = tts.generate(
                    voice.audio_path,
                    cleaned_text,
                    language=config.LANGUAGE,
                    speed=speed,
                )
            except RuntimeError as e:
                raise gr.Error(f"Génération échouée : {e}")

            # Nouveau tmp file pour cette génération
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_bytes)
            tmp.close()

            # Ajoute à l'historique
            text_preview = text[:80] + ("…" if len(text) > 80 else "")
            new_entry = {
                "path": tmp.name,
                "voice": voice.name,
                "text_preview": text_preview,
                "time": time.strftime("%H:%M:%S"),
                "speed": speed,
            }
            new_history = ([new_entry] + (history or []))[:5]
            _prune_history_tmps([e["path"] for e in new_history])

            return (
                tmp.name,                                             # output_audio
                audio_bytes,                                          # last_audio_state
                voice.name,                                           # last_voice_state
                voice_id,                                             # last_voice_id_state
                text,                                                 # last_text_state
                speed,                                                # last_speed_state
                new_history,                                          # history_state
                _render_history_html(new_history),                    # history_html
                gr.Button(visible=True),                              # regenerate_btn
                gr.DownloadButton(value=tmp.name, visible=True),      # download_btn
                gr.Button(visible=True),                              # save_drive_btn
            )

        generate_outputs = [
            output_audio,
            last_audio_state,
            last_voice_state,
            last_voice_id_state,
            last_text_state,
            last_speed_state,
            history_state,
            history_html,
            regenerate_btn,
            download_btn,
            save_drive_btn,
        ]

        generate_btn.click(
            on_generate,
            inputs=[voice_dropdown, text_input, speed_slider, history_state],
            outputs=generate_outputs,
        )

        # Regénérer = rejouer avec les derniers inputs
        @_log_errors
        def on_regenerate(last_voice_id, last_text, last_speed, history):
            if not last_voice_id or not last_text:
                raise gr.Error("Rien à regénérer — fais d'abord une première génération")
            return on_generate(last_voice_id, last_text, last_speed, history)

        regenerate_btn.click(
            on_regenerate,
            inputs=[last_voice_id_state, last_text_state, last_speed_state, history_state],
            outputs=generate_outputs,
        )

        # Save Drive
        @_log_errors
        def on_save_drive(audio_bytes, voice_name):
            from datetime import datetime
            from voice_studio import drive as drive_mod

            if not audio_bytes:
                return gr.Markdown("⚠️ Aucun audio à sauver", visible=True)

            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{ts}_{voice_name}.wav"
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

        # Load initial
        @_log_errors
        def _initial_load():
            from voice_studio import voices as voices_mod
            all_voices = voices_mod.list_all()
            if not all_voices:
                return (
                    gr.Radio(value="Uploader une nouvelle"),
                    gr.Group(visible=True),
                    gr.Dropdown(choices=[], value=None, visible=False),
                    gr.Audio(value=None, visible=False),
                )
            first = all_voices[0]
            return (
                gr.Radio(value="Préchargée"),
                gr.Group(visible=False),
                gr.Dropdown(
                    choices=[(v.name, v.id) for v in all_voices],
                    value=first.id,
                    visible=True,
                ),
                gr.Audio(value=first.audio_path, visible=True),
            )

        app.load(
            _initial_load,
            outputs=[voice_mode, upload_group, voice_dropdown, voice_preview],
        )

        # --- Footer custom ---
        gr.HTML(
            """
            <div class='custom-footer'>
              <div class='footer-ornament'>·&nbsp;·&nbsp;·</div>
              <div class='footer-text'>
                Voice Studio — fait avec <span class='footer-heart'>❤️</span>
                par <strong>Aghiles A MANSEUR</strong>
              </div>
            </div>
            """
        )

    return app


# ============================================================================
# LAUNCH
# ============================================================================


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
        auth_message="Entre tes identifiants pour accéder à ton studio",
        show_error=True,
        debug=True,
        allowed_paths=[config.VOICES_DIR, config.OUTPUTS_DIR],
    )
