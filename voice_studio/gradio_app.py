"""Construction de l'UI Gradio Voice Clone Studio.

Thème visuel : "Vintage Amber Console" — console de mixage analogique
réinterprétée en éditorial magazine. Layout asymétrique 2-colonnes sur
desktop, sections sans cartes (rail ambré à la place), SVG décoratifs,
typographie variable Fraunces.
"""
from __future__ import annotations

import functools
import os
import time
import traceback

import gradio as gr

from voice_studio import config


def _log_errors(fn):
    """Imprime la traceback complète sur stdout + re-raise."""
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
# THÈME "VINTAGE AMBER CONSOLE" — v2, éditorial magazine
# ============================================================================

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..900,0..100,0..1;1,9..144,300..900,0..100,0..1&family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root, .gradio-container {
    --bg-black: #0d0a07;
    --bg-soft: #14100a;
    --bg-elevated: #1c1510;
    --bg-input: #1a130d;
    --amber: #e8a54a;
    --amber-glow: #f5c878;
    --amber-dim: #8e6a2f;
    --crimson: #c94e33;
    --rose: #e76f6f;
    --text-primary: #f2ebe0;
    --text-secondary: #c9a47a;
    --text-dim: #7d674a;
    --text-faint: #4a3d2b;
    --border: #2a1f14;
    --border-hot: rgba(232, 165, 74, 0.35);

    --body-background-fill: var(--bg-black) !important;
    --background-fill-primary: transparent !important;
    --background-fill-secondary: transparent !important;
    --border-color-primary: var(--border) !important;
    --body-text-color: var(--text-primary) !important;
    --body-text-color-subdued: var(--text-secondary) !important;
    --color-accent: var(--amber) !important;
    --color-accent-soft: var(--amber-glow) !important;
    --block-background-fill: transparent !important;
    --block-border-width: 0 !important;
    --block-border-color: transparent !important;
    --block-label-background-fill: transparent !important;
    --block-label-text-color: var(--text-secondary) !important;
    --block-title-text-color: var(--text-primary) !important;
    --input-background-fill: var(--bg-input) !important;
    --input-border-color: var(--border) !important;
    --input-border-color-focus: var(--amber) !important;
    --radius-sm: 6px !important;
    --radius-md: 10px !important;
    --radius-lg: 12px !important;
    --radius-xl: 16px !important;
}

/* --- RESET + OVERFLOW --- */
html, body {
    background: var(--bg-black) !important;
    font-family: 'Instrument Sans', system-ui, sans-serif !important;
    overflow-x: hidden !important;
    max-width: 100vw !important;
    margin: 0 !important;
}
*, *::before, *::after { box-sizing: border-box; }

/* --- ATMOSPHERIC BACKGROUND --- */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 99;
    opacity: 0.04;
    mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Gradient blobs atmosphériques */
.bg-decor {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.55;
    animation: blob-float 22s ease-in-out infinite;
}
.blob-1 {
    top: -10%;
    left: 50%;
    transform: translateX(-50%);
    width: min(60vw, 700px);
    height: min(60vw, 700px);
    background: radial-gradient(circle, rgba(232, 165, 74, 0.18) 0%, transparent 65%);
}
.blob-2 {
    top: 30%;
    right: -15%;
    width: min(45vw, 500px);
    height: min(45vw, 500px);
    background: radial-gradient(circle, rgba(201, 78, 51, 0.12) 0%, transparent 65%);
    animation-delay: -8s;
}
.blob-3 {
    bottom: 10%;
    left: -10%;
    width: min(50vw, 600px);
    height: min(50vw, 600px);
    background: radial-gradient(circle, rgba(231, 111, 111, 0.08) 0%, transparent 65%);
    animation-delay: -15s;
}
@keyframes blob-float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33%      { transform: translate(30px, -20px) scale(1.05); }
    66%      { transform: translate(-20px, 30px) scale(0.95); }
}

.gradio-container {
    max-width: min(1100px, 100%) !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 3rem 1.75rem 4rem !important;
    position: relative;
    z-index: 1;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}
.gradio-container > *, .gradio-container .main { max-width: 100% !important; }

