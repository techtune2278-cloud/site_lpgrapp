"""Textes et sélection de l’abonnement libre, version du 21 octobre 2026."""
from datetime import date
import re

TITLE='Offrir un abonnement : livres pour enfants, grands auteurs'
DESCRIPTION="Offrez à un enfant dès 5 ans un abonnement à la collection : choisissez vos livres, groupez les envois. Carte et dédicace d'Hervélina ou Valérie."
H1='Offrir un abonnement à une collection de livres pour enfants'
INTRO="Offrez à un enfant, un petit-enfant ou un filleul les grands auteurs de la littérature française, un livre après l'autre. Vous choisissez les titres ; nous les envoyons au fil des parutions, avec une carte et une dédicace d'Hervélina ou de Valérie."
NEXT="Chaque titre annonce son mois de parution prévu. Un décalage d'un mois au plus est possible ; nous vous prévenons par e-mail. Si un titre a plus d'un mois de retard sur la date annoncée, vous pouvez l'annuler : nous vous remboursons son prix et son port. Votre livre part dans les 10 jours qui suivent sa parution. Le contenu sera en ligne à la parution : comme les dix premiers tomes, chaque livre contient la vie de l'auteur, un extrait, des rubriques culturelles et des activités."
LATER="Un titre plus lointain vous tente ? Réservez-le sans payer : nous vous écrivons quand sa date est confirmée, avec le lien de paiement. Vous pouvez renoncer à tout moment avant."
GROUP="Un envoi, c'est un colis. Plus il contient de livres, moins le port pèse. Mais pour les titres à paraître, grouper veut dire que le premier livre attend le suivant : votre premier livre partira à la parution du deuxième."
INCLUDED="Une carte et une dédicace d'Hervélina ou de Valérie. Les livres sont au prix habituel, le port est groupé selon le nombre de livres de chaque envoi."
GUARANTEES=['Un seul paiement, sans prélèvement récurrent.','Envoi en lettre suivie.','Droit de rétractation de 14 jours à compter de la réception du premier livre.',"Remboursement d'un titre qui aurait plus d'un mois de retard."]


def prepare_catalog(books):
    # Six prochains par défaut, sans transformer les Collectors non confirmés en préventes.
    future=sorted((b for b in books if not b['available'] and b['number'] not in [10,20,30]),key=lambda b:b['number'])
    explicit=[b for b in future if b.get('status')=='prochain']
    if len(explicit)>6:raise ValueError('Le catalogue contient plus de six prochains titres.')
    defaults=[b['number'] for b in future if not b.get('status')][:max(0,6-len(explicit))]
    for book in books:
        status='paru' if book['available'] else book.get('status') or ('prochain' if book['number'] in defaults else 'plus_tard')
        if status not in {'paru','prochain','plus_tard'}:raise ValueError('Statut de livre invalide : '+str(status))
        if status=='paru' and not book['available']:raise ValueError('Un livre paru doit avoir available=true.')
        month=book.get('release_month','')
        if month:
            if not re.fullmatch(r'\d{4}-\d{2}',month):raise ValueError('release_month attend AAAA-MM.')
            date.fromisoformat(month+'-01')
        book.update(status=status,release_month=month,has_page=bool(book['available'] or book.get('cover') or book.get('description','').strip()))
        book['subscription_payable']=bool(status=='paru' or (status=='prochain' and month))
    if sum(b['status']=='prochain' for b in books)>6:raise ValueError('Le catalogue contient plus de six prochains titres.')


def month_label(value):
    if not value:return 'Mois de parution à confirmer'
    names=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
    return names[int(value[5:])-1]+' '+value[:4]


