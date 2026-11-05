# V1.8.0 — corrections et feuilletage du 5 novembre 2026

## Installation par copier-coller

Ce paquet contient le site complet. Aucun installateur ni fichier BAT n’est nécessaire.

1. Faites une copie de sauvegarde de votre dossier `C:\Techtune\Devt\Site Lpgrapp\Site lpgrapp` ailleurs sur le PC.
2. Depuis le dossier habituel, récupérez les changements que l’administration aurait publiés : `git pull --rebase`. Si Git signale des changements locaux ou un conflit, résolvez-le avant la copie ; n’utilisez pas de reset forcé.
3. Décompressez le ZIP ailleurs puis copiez **son contenu**, y compris `dist`, `api`, `lib`, `scripts` et `tests`, à la racine du projet, à côté du `content.json` existant. Acceptez le remplacement des fichiers. Ne remplacez pas le dossier complet par un nouveau dossier : votre `.git` et vos éventuels secrets locaux restent à leur place.
4. Le `content.json` livré reprend le catalogue lu dans votre dépôt GitHub le 5 novembre, y compris vos modifications administratives. Il ajoute les extraits et la couverture du Collector et confirme les trois salons demandés. Si vous avez modifié le catalogue après cette préparation, conservez aussi votre nouveau fichier pour reprendre ces seules différences.
5. Dans le dossier du projet, lancez :

```cmd
python build.py
```

La version doit afficher **V1.8.0**. Le paquet inclut désormais un `package-lock.json` sans dépendance npm : `npm ci` peut aussi être utilisé, mais n’est pas nécessaire pour lancer directement le générateur Python si Pillow est déjà installé.

Après vérification :

```cmd
git add -A -- . ":(exclude)*.zip"
git commit -m "V1.8.0 - Feuilletage, corrections et administration"
git push
```

Dans Vercel, ouvrir le projet **sitelpgrapp**, relié à **site_lpgrapp**, et vérifier le nouveau commit et son statut Ready en production.

## Points du cahier des charges traités

- Citation : espace insécable entre le tiret et Amélie, pour ne pas laisser le tiret seul. Citation retirée du héros d’accueil, conservée sur les pages Presse et Professionnels.
- Accueil : arrêt avant « Ils parlent de nous ». Les sections presse, commande et newsletter ne sont plus répétées sur l’accueil. Les liens vers ces pages restent disponibles.
- Achat du menu et du héros : boutique SumUp en nouvel onglet ; le catalogue reste accessible via « La collection ».
- Catalogue : Collectors exclus de la grille principale et réunis dans leur rubrique. Collector n° 1 / tome 10 disponible à **16,50 €**, nouvelle couverture et fiche. La couverture ne donne pas lieu à un lien SumUp produit inventé : faute d’URL produit renseignée, le bouton ouvre la boutique.
- « Me prévenir » : formulaire de contact avec le titre prérempli, et non abonnement.
- Retrait du nom John du texte publié et des données structurées. Retrait de « Disponible chez votre libraire » et de la section « Dans ce livre » des fiches.
- « Où nous trouver ? » : point d’interrogation au menu, boutique SumUp en premier, puis libraires, salons plus compacts. Suppression de la phrase Dilicom sur cette page. Les dates des trois salons sont confirmées conformément à votre nouvelle précision ; les salles non renseignées ne sont pas inventées.
- Professionnels : titre élargi ; textes librairies, bibliothèques, écoles/Alliances, musées et salons repris. Le tableau ISBN est retiré. La nouvelle demande de dépôt-vente pour les musées remplace la précédente consigne de vente ferme. Suppression du bloc générique À télécharger ; le vrai PDF reste proposé dans la rubrique Alliances françaises/écoles. Retrait de la phrase « plus de 12 livres » au-dessus du formulaire et de « photos des auteurs… ».
- Abonnement : introduction et étapes fournies ; même processus dans la FAQ. Les quantités, colis et totaux restent contrôlés sur le serveur. Une liste explicite des mois remplace le champ `month` pour les clients : décembre peut être sélectionné directement sur mobile. Les dates proposées ne précèdent ni le mois courant ni la parution connue.
- Formulaires : les phrases de brouillon sont retirées. Sans service Brevo opérationnel, le bouton ouvre une demande préparée dans la messagerie du visiteur ; il faut **envoyer ce message depuis cette messagerie** pour le transmettre. Le récapitulatif téléchargeable reste proposé. Aucune réception n’est annoncée si l’envoi direct n’est pas confirmé.
- Administration : les identifiants/adresses des nouveaux éléments sont calculés automatiquement ; les adresses existantes restent stables. Retrait des champs Présentation intégrale, chemins de couverture et d’extraits. Couverture, photo de salon et quatre pages à feuilleter s’ajoutent par sélection de fichiers, avec compression et aperçu. Les rubriques modifiées sont enregistrées ensemble. Le retrait du dernier livre ou d’un salon reste publiable même si la liste est vide. Les anciennes fiches générées sont supprimées à la reconstruction. Retirer un extrait ou une couverture ne restaure plus automatiquement l’ancienne image.