/* --- HERO --- */
.hero {
    text-align: center;
    margin-bottom: 3.5rem;
    position: relative;
    padding: 0 0.5rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--amber-dim);
    padding: 0.35rem 1rem;
    border: 1px solid var(--border);
    border-radius: 100px;
    margin-bottom: 1.5rem;
    background: rgba(28, 21, 16, 0.5);
    backdrop-filter: blur(8px);
}
.hero-badge::before, .hero-badge::after {
    content: '·';
    color: var(--amber);
    font-size: 1.3em;
    line-height: 0;
}
.hero-title {
    font-family: 'Fraunces', serif !important;
    font-weight: 700 !important;
    font-size: clamp(2.6rem, 9vw, 5.5rem) !important;
    line-height: 0.95 !important;
    letter-spacing: -0.035em !important;
    font-variation-settings: "opsz" 144, "SOFT" 50, "WONK" 1 !important;
    background: linear-gradient(135deg, #fbe1a6 0%, #e8a54a 35%, #c94e33 85%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
}
.hero-title em {
    font-style: italic;
    font-weight: 400;
    font-variation-settings: "opsz" 144, "SOFT" 100, "WONK" 1 !important;
    display: block;
}
.hero-sub {
    font-family: 'Fraunces', serif !important;
    font-style: italic !important;
    font-weight: 300 !important;
    font-size: clamp(1rem, 2.3vw, 1.25rem) !important;
    color: var(--text-secondary) !important;
    margin-top: 1.2rem !important;
    margin-bottom: 0 !important;
    line-height: 1.4 !important;
}
.hero-wave {
    position: absolute;
    left: 0;
    right: 0;
    bottom: -60px;
    opacity: 0.28;
    pointer-events: none;
    z-index: -1;
}
.hero-wave svg { width: 100%; height: 80px; }
.hero-wave path {
    stroke: var(--amber);
    fill: none;
    stroke-width: 1;
}

/* --- LAYOUT : 2 COLONNES sur desktop --- */
.main-grid {
    display: flex !important;
    gap: 2.5rem !important;
    align-items: flex-start !important;
    margin-bottom: 2rem !important;
}
.col-setup {
    flex: 0 0 38% !important;
    min-width: 0 !important;
    position: relative;
}
.col-create {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

@media (max-width: 900px) {
    .main-grid {
        flex-direction: column !important;
        gap: 2.5rem !important;
    }
    .col-setup, .col-create {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
}
@media (max-width: 640px) {
    .gradio-container { padding: 1.75rem 1rem 3rem !important; }
    .main-grid { gap: 2rem !important; }
    .hero { margin-bottom: 2.5rem; }
}

/* --- SECTIONS : rail ambré + label, plus de cards --- */
.section {
    position: relative;
    padding-left: 1.4rem !important;
    margin-bottom: 2rem !important;
}
.section::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.35em;
    bottom: 0.35em;
    width: 2px;
    background: linear-gradient(180deg, var(--amber) 0%, var(--crimson) 50%, transparent 100%);
    opacity: 0.55;
    border-radius: 2px;
}
.section-label {
    display: flex;
    align-items: baseline;
    gap: 0.8rem;
    margin-bottom: 0.85rem;
}
.section-label .num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--amber-dim);
    font-weight: 600;
}
.section-label .title {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 400;
    font-size: 1.15rem;
    color: var(--text-primary);
    font-variation-settings: "SOFT" 100, "WONK" 1;
}

