"""Liens sortants et sélection d’abonnement."""
import re


def external_links(markup):
    def update(match):
        attrs = match.group(1)
        href = re.search(r'\bhref="([^"]+)"', attrs)
        if not href:
            return match.group(0)
        value = href.group(1)
        if not (value.startswith(('https://', 'http://')) or value.split('?')[0].lower().endswith('.pdf')):
            return match.group(0)
        attrs = re.sub(r'\s+(target|rel)="[^"]*"', '', attrs)
        return '<a' + attrs + ' target="_blank" rel="noopener noreferrer">'
    return re.sub(r'<a\b([^>]*)>', update, markup)


def subscription_books(books):
    # Six livres de 24 pages à 15 €. Les Collectors n’ont pas un prix confirmé.
    return [b for b in books if b['number'] not in [1,2,10,20,30] and b['pages']==24 and b['price']==15]


def subscription_builder(books, esc):
    eligible=subscription_books(books)
    cheap=[b for b in books if b['number'] in [1,2]]
    options=''
    for book in cheap+eligible:
        options += '<label class="subscription-book"'+(' data-starter="true"' if book['number'] in [1,2] else '')+'><input type="checkbox" name="subscription-title" value="'+str(book['number'])+'" data-price="'+str(book['price'])+'" data-title="'+esc(book['title'])+'" data-available="'+str(book['available']).lower()+'"><span><strong>'+esc(book['title'])+'</strong><small>N° '+str(book['number'])+' · '+str(book['price'])+' € · '+('Disponible' if book['available'] else 'À paraître')+'</small></span></label>'
    packs=''
    for key,name,subtitle,amount in [('decouverte','Découverte','Je commence : Rimbaud et Hugo + quatre titres à 15 € au choix',sum(b['price'] for b in cheap)+60),('passion','Passion','Je poursuis : six titres à 15 € au choix',90)]:
        packs+='<label class="subscription-pack"><input type="radio" name="subscription-pack" value="'+key+'" '+('checked' if key=='decouverte' else '')+'><span><strong>Pack « '+name+' »</strong><span>'+subtitle+'</span><span>'+str(amount)+' € de livres</span><span>Éco : '+str(amount+14)+' € · 2 envois de 3 livres (14 € de port)</span><span>Équilibre : '+str(amount+21)+' € · 3 envois de 2 livres (21 € de port)</span><span>Plaisir : '+str(amount+27)+' € · 6 envois individuels (27 € de port)</span></span></label>'
    return '''<section class="section copy-section subscription" id="abonnement"><h2>L’abonnement à la collection : « L’aventure des grands auteurs, au fil du temps »</h2><p>Six livres à choisir, une belle aventure à partager.</p><p>Faites découvrir aux enfants les grands noms de la littérature française, à travers de vrais textes, des illustrations, des découvertes culturelles et des activités ludiques.</p><p>Choisissez librement six titres parmi les livres de la collection, puis recevez-les au fil du temps, au rythme des parutions.</p><p>Chaque abonnement comprend une carte et une dédicace d’un des auteurs de la collection.</p><figure class="subscription-fan"><img src="/assets/photos/collection-livres-eventail.jpeg" alt="Les dix livres parus de la collection disposés en éventail" width="1824" height="1373" loading="lazy"></figure><h3>Composez votre abonnement</h3><form id="subscription-builder"><fieldset><legend>Choisissez votre pack</legend><div class="subscription-packs">'''+packs+'''</div></fieldset><fieldset><legend>Choisissez vos titres</legend><p id="subscription-selection-help">Pack Découverte : Rimbaud et Hugo sont inclus ; choisissez quatre autres titres à 15 €.</p><p>Les numéros Collector sont exclus. Le calendrier des titres à paraître est confirmé avant le paiement.</p><div class="subscription-book-list">'''+options+'''</div></fieldset><fieldset><legend>Choisissez le rythme des envois — France, en Lettre suivie</legend><label class="shipping-choice"><input name="subscription-shipping" type="radio" value="3"> Formule Éco — 2 envois de 3 livres : 14 € de port</label><label class="shipping-choice"><input name="subscription-shipping" type="radio" value="2" checked> Formule Équilibre — 3 envois de 2 livres : 21 € de port</label><label class="shipping-choice"><input name="subscription-shipping" type="radio" value="1"> Formule Plaisir — 6 envois individuels : 27 € de port (6 × 4,50 €)</label></fieldset><label class="shipping-choice"><input id="subscription-gift" type="checkbox"> C’est un abonnement cadeau</label><p>Paiement en une fois, sans prélèvement récurrent. Les envois sont effectués en Lettre suivie.</p><div id="subscription-summary" class="subscription-summary" role="status" aria-live="polite"><strong>Choisissez votre pack et vos six livres.</strong></div><button class="button primary" id="subscription-submit" type="submit" disabled>Demander cet abonnement →</button><p class="muted">Cette sélection prépare votre demande. Elle ne déclenche ni commande payée ni prélèvement. Nous confirmons les titres, les dates et les modalités avant le paiement. Tarifs d’envoi pour la France.</p><noscript><p>Contactez-nous pour composer votre abonnement.</p></noscript></form></section>'''