## Feuilletage : 40 pages, dix livres

Quatre images WebP sont intégrées pour Rimbaud, Hugo, Ségur, Proust, Sand, Verne, Zola, Balzac, Colette et Molière. Les doubles pages de Rimbaud, Hugo, Balzac et Molière sont séparées en deux pages, dans l’ordre. Aucune page n’est inventée ; aucune page de Collector n’était fournie.

Lecture par flèches, vignettes, clavier ou balayage horizontal ; agrandissement de la page dans une fenêtre qui se ferme aussi par Échap. Sans JavaScript, les liens vers les pages restent accessibles. Aucun lecteur PDF ni bibliothèque externe lourde n’est ajouté. Les images sont dans `dist/assets/extraits/<adresse-du-livre>/` et les références dans `content.json`.

## SEO et indexation temporaire

Le document demande de suspendre l’indexation pendant les ajustements : les pages sont donc générées avec **noindex,nofollow**. Les titres, descriptions, canoniques, cartes de partage et données structurées restent présents ; le sitemap est vide tant que l’indexation est suspendue. Le robots.txt laisse le robot lire les pages afin qu’il voie le noindex.

Dans Vercel, ajouter `INDEXATION_ENABLED=false` pendant cette phase. Pour autoriser l’indexation finale : `INDEXATION_ENABLED=true`, régler `SITE_URL` sur le domaine principal **déjà connecté**, puis redéployer. En développement, ne pas laisser une ancienne valeur `INDEXATION_ENABLED=true` écraser le réglage de préparation. Les prévisualisations Vercel restent hors indexation même si la production est activée. La page d’administration et les pages techniques restent hors indexation.

Les textes alternatifs sont sobres et propres à chaque couverture, sans ajouter de crédit supprimé. La répétition d’un CTA n’est pas présentée comme une pénalité SEO démontrée. Les propositions du document sont appliquées pour clarifier le parcours, sans promettre une position dans Google. Références : https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag ; https://developers.google.com/search/docs/crawling-indexing/block-indexing?hl=fr.

## Publication depuis l’administration

Après **Publier**, l’administration confirme d’abord le commit GitHub, puis vérifie `/publication.json` : elle affiche « Publication terminée » seulement quand le site sert la nouvelle version du catalogue. Si elle ne la voit pas après environ trois minutes, elle demande de contrôler Vercel au lieu d’annoncer un succès fictif.

Si les commits de l’administration n’entraînent pas de déploiement malgré une connexion correcte :

1. Dans Vercel **sitelpgrapp**, Settings → Git → Deploy Hooks : créer un hook pour `main`.
2. Copier son URL dans la variable serveur `ADMIN_VERCEL_DEPLOY_HOOK`, environnement Production. Garder cette URL secrète.
3. Redéployer une fois. Les publications suivantes pourront demander explicitement une reconstruction après leur commit.

Ce hook est facultatif si l’intégration Git fonctionne. Il ne remplace pas les autorisations requises pour le dépôt, l’auteur du commit et le projet Vercel. Il ne garantit pas qu’un build défaillant réussisse. Guide officiel : https://vercel.com/docs/deploy-hooks.

## Contrôles et limites

Compilation et tests Python/Node exécutés. Suppressions de livres, de salons et de points de vente contrôlées côté serveur, y compris listes vides et modification simultanée de plusieurs rubriques. Reconstruction réelle testée après retrait des anciennes fiches et ajout d’images intégrées. Interface vérifiée dans Chrome : sélection du mois de décembre, mise à jour du port, pages et agrandissement, ajout d’une couverture et de quatre extraits, photo de salon, sauvegarde simulée de plusieurs rubriques.

Les tests des API utilisent des fournisseurs simulés : aucun message réel, aucune facture et aucun commit n’ont été envoyés vers votre propre dépôt par ces tests. Les essais de réception réelle nécessitent vos variables Brevo dans Vercel. L’aperçu privé statique ne fait pas tourner les fonctions Vercel ; l’administration réelle s’utilise sur votre domaine Vercel configuré.