/* --- INPUTS : plus épais, amber focus ring --- */
input[type="text"], textarea, .input-container input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    font-size: 15px !important;
    padding: 0.8rem 1rem !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px rgba(232, 165, 74, 0.1), 0 0 40px -10px rgba(232, 165, 74, 0.25) !important;
    outline: none !important;
}
label > span, label > .label-wrap {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.82rem !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* --- RADIO → SEGMENTED CONTROL --- */
fieldset {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 100px !important;
    padding: 0.25rem !important;
    display: flex !important;
    gap: 0.25rem !important;
}
fieldset > label, fieldset > .wrap {
    flex: 1 !important;
    margin: 0 !important;
    padding: 0.7rem 1rem !important;
    border-radius: 100px !important;
    cursor: pointer !important;
    transition: background 0.25s ease, color 0.25s ease !important;
    text-align: center !important;
    background: transparent !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.02em !important;
    position: relative;
    text-transform: none !important;
}
fieldset > label input[type="radio"] {
    display: none !important;
}
fieldset > label.selected,
fieldset > label:has(input:checked) {
    background: linear-gradient(135deg, var(--amber) 0%, var(--crimson) 100%) !important;
    color: #1a0f04 !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 12px -2px rgba(232, 165, 74, 0.35), 0 1px 0 rgba(255, 220, 170, 0.3) inset !important;
}

/* --- DROPDOWN : cacher double chevron --- */
.gradio-container select {
    background-image: none !important;
    appearance: none !important;
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
}
.gradio-container [data-testid="dropdown"] input {
    font-size: 15px !important;
    padding: 0.8rem 1rem !important;
}

/* --- UPLOAD ZONE : compacte + dashed ambré --- */
.gradio-container .upload-zone .file-preview,
.gradio-container [data-testid="file"] {
    background: var(--bg-input) !important;
    border: 1.5px dashed var(--border-hot) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    transition: all 0.25s ease !important;
}
.gradio-container [data-testid="file"]:hover {
    border-color: var(--amber) !important;
    background: rgba(232, 165, 74, 0.03) !important;
}
.gradio-container [data-testid="file"] .wrap {
    min-height: 110px !important;
    padding: 0 !important;
    color: var(--text-secondary) !important;
    font-family: 'Fraunces', serif !important;
    font-style: italic !important;
    font-size: 0.95rem !important;
}
.gradio-container [data-testid="file"] button {
    color: var(--amber) !important;
    font-family: 'Instrument Sans', sans-serif !important;
}

/* --- AUDIO --- */
.gradio-container audio, .gradio-container .audio {
    width: 100% !important;
    max-width: 100% !important;
}
.result-wrap audio { filter: sepia(0.2) saturate(1.1); }

/* --- TEMPLATES chips : plus petits, plus élégants --- */
.templates-row {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 0.4rem !important;
    margin-bottom: 1rem !important;
    width: 100% !important;
}
.template-chip, .template-chip > button {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    padding: 0.45rem 0.95rem !important;
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 100px !important;
    color: var(--text-secondary) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    min-height: auto !important;
    font-weight: 500 !important;
    flex: 0 0 auto !important;
    width: auto !important;
}
.template-chip:hover, .template-chip > button:hover {
    border-color: var(--amber) !important;
    color: var(--amber-glow) !important;
    background: rgba(232, 165, 74, 0.06) !important;
    transform: translateY(-1px);
}

/* --- GENERATE : bouton cuivre lumineux --- */
button.primary, #generate-btn {
    background: linear-gradient(135deg, var(--amber) 0%, var(--crimson) 100%) !important;
    color: #1a0f04 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-size: 0.92rem !important;
    border: none !important;
    border-radius: 14px !important;
    min-height: 62px !important;
    box-shadow: 0 10px 30px -8px rgba(232, 165, 74, 0.35),
                0 1px 0 rgba(255, 220, 170, 0.4) inset !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}
button.primary:hover:not(:disabled), #generate-btn:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 40px -4px rgba(232, 165, 74, 0.5),
                0 1px 0 rgba(255, 220, 170, 0.4) inset !important;
}
button.primary::before, #generate-btn::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transform: translateX(-100%);
    transition: transform 0.6s ease;
}
button.primary:hover::before, #generate-btn:hover::before {
    transform: translateX(100%);
}
button.primary:disabled, #generate-btn:disabled {
    background: var(--bg-elevated) !important;
    color: var(--text-dim) !important;
    cursor: not-allowed !important;
    box-shadow: inset 0 0 0 1px var(--border) !important;
    border: none !important;
    opacity: 1 !important;
}

/* Secondary buttons (regénérer, download, save drive) */
button.secondary, .gradio-container button:not(.primary):not(#generate-btn):not(.template-chip):not(.template-chip > button) {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    padding: 0.6rem 1rem !important;
    min-height: auto !important;
}
button.secondary:hover:not(:disabled) {
    border-color: var(--border-hot) !important;
    color: var(--amber-glow) !important;
    background: rgba(232, 165, 74, 0.04) !important;
}

/* --- ACCORDION (réglages avancés) --- */
.gradio-container details > summary {
    font-family: 'Fraunces', serif !important;
    font-style: italic !important;
    font-size: 0.88rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: var(--text-secondary) !important;
    font-weight: 400 !important;
    cursor: pointer;
    padding: 0.6rem 0 !important;
}
.gradio-container details > summary:hover { color: var(--amber-glow) !important; }

