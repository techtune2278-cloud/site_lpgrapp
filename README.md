# Les plus grands racontés aux plus petits — V1.2.0

Textes éditoriaux issus du document transmis le 20 octobre 2026, sans résumé. Guide d’installation et correspondance des contenus : MAJ_TEXTES_V1.2.md. Configuration du formulaire : PRIORITE_1.md.

## Fichiers

- textes-brief.json : source textuelle complète, non publiée dans dist.
- editorial_pages.py : contenu et mise en page des rubriques.
- build.py : générateur, navigation, pied de page et métadonnées.
- content.json : catalogue et couvertures.
- site-settings.json : liens de commande, tarifs et audio.
- site_features.py : formulaires, boutons, FAQ et audio.
- api/contact.js et lib/contact-service.js : envoi de messages via Brevo sur Vercel.
- dist/style.css et dist/app.js : style et interactions.

Générer : python build.py.
Voir localement : python -m http.server 8080 --bind 127.0.0.1 --directory dist
Puis http://127.0.0.1:8080.

Les fonctions serveur ne tournent pas avec le serveur Python. Tester l’envoi sur votre Vercel configuré. L’atelier reste local. Le MP3 n’est pas fourni ; le lecteur s’active à l’ajout de dist/assets/audio/moliere.mp3. Les identifiants Brevo sont à configurer dans Vercel, jamais dans les fichiers publics.

Les pages HTML et dist/content.json sont générés. Ne pas les modifier à la main. Les images et le catalogue existants sont conservés par l’installateur. Le build ne réécrit plus le README.

Tests :

    node --test tests/contact.test.js
    python -m unittest discover -s tests -p "test_*.py"

Le brouillon reste en noindex ; le domaine actuel utilisé dans les métadonnées est sitelpgrapp.vercel.app, configurable par site_url dans site-settings.json. Les pages légales et les points entre crochets restent à compléter.
