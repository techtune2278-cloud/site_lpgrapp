# Informations administratives à compléter — 5 novembre 2026

## Pour activer l’administration de Valérie

Dans Vercel → Settings → Environment Variables → Production :

- `ADMIN_PASSWORD` : une phrase de passe personnelle d’au moins 16 caractères. Ne pas la transmettre dans ChatGPT ni l’écrire dans le dépôt.
- `ADMIN_SESSION_SECRET` : une valeur aléatoire d’au moins 32 caractères. Exemple de génération locale : `node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"`.
- `ADMIN_GITHUB_TOKEN` : un jeton GitHub à accès fin, limité au dépôt du site, avec permission **Contents: Read and write**. Ni accès aux autres dépôts, ni permission de gérer les workflows ne sont nécessaires.
- `ADMIN_GITHUB_REPOSITORY` : `techtune2278-cloud/site_lpgrapp`.
- `ADMIN_GITHUB_BRANCH` : `main`.

Puis redéployer et ouvrir `/administration/`. Ce compte est destiné à **Valérie Lemoine**, administratrice unique. Le mot de passe n’est pas enregistré dans le navigateur ; une session sécurisée et temporaire est créée côté serveur. L’espace n’apparaît pas dans les menus publics et n’est pas indexable.

Un enregistrement crée une modification de `content.json` dans GitHub. Le déploiement automatique Vercel doit donc être actif pour ce dépôt et cette branche. Le succès GitHub n’est pas présenté comme un déploiement déjà terminé : attendre le succès Vercel puis actualiser le site. Les modifications concurrentes sont refusées pour éviter d’écraser un changement plus récent. Les limites de tentatives de connexion sont appliquées par instance ; une protection supplémentaire du chemin `/api/admin` peut être configurée dans le pare-feu Vercel si nécessaire.

## Pour les messages et accusés de réception

- Vérifier `BREVO_API_KEY`, `CONTACT_FROM_EMAIL` (expéditeur validé) et `CONTACT_TO_EMAIL=contact@lesplusgrandsracontes.fr`.
- Vérifier que la boîte contact existe et reçoit les messages.
- Faire une demande réelle sur Vercel : réception vendeur, accusé client et pièce jointe CGV.
- Vérifier la délivrabilité et l’authentification du domaine expéditeur dans Brevo.
- Pour l’infolettre facultative : `BREVO_NEWSLETTER_LIST_ID` et `BREVO_DOI_TEMPLATE_ID`, modèle de double confirmation et désabonnement dans les campagnes. Un échec d’inscription à la newsletter ne fait pas échouer la demande de livres.

## Entreprise et documents légaux

- Confirmer les références exactes d’immatriculation et le code APE sur l’avis Sirene. Les notes à confirmer ne sont pas publiées.
- Valérie Lemoine et Hervélina Vyskoc restent les deux auteurs. Les informations juridiques de l’EI et la directrice de publication sont reprises des documents fournis (Valérie Lemoine) : rectifier si les documents administratifs officiels indiquent autre chose.
- Le téléphone 06 18 37 69 14 est repris des mentions légales jointes ; vérifier qu’il peut être diffusé publiquement.
- Conserver le justificatif d’adhésion MED CONSO DEV, sa référence, sa date d’effet et la couverture de l’activité. Les coordonnées publiques du médiateur ont été vérifiées sur son site : Centre d’Affaires Stéphanois, Immeuble l’Horizon, Esplanade de France, 3 rue J. Constant Milleret, 42000 Saint-Étienne — https://www.medconsodev.eu/.
- Faire valider la version finale des CGV, notamment la rétractation à réception du dernier bien pour cette offre, les livres dédicacés, les retours et la part de port remboursable en cas d’annulation partielle. Aucun droit de rétractation n’a été supprimé.
- Confirmer les durées de conservation, les rôles de Vercel/Brevo/OVH/GitHub/SumUp, les garanties contractuelles et transferts éventuels dans le registre RGPD. La durée de trois ans des demandes sans suite reprend le fonctionnement antérieur et reste à valider.
- Vérifier les paramètres réels des outils d’audience ; le code n’ajoute pas de traceur publicitaire ni de carte/vidéo tierce intégrée. La session d’administration est un cookie nécessaire réservé à l’admin.

## Facturation et exploitation

- Préparer le modèle de facture avec numérotation, mentions fiscales, coordonnées bancaires et référence à utiliser pour le virement. Le RIB doit figurer sur la facture, pas dans les fichiers publics du site.
- Facture valable 15 jours, contrat conclu au paiement intégral, puis confirmation manuelle avec l’échéancier. La génération de facture, le contrôle du virement, les relances, remboursements et numéros de suivi ne sont pas automatisés par cette mise à jour.
- Confirmer les délais opérationnels : livres disponibles sous cinq jours ouvrés pour un départ immédiat ; titres à paraître dans les dix jours suivant leur parution ou au mois ultérieur choisi.
- Confirmer la version finale de la carte et la façon de réaliser les dédicaces.
- Valider le mois de disponibilité des Collector n° 1 et 2 et les mois d’avril/octobre 2027 saisis ; ne marquer un livre comme paru qu’à sa disponibilité réelle.

## Événements et autorisations

- Les dates des trois salons sont confirmées selon votre cahier des charges du 4 novembre. Compléter les salles/adresses depuis l’administration sans modifier les dates confirmées.
- Tout événement de test conservé dans votre catalogue peut être retiré avec Retirer cet élément puis Publier.
- Conserver les accords écrits pour la citation d’Amélie Nothomb, la photographie de l’enfant, les photos et les reproductions de presse.

## Domaine et référencement

- Connecter/valider le domaine principal dans Vercel, régler `SITE_URL` sur l’URL réellement connectée puis redéployer. Les tentatives de consultation du domaine officiel n’ont pas permis d’en vérifier la connexion dans cet environnement ; le domaine existant est donc conservé dans le paramétrage.
- Vérifier Search Console, Bing, le sitemap et l’indexation après le déploiement public.
- Confirmer les anciennes redirections du site Les Compagnons de Route et préserver les QR codes imprimés.
- Mesurer les performances mobiles sur le site Vercel avec vos médias réels ; aucun score Lighthouse n’est inventé.

## Ajouts V1.8

- `INDEXATION_ENABLED=false` pendant les ajustements ; passer à `true` puis redéployer pour le lancement du référencement. Contrôler aussi `SITE_URL`.
- Facultatif si les commits admin ne déclenchent pas Vercel : `ADMIN_VERCEL_DEPLOY_HOOK`, URL secrète créée dans les paramètres Git de **sitelpgrapp** pour `main`. Voir MAJ_V1.8.md.
