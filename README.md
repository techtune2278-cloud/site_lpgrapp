# Les plus grands racontés aux plus petits — V1.1.0

Site vitrine statique et formulaire serveur Vercel. Les détails de cette mise à jour et les réglages du formulaire sont dans PRIORITE_1.md.

## Développement

- Catalogue : content.json (descriptions, prix, couvertures, commande_url).
- Réglages : site-settings.json (boutique, formules, tarifs et audio).
- Modèles généraux : build.py ; blocs priorité 1 : site_features.py.
- Style et interactions : dist/style.css et dist/app.js.
- Fonction Vercel : api/contact.js ; service d’envoi : lib/contact-service.js.

Générer : python build.py (ou python3 selon le poste).
Voir localement : python -m http.server 8080 --bind 127.0.0.1 --directory dist
Puis http://127.0.0.1:8080. Le formulaire réel s’essaie sur Vercel : le serveur Python ne lance pas les fonctions Node.

Après modification : générer, git add ., git commit, git push. Le déploiement Vercel utilise dist sans construction automatique. Les fichiers HTML générés sont à conserver dans Git. Ne pas modifier directement dist/content.json ni les index.html générés.

## Fonctionnement

Dix liens directs SumUp ; FAQ et livraison ; formulaire prêt à activer avec Brevo ; lecteur Molière prêt à recevoir le fichier. Les offres sans URL dédiée restent des demandes de contact. Sans clé et expéditeur configurés, aucun envoi n’est annoncé. Le lecteur ne s’affiche que si le MP3 existe ou si son URL est renseignée.

Les contenus et droits manquants, les conditions cadeaux/abonnement et les pages légales restent à compléter. Les instructions noindex sont conservées pour le brouillon. L’atelier reste un outil local avec import/export, sans publication directe ni authentification.

## Tests

node --test tests/contact.test.js
python -m unittest discover -s tests -p "test_*.py"

Les tests d’envoi utilisent un prestataire simulé. Aucun e-mail réel n’est envoyé par les tests.
