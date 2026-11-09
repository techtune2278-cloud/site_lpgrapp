"""Textes et sélection de l’abonnement libre, version du 21 octobre 2026."""
from datetime import date
import re

TITLE='Offrir un abonnement : livres pour enfants, grands auteurs'
DESCRIPTION="Offrez à un enfant dès 5 ans un abonnement à la collection : choisissez vos livres, recevez-en un par mois d’envoi. Carte et dédicace d'Hervélina ou Valérie."
H1='Offrir un abonnement à une collection de livres pour enfants'
INTRO="Choisissez les livres à offrir : nous les expédions au rythme d’un livre par mois, sans envoi avant la parution. Une carte personnalisée et une dédicace d’Hervélina ou de Valérie sont comprises."
NEXT="Les livres à paraître sont programmés à partir de leur mois de parution prévu."
LATER="Un titre plus lointain vous tente ? Réservez-le sans payer : nous vous écrivons quand sa date est confirmée, avec le lien de paiement. Vous pouvez renoncer à tout moment avant."
GROUP="Un livre est expédié par mois d’envoi."
INCLUDED="Une carte et une dédicace d’Hervélina ou de Valérie. Les livres sont au prix habituel, avec des frais d’expédition par envoi."
GUARANTEES=['Un seul paiement par virement après réception de la facture, sans prélèvement récurrent.','Envoi en lettre suivie.','Droit de rétractation de 14 jours à compter de la réception du dernier livre.',"Remboursement d'un titre qui aurait plus d'un mois de retard."]


def prepare_catalog(books):
    for book in books:
        status='paru' if book['available'] else ('prochain' if book.get('release_month') else 'plus_tard')
        if status not in {'paru','prochain','plus_tard'}:raise ValueError('Statut de livre invalide : '+str(status))
        if status=='paru' and not book['available']:raise ValueError('Un livre paru doit avoir available=true.')
        month=book.get('release_month','')
        if month:
            if not re.fullmatch(r'\d{4}-\d{2}',month):raise ValueError('release_month attend AAAA-MM.')
            date.fromisoformat(month+'-01')
        book.update(status=status,release_month=month,has_page=bool(book['available'] or book.get('cover') or book.get('description','').strip()))
        book['subscription_payable']=bool(status=='paru' or (status=='prochain' and month))



def month_label(value):
    if not value:return 'Mois de parution à confirmer'
    names=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
    return names[int(value[5:])-1]+' '+value[:4]


def subscription_steps(settings=None):
    settings=settings or {'min_books':3,'max_books':12}
    return [
        ('Sélectionnez vos livres.',f"Choisissez de {settings['min_books']} à {settings['max_books']} titres disponibles ou à paraître, à raison d’un exemplaire par titre. Un ouvrage ne peut pas partir avant sa parution prévue."),
        ("Consultez les envois prévus.","Le calendrier est établi automatiquement : un livre par mois d’envoi, à partir de sa parution. Les mois affichés ne sont pas modifiables."),
        ('Personnalisez votre cadeau.',"Indiquez le prénom et l'adresse du destinataire, puis rédigez votre mot d'accompagnement pour la carte."),
        ('Envoyez votre demande sans paiement.',"Nous vérifions les informations et adressons une facture valable 15 jours. Le paiement se fait en une fois par virement ; le contrat est conclu à réception du paiement.")
    ]


