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
    options=''
    for book in subscription_books(books):
        options += '<label class="subscription-book"><input type="checkbox" name="subscription-title" value="'+str(book['number'])+'" data-title="'+esc(book['title'])+'" data-available="'+str(book['available']).lower()+'"><span><strong>'+esc(book['title'])+'</strong><small>N° '+str(book['number'])+' · 15 € · '+('Disponible' if book['available'] else 'À paraître')+'</small></span></label>'
    return '''<section class="section copy-section subscription" id="abonnement"><h2>Composez votre abonnement</h2><p>Cochez les six titres que vous souhaitez recevoir. Les deux premiers livres, Arthur Rimbaud et Victor Hugo, à 9 €, ne font pas partie de cette formule. Les numéros Collector sont également exclus.</p><p>Les titres à paraître peuvent être sélectionnés. Leur calendrier de parution et d’envoi sera confirmé avant le paiement.</p><form id="subscription-builder"><fieldset><legend>Choisissez six livres à 15 €</legend><div class="subscription-book-list">'''+options+'''</div></fieldset><fieldset><legend>Choisissez le rythme des envois</legend><label class="shipping-choice"><input name="subscription-shipping" type="radio" value="1" checked> Un livre par envoi — 5 € de port et d’emballage par envoi : 120 € au total</label><label class="shipping-choice"><input name="subscription-shipping" type="radio" value="2"> Deux livres par envoi — 7 € de port par envoi : 111 € au total</label><label class="shipping-choice"><input name="subscription-shipping" type="radio" value="3"> Trois livres par envoi — 7 € de port par envoi : 104 € au total</label></fieldset><label class="shipping-choice"><input id="subscription-gift" type="checkbox"> C’est un abonnement cadeau</label><p>Paiement en une fois, sans prélèvement récurrent ; abonnement cadeau au même prix, avec une carte et dédicace d’un des auteurs.</p><p>Aucune remise sur les livres (prix unique du livre) : l’argument est la régularité et le port groupé.</p><div id="subscription-summary" class="subscription-summary" role="status" aria-live="polite"><strong>0 livre sélectionné sur 6</strong><p>Six livres : 90 € de livres + 30 € de port et d’emballage en six envois, soit 120 €. Variante : 90 € de livres + 14 € de port en deux envois de trois livres, soit 104 €.</p></div><button class="button primary" id="subscription-submit" type="submit" disabled>Demander cet abonnement →</button><p class="muted">Cette sélection prépare votre demande. Elle ne déclenche ni commande payée ni prélèvement. Nous confirmons les titres, les dates et les modalités avant le paiement. Tarifs d’envoi de cette formule pour la France.</p><noscript><p>Activez JavaScript pour sélectionner vos titres ou contactez-nous pour composer votre abonnement.</p></noscript></form></section>'''
