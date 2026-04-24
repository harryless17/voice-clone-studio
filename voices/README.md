# Voix préchargées

Ce dossier contient les échantillons audio utilisés comme presets par défaut au premier lancement.

## Ajouter un preset

1. Trouver un extrait public (interview YouTube, conférence de presse, émission TV) de 10-30 secondes
2. Extraire l'audio en mono 22050 Hz WAV (outil : `ffmpeg -i input.mp4 -ac 1 -ar 22050 output.wav`)
3. S'assurer : une seule personne parle, pas de musique, pas de bruit de fond
4. Nommer le fichier `<slug>.wav` (minuscules, underscores, pas d'espaces)
5. Committer le fichier dans ce dossier

## Presets actuels

- `zidane.wav` — extrait d'interview post-match (10s) *[à sourcer manuellement]*
- `jamel.wav` — extrait de stand-up (12s) *[à sourcer manuellement]*

## Considérations légales

Ces échantillons sont inclus à des fins de démonstration (fair-use). L'utilisateur final est responsable de l'usage qu'il fait des clones générés.