def subscription_page(ctx):
    esc=ctx['esc'];books=ctx['books'];heading=ctx['heading']
    def para(value):return '<p>'+esc(value)+'</p>'
    def choices(status):
        result=''
        for book in books:
            if book['status']!=status:continue
            reserve=not book['subscription_payable']
            label=('Réserver — sans paiement' if reserve else 'Choisir')
            detail='Disponible tout de suite' if status=='paru' else (month_label(book['release_month']) if status=='prochain' else 'Réservation sans paiement')
            price=(' · '+str(book['price'])+' €') if book['number'] not in [10,20,30] or book['available'] else ''
            result+='<div class="subscription-book"><label><input type="checkbox" name="'+('reserve-title' if reserve else 'subscription-title')+'" value="'+str(book['number'])+'"><span><strong>'+esc(book['title'])+'</strong><small>'+esc(detail+price)+'</small><span>'+label+'</span></span></label>'
            if book['has_page']:result+='<a class="underlink" href="/livres/'+book['slug']+'/" target="_blank" rel="noopener noreferrer">Voir le livre ↗</a>'
            result+='</div>'
        return result or '<p>Aucun titre dans cette catégorie pour le moment.</p>'
    body='<section class="section gift-hero" id="abonnement"><div>'+heading('Offrir',H1)+para(INTRO)+'</div><img src="/assets/photos/enfant-lecture-fauteuil.png" alt="Une petite fille lit un livre de la collection dans un fauteuil" width="806" height="1069" loading="eager"></section>'
    body+='<section class="section copy-section"><h2>Comment ça marche</h2><ol class="brief-list">'+''.join('<li>'+esc(s)+'</li>' for s in ['Choisissez vos livres : des livres déjà parus, au choix, et jusqu’aux six prochains titres à paraître.',"Choisissez le nombre d’envois : plus vous groupez, moins vous payez de port.",'Indiquez le destinataire et, si vous le souhaitez, un mot pour la carte.',"Nous vous confirmons le montant par e-mail et vous envoyons un lien de paiement. Un seul paiement, sans prélèvement."] )+'</ol></section>'
    body+='<section class="section copy-section subscription"><form id="subscription-builder" action="/api/subscription" method="post"><h2 id="choisir-livres">Choisir vos livres</h2><fieldset><legend>Déjà parus</legend><p>Disponibles tout de suite. Chaque titre a sa fiche.</p><div class="subscription-book-list">'+choices('paru')+'</div></fieldset><fieldset><legend>Les six prochains titres</legend>'+para(NEXT)+'<p>Les titres dont le mois n’est pas encore confirmé peuvent être réservés sans paiement. Leur date sera confirmée par e-mail avant tout règlement.</p><div class="subscription-book-list">'+choices('prochain')+'</div></fieldset><fieldset><legend>À paraître, réservez le vôtre</legend>'+para(LATER)+'<div class="subscription-book-list">'+choices('plus_tard')+'</div></fieldset>'
    body+='<h2>Choisir le nombre d’envois</h2>'+para(GROUP)+'<div class="table-scroll"><table class="shipping-table"><thead><tr><th>Livres dans l’envoi</th><th>Port (France, lettre suivie)</th></tr></thead><tbody><tr><td>1 livre</td><td>4,50 €</td></tr><tr><td>2 ou 3 livres</td><td>7 €</td></tr><tr><td>4 à 6 livres</td><td>9 €</td></tr><tr><td>7 à 12 livres</td><td>11 €</td></tr><tr><td>Au-delà de 12 livres</td><td>Sur devis</td></tr></tbody></table></div><p>Exemples pour six livres à 15 € (90 €) : 6 envois, 117 € ; 3 envois de 2 livres, 111 € ; 2 envois de 3 livres, 104 €. Chaque livre à 9 € (Rimbaud, Hugo) fait baisser le total de 6 €.</p><label for="subscription-shipments">Nombre d’envois</label><select id="subscription-shipments" name="shipments" disabled><option value="0">Choisissez vos livres</option></select><p>Les livres sont répartis entre les colis aussi régulièrement que possible, dans l’ordre des parutions. La composition de chaque envoi est indiquée ci-dessous et sera confirmée avec vous.</p><div id="subscription-summary" class="subscription-summary" role="status" aria-live="polite"><p>Choisissez vos livres pour afficher le détail : livres, port, total.</p></div><div id="subscription-parcels"></div><p id="reservation-summary"></p>'
    body+='<h2>Ce qui est inclus</h2>'+para(INCLUDED)+'<h2>Délais et garanties</h2><ul class="brief-list">'+''.join('<li>'+esc(value)+'</li>' for value in GUARANTEES)+'</ul>'
    body+='''<fieldset><legend>Vos coordonnées</legend><div class="contact-form"><label>Votre nom<input name="nom" autocomplete="name" maxlength="120" required></label><label>Votre e-mail<input name="email" type="email" autocomplete="email" maxlength="254" required></label><label>Téléphone (facultatif)<input name="phone" type="tel" autocomplete="tel" maxlength="40"></label></div></fieldset><fieldset id="recipient-fields"><legend>Le destinataire</legend><div class="contact-form"><label>Prénom et nom du destinataire<input name="recipient_name" autocomplete="shipping name" maxlength="120" required></label><label>Adresse<input name="address" autocomplete="shipping address-line1" maxlength="200" required></label><label>Complément (facultatif)<input name="address_extra" autocomplete="shipping address-line2" maxlength="200"></label><label>Code postal<input name="postal_code" autocomplete="shipping postal-code" inputmode="numeric" pattern="[0-9]{5}" maxlength="5" required></label><label>Ville<input name="city" autocomplete="shipping address-level2" maxlength="120" required></label><label>Pays<input name="country" value="France" readonly></label></div><p>Pour une destination hors de France, contactez-nous pour un devis.</p><label>Un mot pour la carte (facultatif)<textarea name="card_message" maxlength="1000" rows="4"></textarea></label></fieldset><div class="contact-trap" aria-hidden="true"><label>Ne pas remplir<input name="website" tabindex="-1" autocomplete="off"></label></div><label class="contact-consent"><input type="checkbox" name="consent" required> J’accepte l’utilisation de ces informations pour traiter ma demande et préparer les envois au destinataire indiqué. <a href="/confidentialite/">Confidentialité</a>.</label><p id="subscription-availability" role="status">Vérification de la disponibilité de l’envoi…</p><button class="button primary" id="subscription-submit" type="submit" disabled>Envoyer ma demande</button><p id="subscription-result" role="status" aria-live="polite" tabindex="-1"></p><button class="button light" id="subscription-email" type="button">Préparer un e-mail</button><button class="button light" id="subscription-download" type="button">Télécharger mon récapitulatif</button><p>Vous ne payez rien sur cette page. Le montant et le calendrier sont confirmés par e-mail avant l’envoi du lien de paiement SumUp.</p><noscript><p>Activez JavaScript pour composer votre abonnement ou écrivez à <a href="mailto:contact@lesplusgrandsracontes.fr">contact@lesplusgrandsracontes.fr</a>.</p></noscript></form></section>'''
    return body