/* --- SLIDER --- */
.gradio-container input[type="range"] {
    accent-color: var(--amber) !important;
}
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

/* --- RESULT WRAP --- */
.result-wrap {
    margin-top: 1.5rem;
    padding: 1.2rem;
    background: linear-gradient(135deg, rgba(232, 165, 74, 0.03), transparent 60%);
    border: 1px solid rgba(232, 165, 74, 0.1);
    border-radius: 14px;
}
.result-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
}
.result-actions > * { flex: 1 1 auto; min-width: 0; }

/* --- CHAR COUNTER --- */
.char-counter {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: var(--text-dim);
    text-align: right;
    margin-top: -0.5rem;
}

/* --- HISTORY --- */
.history-section { margin-top: 3.5rem; }
.history-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(1.3rem, 3vw, 1.8rem);
    font-weight: 400;
    font-style: italic;
    color: var(--amber);
    margin: 0 0 1.2rem;
    display: flex;
    align-items: baseline;
    gap: 0.9rem;
    font-variation-settings: "SOFT" 100, "WONK" 1;
}
.history-title .ornament {
    color: var(--amber-dim);
    font-size: 0.68rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    font-style: normal;
    font-weight: 600;
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
    padding: 3rem 1.5rem;
    color: var(--text-dim);
    font-family: 'Fraunces', serif;
    font-size: 1.05rem;
    line-height: 1.6;
    border: 1px dashed var(--border);
    border-radius: 16px;
    background: rgba(232, 165, 74, 0.015);
    font-style: italic;
}
.history-empty em {
    color: var(--amber-dim);
    font-weight: 400;
}
.history-list { display: flex; flex-direction: column; gap: 0.7rem; }
.history-item {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    transition: all 0.25s ease;
    position: relative;
}
.history-item::before {
    content: '';
    position: absolute;
    left: 0;
    top: 1rem;
    bottom: 1rem;
    width: 2px;
    background: var(--amber-dim);
    border-radius: 2px;
    opacity: 0.5;
}
.history-item:hover {
    border-color: var(--border-hot);
    transform: translateX(2px);
}
.history-item:hover::before { opacity: 1; background: var(--amber); }
.history-meta {
    display: flex;
    gap: 0.9rem;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    color: var(--text-dim);
    flex-wrap: wrap;
}
.history-time { color: var(--amber-dim); }
.history-voice { color: var(--amber); font-weight: 600; }
.history-speed {
    margin-left: auto;
    padding: 0.15rem 0.55rem;
    background: rgba(232, 165, 74, 0.08);
    border-radius: 4px;
    color: var(--amber);
}
.history-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 0.6rem;
    line-height: 1.45;
}
.history-audio { width: 100%; height: 36px; }

/* --- FOOTER --- */
footer { display: none !important; }
.custom-footer {
    margin-top: 4rem;
    padding-top: 2rem;
    text-align: center;
    border-top: 1px solid var(--border);
}
.footer-ornament {
    color: var(--amber-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.5em;
    margin-bottom: 0.9rem;
    opacity: 0.7;
}
.footer-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 0.9rem;
    color: var(--text-dim);
}
.footer-text strong {
    color: var(--text-secondary);
    font-weight: 600;
    font-style: normal;
    letter-spacing: 0.01em;
}
.footer-heart { display: inline-block; animation: heartbeat 1.8s ease-in-out infinite; }

/* --- SPLASH --- */
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
    animation: heartbeat 1.4s ease-in-out infinite;
    position: relative;
}
.splash-text {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 1.15em;
    color: var(--text-secondary);
    margin-bottom: 0.3em;
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
@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.15); }
}

/* Markdown inside .block : hairline nulle */
.gradio-container .prose, .gradio-container .markdown {
    color: var(--text-secondary) !important;
}
.gradio-container .prose em { color: var(--text-dim); }
"""

HERO_WAVE_SVG = """
<div class='hero-wave'>
  <svg viewBox='0 0 1200 80' preserveAspectRatio='none'>
    <path d='M0,40 Q150,10 300,40 T600,40 T900,40 T1200,40' stroke-opacity='0.8'/>
    <path d='M0,50 Q150,20 300,50 T600,50 T900,50 T1200,50' stroke-opacity='0.5'/>
    <path d='M0,30 Q150,60 300,30 T600,30 T900,30 T1200,30' stroke-opacity='0.3'/>
  </svg>