def subscription_page(ctx):
    esc=ctx['esc'];heading=ctx['heading'];books=ctx['books'];settings=ctx['catalog'].get('subscription',{'min_books':3,'max_books':12})
    body='<section class="section gift-hero" id="abonnement"><div>'+heading('Offrir',H1)+'<p>'+esc(INTRO)+'</p></div><img src="/assets/photos/enfant-lecture-fauteuil.png" alt="Une petite fille lit un livre de la collection dans un fauteuil" width="806" height="1069" loading="eager"></section>'
    body+='<section class="section copy-section"><h2>Comment ça marche ?</h2><ol class="brief-list">'+''.join('<li><strong>'+esc(title)+'</strong> '+esc(text)+'</li>' for title,text in subscription_steps(settings))+'</ol><p>💡 Une demande spéciale ? (date précise, événement particulier, calendrier sur mesure...) Pour plusieurs exemplaires d’un même titre ou une demande particulière, <a href="/contact/?sujet=Abonnement%20sur%20mesure">contactez l’éditeur</a>.</p></section>'
    body+='<section class="section copy-section subscription"><form id="subscription-builder" action="/api/subscription" method="post"><h2 id="choisir-livres">Choisir vos livres</h2>'
    for available,label in [(True,'Livres déjà parus'),(False,'Titres à paraître et Collectors')]:
        body+='<fieldset><legend>'+label+'</legend><div class="subscription-book-list">'
        for book in books:
            if book['available']!=available:continue
            reserve=not book['subscription_payable'];detail='Disponible' if available else month_label(book['release_month']);name='reserve-title' if reserve else 'subscription-title'
            body+='<div class="subscription-book"><label><input type="checkbox" name="'+name+'" value="'+str(book['number'])+'"><span><strong>'+esc(book['title'])+'</strong><small>'+esc(detail)+' · '+str(book['price']).replace('.',',')+' €</small><span>'+('Réserver sans paiement' if reserve else 'Choisir')+'</span></span></label>'
            if book['has_page']:body+='<a href="/livres/'+book['slug']+'/" target="_blank" rel="noopener noreferrer">Voir le livre ↗</a>'
            body+='</div>'
        body+='</div></fieldset>'
    body+='<h2>Envois prévus</h2><p>Un livre par mois d’envoi, en commençant par les livres disponibles. Aucun titre ne part avant sa parution. Si aucun livre sélectionné n’est encore paru, le calendrier attend la prochaine parution.</p><ol id="subscription-schedule" aria-label="Mois d’expédition prévus"></ol><p>Le calendrier est prévisionnel et les envois commencent après réception du paiement. Les mois affichés ne sont pas modifiables.</p><p>Ce calendrier ne vous convient pas ? Rapprochez-vous de l’éditeur pour en discuter.</p><a class="button light" href="/contact/?sujet=Calendrier%20de%20mon%20abonnement">Contacter l’éditeur</a><p>France métropolitaine : 4,50 € par envoi. Autres destinations sur devis.</p><div id="subscription-summary" class="subscription-summary" role="status" aria-live="polite"></div><p id="reservation-summary"></p><h2>Ce qui est inclus</h2><p>'+esc(INCLUDED)+'</p><h2>Délais et garanties</h2><p>Les mois d’expédition sont confirmés sur la facture. En cas de retard de plus d’un mois, vous pouvez maintenir, remplacer ou annuler le titre selon les CGV.</p><ul>'+''.join('<li>'+esc(x)+'</li>' for x in GUARANTEES)+'</ul>'
    body+='''<fieldset><legend>Vos coordonnées</legend><div class="contact-form"><label>Votre nom<input name="nom" required maxlength="120" autocomplete="name"></label><label>Votre e-mail<input name="email" type="email" required maxlength="254" autocomplete="email"></label><label>Téléphone (facultatif)<input name="phone" type="tel" maxlength="40"></label><label>Adresse de facturation<input name="billing_address" maxlength="500" autocomplete="billing street-address" required></label></div></fieldset><fieldset id="recipient-fields"><legend>Le destinataire</legend><div class="contact-form"><label>Prénom et nom<input name="recipient_name" required maxlength="120" autocomplete="shipping name"></label><label>Adresse<input name="address" required maxlength="200" autocomplete="shipping address-line1"></label><label>Complément<input name="address_extra" maxlength="200"></label><label>Code postal<input name="postal_code" required maxlength="5" pattern="[0-9]{5}" autocomplete="shipping postal-code"></label><label>Ville<input name="city" required maxlength="120" autocomplete="shipping address-level2"></label><label>Pays<input name="country" value="France" readonly></label></div><label>Mot pour la carte<textarea name="card_message" maxlength="1000" rows="4"></textarea></label></fieldset><div class="contact-trap" aria-hidden="true"><input name="website" tabindex="-1" autocomplete="off" aria-label="Ne pas remplir"></div><label class="contact-consent"><input name="terms" type="checkbox" required> J’ai lu et j’accepte les <a href="/cgv/" target="_blank" rel="noopener noreferrer">CGV</a>.</label><label class="contact-consent"><input name="acknowledge" type="checkbox" required> Je comprends que cette demande n’entraîne aucun paiement et qu’une facture me sera adressée après vérification.</label><p>Vos données servent à traiter votre demande. <a href="/confidentialite/" target="_blank" rel="noopener noreferrer">Politique de confidentialité</a>.</p><p id="subscription-availability" role="status"></p><button id="subscription-submit" class="button primary" type="submit" disabled>Envoyer ma demande</button><p id="subscription-result" role="status" aria-live="polite" tabindex="-1"></p><a id="subscription-contact" href="/contact/?sujet=abonnement-personnalise" class="button light" hidden>Passer par le formulaire de contact</a><button id="subscription-download" class="button light" type="button">Télécharger le récapitulatif</button><noscript><p>Contactez <a href="mailto:contact@lesplusgrandsracontes.fr">contact@lesplusgrandsracontes.fr</a> pour composer votre abonnement.</p></noscript></form></section>'''
    return body
