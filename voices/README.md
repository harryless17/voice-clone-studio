# Voix préchargées

Ce dossier contient les échantillons audio utilisés comme presets par défaut au premier lancement.

## Ajouter un preset

1. Trouver un extrait public (interview YouTube, conférence de presse, émission TV) de 10-30 secondes
2. Extraire l'audio en mono 22050 Hz WAV (outil : `ffmpeg -i input.mp4 -ac 1 -ar 22050 output.wav`)
3. S'assurer : une seule personne parle, pas de musique, pas de bruit de fond
4. Nommer le fichier `<slug>.wav` (minuscules, underscores, pas d'espaces)
5. Committer le fichier dans ce dossier

## Presets actuels

Aucun preset livré avec le repo. L'outil démarre vide — l'utilisateur uploade sa première voix lui-même via l'interface (radio "Uploader une nouvelle"). Quand il n'y a pas de voix, l'UI bascule automatiquement sur ce mode au chargement.

Tu peux ajouter des presets plus tard en suivant les étapes ci-dessus.

## Considérations légales

Si tu ajoutes des presets de personnes publiques, tu es responsable de leur usage. Privilégie des sources avec licence permissive (Common Voice de Mozilla, archives publiques) pour éviter les problèmes de droit voisin / copyright.