</div>
"""


TEMPLATES = [
    ("🎬 Intro TikTok", "Salut tout le monde, bienvenue sur ma chaîne ! Aujourd'hui on va parler de "),
    ("🔚 Outro", "Voilà pour aujourd'hui. N'oubliez pas de liker et de vous abonner. À très vite !"),
    ("😂 Réaction", "Attendez attendez, j'ai vu ça sur internet et je peux pas, faut que je vous le raconte."),
    ("🎙️ Présentation", "Bonjour, je m'appelle Nordine et aujourd'hui je vais vous présenter "),
]


# ============================================================================
# STATE utilitaire (tmp files alive pour l'historique)
# ============================================================================

_history_paths: list = []


def _prune_history_tmps(active_paths: list[str]) -> None:
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
    if not history:
        return (
            "<div class='history-section'>"
            + _HISTORY_HEADING
            + "<div class='history-empty'>"
              "Rien dans la mixtape pour le moment.<br>"
              "<em>Tes pistes s'accumuleront ici au fur et à mesure.</em>"
              "</div>"
            + "</div>"
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
        "<div class='history-section'>"
        + _HISTORY_HEADING
        + f"<div class='history-list'>{''.join(items)}</div>"
        + "</div>"
    )


def _section_label(num: str, title: str) -> str:
    return (
        f"<div class='section-label'>"
        f"<span class='num'>{num}</span>"
        f"<span class='title'>{title}</span>"
        f"</div>"
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
        # Splash
        gr.HTML(
            """
            <div class='splash-overlay'>
              <div class='splash-hearts'>❤️</div>
              <div class='splash-text'>Fait avec amour par</div>
              <div class='splash-name'>Aghiles A MANSEUR</div>
            </div>
            """
        )

        # Decorative background (gradient blobs)
        gr.HTML(
            """
            <div class='bg-decor'>
              <div class='blob blob-1'></div>
              <div class='blob blob-2'></div>
              <div class='blob blob-3'></div>
            </div>
            """
        )

        # --- HERO ---
        gr.HTML(
            f"""
            <div class='hero'>
              <div class='hero-badge'>voice studio · 2026</div>
              <h1 class='hero-title'>Le Studio Vocal<em>de Nordine</em></h1>
              <p class='hero-sub'>Clone n'importe quelle voix.<br>Dis-lui ce que tu veux.</p>
              {HERO_WAVE_SVG}
            </div>
            """
        )

        # --- MAIN GRID : 2 colonnes sur desktop, stack sur mobile ---
        with gr.Row(elem_classes=["main-grid"]):
            # ============================================================
            # COL 1 : SETUP DE LA VOIX
            # ============================================================
            with gr.Column(elem_classes=["col-setup"]):
                with gr.Column(elem_classes=["section"]):
                    gr.HTML(_section_label("01", "la voix"))

                    voice_mode = gr.Radio(
                        choices=["Préchargée", "Uploader une nouvelle"],
                        value="Préchargée",
                        show_label=False,
                        container=False,
                    )
                    voice_dropdown = gr.Dropdown(
                        choices=[],
                        label="Ta banque",
                        visible=True,
                        container=False,
                    )
                    voice_preview = gr.Audio(
                        label="Aperçu",
                        interactive=False,
                        visible=True,
                        elem_id="voice-preview",
                        elem_classes=["preview-audio"],
                        show_download_button=False,
                        show_share_button=False,
                        container=False,
                    )
                    with gr.Group(visible=False, elem_classes=["upload-group"]) as upload_group:
                        upload_name = gr.Textbox(
                            label="Comment tu l'appelles ?",
                            placeholder="ex: zidane, ma mère, ...",
                            container=False,
                        )
                        upload_file = gr.File(
                            label="Ton échantillon audio",
                            file_types=[".wav", ".mp3"],
                            elem_classes=["upload-zone"],
                            container=False,
                        )
                        gr.Markdown(
                            "*Une seule personne, 10–30 secondes, pas de musique.*"
                        )
                        upload_btn = gr.Button(
                            "Ajouter à la banque",
                            interactive=False,
                            size="sm",
                        )
                        upload_status = gr.Markdown(visible=False)

            # ============================================================
            # COL 2 : ZONE DE CRÉATION
            # ============================================================
            with gr.Column(elem_classes=["col-create"]):
                # --- Templates + Texte ---
                with gr.Column(elem_classes=["section"]):
                    gr.HTML(_section_label("02", "ton texte"))

                    with gr.Row(elem_classes=["templates-row"]):
                        template_btns = [
                            gr.Button(label, elem_classes=["template-chip"], size="sm")
                            for label, _ in TEMPLATES
                        ]

                    text_input = gr.Textbox(
                        show_label=False,
                        lines=5,
                        max_lines=10,
                        placeholder="Salut les gars, aujourd'hui on va parler de...",
                        container=False,
                    )
                    char_count = gr.HTML(
                        f"<div class='char-counter'>0 / {config.MAX_TEXT_LENGTH}</div>"
                    )

                    with gr.Accordion("Réglages avancés", open=False):
                        speed_slider = gr.Slider(
                            minimum=0.7,
                            maximum=1.3,
                            value=1.0,
                            step=0.05,
                            label="Vitesse de lecture",
                            info="1.0 = naturel · < 1 = ralenti · > 1 = accéléré",
                        )

                # --- Bouton générer ---
                generate_btn = gr.Button(
                    "Générer la piste",
                    variant="primary",
                    elem_id="generate-btn",
                    interactive=False,
                )

                # --- Résultat ---
                with gr.Column(elem_classes=["result-wrap"]):
                    output_audio = gr.Audio(
                        label="La dernière piste",
                        interactive=False,
                        container=False,
                    )
                    with gr.Row(elem_classes=["result-actions"]):
                        regenerate_btn = gr.Button("🔄 Regénérer", visible=False, size="sm")
                        download_btn = gr.DownloadButton("⬇️ Télécharger", visible=False, size="sm")
                        save_drive_btn = gr.Button("💾 Sauver", visible=False, size="sm")
                    save_status = gr.Markdown(visible=False)

        # --- HISTORIQUE : full-width sous les 2 colonnes ---
        history_html = gr.HTML(_render_history_html([]))

        # States
        last_audio_state = gr.State(value=None)
        last_voice_state = gr.State(value=None)
        last_voice_id_state = gr.State(value=None)
        last_text_state = gr.State(value=None)
        last_speed_state = gr.State(value=1.0)
        history_state = gr.State(value=[])

        # ====================================================================
        # HANDLERS (logique inchangée)
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
            return gr.Button(interactive=bool(voice_id) and _is_text_valid(text))

        @_log_errors
        def on_voice_selected(voice_id, text):
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
            count = len(text or "")
            over = count > config.MAX_TEXT_LENGTH
            color = "var(--crimson)" if over else "var(--text-dim)"
            md = (
                f"<div class='char-counter' style='color:{color};'>"
                f"{count} / {config.MAX_TEXT_LENGTH}"
                f"</div>"
            )
            return md, _generate_btn_state(voice_id, text)

        text_input.change(
            on_text_change,
            inputs=[text_input, voice_dropdown],
            outputs=[char_count, generate_btn],
        )

        # Template chips : injectent le texte
        for btn, (_, template_text) in zip(template_btns, TEMPLATES):
            btn.click(lambda tpl=template_text: tpl, inputs=[], outputs=[text_input])

        # Upload button : activé que si fichier + nom OK
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
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                )
            all_voices = voices_mod.list_all()
            new_dropdown = gr.Dropdown(
                choices=[(voice.name, voice.id) for voice in all_voices],
                value=v.id,
            )
            return (
                gr.Markdown(f"✅ Voix **{v.name}** ajoutée", visible=True),
                new_dropdown,
                v.audio_path,
                _generate_btn_state(v.id, current_text),
                gr.Button(interactive=False),
            )

        upload_btn.click(
            on_upload,
            inputs=[upload_file, upload_name, text_input],
            outputs=[upload_status, voice_dropdown, voice_preview, generate_btn, upload_btn],
        )

        # Sanitization
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

            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_bytes)
            tmp.close()

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
                tmp.name,
                audio_bytes,
                voice.name,
                voice_id,
                text,
                speed,
                new_history,
                _render_history_html(new_history),
                gr.Button(visible=True),
                gr.DownloadButton(value=tmp.name, visible=True),
                gr.Button(visible=True),
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

        # --- Footer ---
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
