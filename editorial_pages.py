"""Mise en page des textes du brief, sans réécriture éditoriale."""
import json
from urllib.parse import urljoin
from image_assets import portraits, press_images
from content_features import excerpts, editorial_lists
from page_helpers import subscription_builder
from site_features import book_order, buying_help, offer_order, contact_form, shipping_body, audio_body


def render_site(ctx):
    root, books, settings = ctx['ROOT'], ctx['books'], ctx['settings']
    t, esc, page, cards, cover = (ctx[k] for k in ['text', 'esc', 'page', 'cards', 'cover'])
    heading, link, book_title = (ctx[k] for k in ['heading', 'link', 'book_title'])
    shop, series, base = ctx['SUMUP'], ctx['SERIES'], ctx['SITE_URL']
    p = lambda number: '<p data-brief="'+str(number)+'">'+esc(t(number))+'</p>'
    para = lambda value: '<p>'+esc(value)+'</p>'
    h = lambda number: '<h2>'+esc(t(number).split('H2 : ', 1)[-1])+'</h2>'
    section = lambda number, body, cls='': '<section class="section copy-section '+cls+'" data-section="'+str(number)+'">'+h(number)+body+'</section>'
    quote = lambda: '<blockquote class="nothomb-quote" data-brief="59">'+esc(t(59).replace('écrivaine','écrivain'))+'</blockquote>'
    event_cards, news_cards = editorial_lists(ctx)
    available = [b for b in books if b['available']]
    future = [b for b in books if not b['available']]
    photo_alt = 'Hervélina Vyskoc et Valérie Lemoine, auteurs de la collection, au Festival du Livre de Paris'
    photo = '<div class="photo-placeholder" role="img" aria-label="'+photo_alt+'"><span aria-hidden="true">✳</span><p>Hervélina Vyskoc et Valérie Lemoine</p></div>'
    photo = portraits(root, esc) or photo
    presse = [
        {'key': 'pyrenees', 'name': 'La République des Pyrénées', 'date': '30 avril 2026', 'details': 'page 49, par Aurélie Dugast', 'url': 'https://www.larepubliquedespyrenees.fr/culture-et-loisirs/livres/montaut-hervelina-vyskoc-et-valerie-lemoine-racontent-les-grands-ecrivains-aux-enfants-28856816.php'},
        {'key': 'tregor', 'name': 'Le Trégor', 'date': '1er avril 2026', 'details': 'par Thierry Morisseau', 'url': 'https://actu.fr/bretagne/runan_22269/cotes-darmor-dans-leur-nouvelle-collection-ils-racontent-les-plus-grands-auteurs-francais-aux-plus-petits_64086485.html'},
        {'key': 'flaneur', 'name': 'Le Flâneur', 'date': '27 juin 2026', 'details': 'par Pascal Le Coz', 'url': 'https://www.flaneur-mag.com/2026/06/27/les-plus-grands-racontes-aux-plus-petits-les-grands-auteurs-a-decouvrir-en-livres-denfants/'},
    ]
    presse.append({'key':'ouest-france','name':'Ouest-France','date':'','details':'','url':'https://www.ouest-france.fr/bretagne/runan-22260/le-concept-de-valerie-lemoine-dans-les-cotes-darmor-la-litterature-a-hauteur-denfant-eddbc2d8-3ef5-11f1-b283-bbda7cee88c6'})
    def press_cards():
        result = []
        for article in presse:
            paths=press_images(root,article['key'])
            if paths:
                image='<a class="press-image-link" href="'+esc(paths[0])+'" target="_blank" rel="noopener"><img src="'+esc(paths[0])+'" alt="Coupure de '+esc(article['name'])+'" loading="lazy"><span>Agrandir la coupure ↗</span></a>'
                if len(paths)>1:
                    image+='<div class="press-pages">'+''.join('<a href="'+esc(url)+'" target="_blank" rel="noopener">Page '+str(i)+' ↗</a>' for i,url in enumerate(paths,1))+'</div>'
            else:
                image=''
            meta='<p>'+article['date']+('<br>' if article['date'] and article['details'] else '')+article['details']+'</p>' if article['date'] or article['details'] else ''
            result.append('<article class="press-article">'+image+'<h3>'+article['name']+'</h3>'+meta+'<a class="underlink" href="'+article['url']+'">Lire l’article ↗</a></article>')
        return '<div class="press-grid">'+''.join(result)+'</div>'

    # Accueil : les onze blocs sont conservés dans l’ordre du document.
    hero_visual = ''.join('<div class="hero-book hb'+str(i)+'">'+cover(books[n], True)+'</div>' for i, n in enumerate([1, 5, 8]))
    home = '<section class="hero brief-hero"><div class="hero-copy"><h1>'+esc(t(55).removeprefix('H1 : '))+'</h1>'+quote()+p(60)+'<div class="actions">'+link('Offrir un abonnement','/offrir/#abonnement')+link('Acheter à l’unité',shop,'light')+'</div></div><div class="hero-visual"><div class="sunburst"></div>'+hero_visual+'</div></section>'
    home += section(62, p(63)+p(64))
    home += section(65, '<ul class="brief-list">'+''.join('<li data-brief="'+str(n)+'">'+esc(t(n))+'</li>' for n in [66,67,68,69])+'</ul>')
    fabrication = t(71).split(' Lien : ',1)[0]
    home += section(70, '<figure class="craft-photo"><img src="/assets/photos/collection-couture-bibliotheque.jpeg" alt="Tranches colorées et couture rose des livres de la collection, entre deux livres anciens" width="546" height="1425" loading="lazy"></figure>'+para(fabrication)+link('Pourquoi ces livres valent leur prix','/fabrique-en-france/','text'))
    home += section(72, '<ul class="brief-list">'+''.join('<li data-brief="'+str(n)+'">'+esc(t(n))+'</li>' for n in [73,74,75])+'</ul>'+p(76))
    home += section(77, '<div class="book-grid">'+cards(available)+'</div>'+para('À paraître : '+', '.join(b['title'] for b in books if 12<=b['number']<=17)+'. Le Collector n° 10, un livre de 32 pages avec jeux et exercices, paraît avant Noël.'))
    audiences = [(92,'Parents','/livres/'),(93,'Grands-parents','/offrir/'),(94,'Écoles et bibliothèques','/professionnels/#bibliotheques'),(95,'Libraires, musées, salons, Alliances françaises','/professionnels/')]
    audience_cards = ''
    for num, label, url in audiences:
        value=t(num).split(' : « ',1)[-1].split(' »',1)[0]
        audience_cards += '<a class="audience-card" href="'+url+'"><h3>'+label+'</h3><p>'+esc(value)+'</p></a>'
    home += section(90, '<div class="audience-grid">'+audience_cards+'</div>')
    home += section(96, '<div class="authors-intro">'+photo+'<div>'+para(t(97).split(' Lien : ',1)[0])+link('Rencontrer les auteurs','/auteurs/','text')+'</div></div>')
    home += section(99, p(100)+press_cards())
    home += section(102, p(103)+link('Commander',shop)+buying_help())
    home += '<section class="section copy-section newsletter-section"><h2>Lettre d’information</h2><p data-brief="105">Soyez prévenu à chaque nouvelle parution.</p>'+'<form id="newsletter-form" action="/api/newsletter" method="post"><div class="newsletter-fields"><label>Votre e-mail<input type="email" name="email" maxlength="254" autocomplete="email" required></label><label class="contact-consent"><input type="checkbox" name="consent" required> J’accepte de recevoir les nouvelles de la collection. Désabonnement à tout moment. <a href="/confidentialite/">Confidentialité</a>.</label><div class="contact-trap" aria-hidden="true"><label>Ne pas remplir<input name="website" tabindex="-1" autocomplete="off"></label></div></div><button class="button light" type="submit" disabled>S’inscrire</button><p role="status" aria-live="polite">Vérification de la disponibilité…</p><noscript><p>Contactez les auteurs pour les prochaines parutions.</p></noscript></form>'+link('Nous contacter','/contact/?sujet=Nouvelle%20parution','light')+' </section>'
    organization={'@context':'https://schema.org','@type':'Organization','name':'Sur le Chemin des Arts','url':base,'founder':[{'@type':'Person','name':n} for n in ['Hervélina Vyskoc','Valérie Lemoine']]}
    page('', t(53).split(' : ',1)[1], home, description=t(54).split(' : ',1)[1], og_description="On n'est jamais trop petit pour découvrir les plus grands.", structured=organization)

    # Collection et prévisions de parution, avec les trois numéros Collector.
    catalog = heading('La collection', 'Les plus grands racontés aux plus petits', t(63))
    catalog += '<section class="section catalog-section"><div class="filter-bar" role="group" aria-label="Filtrer les livres"><button class="filter active" data-filter="available" aria-pressed="true">Disponibles · '+str(len(available))+'</button><button class="filter" data-filter="future" aria-pressed="false">À paraître · '+str(len(future))+'</button><button class="filter" data-filter="all" aria-pressed="false">Toute la collection · '+str(len(books))+'</button><label class="search-label">Chercher un auteur<input id="book-search" type="search" placeholder="Hugo, Colette…"></label></div><div class="book-grid catalog">'
    catalog += ''.join('<div data-book data-status="'+('available' if b['available'] else 'future')+'" data-title="'+esc(b['title'])+'" '+('hidden' if not b['available'] else '')+'>'+cards([b])+'</div>' for b in books)
    catalog += '</div><p id="empty-results" hidden>Aucun auteur ne correspond à votre recherche.</p></section>'
    catalog += '<section class="section copy-section"><h2>Les numéros Collector</h2>'+p(44)+para('Le Collector n° 10, un livre de 32 pages avec jeux et exercices, paraît avant Noël.')+'<p>Prix du Collector : à confirmer.</p><h2>Aux racines du théâtre</h2><p>Sophocle · Aristophane</p></section>'
    page('livres','La collection de livres jeunesse dès 5 ans',catalog,active='La collection',structured={'@context':'https://schema.org','@type':'BookSeries','name':series,'inLanguage':'fr'})

    # Les auteurs : introduction et biographies intégrales à la première personne.
    intro=t(144).removeprefix('Introduction. ').split(' Photo des deux auteurs',1)[0]
    author_body=heading('Les auteurs',t(141).removeprefix('H1 : '),intro)
    author_body+='<section class="section">'+photo+'</section>'
    author_body+=section(145,p(146)).replace('<section ', '<section id="hervelina-vyskoc" ',1)+section(147,p(148)).replace('<section ', '<section id="valerie-lemoine" ',1)
    author_body+=section(149,para(t(150).split(' Lien vers ',1)[0])+link('Contact','/contact/','text')+' '+link('Professionnels','/professionnels/','text'))
    people={'@context':'https://schema.org','@graph':[{'@type':'Person','@id':base+'/auteurs/#hervelina-vyskoc','name':'Hervélina Vyskoc','jobTitle':['Comédienne','Écrivain','Professeur de théâtre'],'worksFor':{'@type':'Organization','name':'Sur le Chemin des Arts'}},{'@type':'Person','@id':base+'/auteurs/#valerie-lemoine','name':'Valérie Lemoine','jobTitle':'Enseignante','worksFor':{'@type':'Organization','name':'Sur le Chemin des Arts'}}]}
    page('auteurs',t(139).split(' : ',1)[1],author_body,description=t(140).split(' : ',1)[1],active='Les auteurs',structured=people)
    page('autrices','Les auteurs',heading('Les auteurs','Cette page a changé d’adresse.')+link('Rencontrer les auteurs','/auteurs/'),extra='<meta http-equiv="refresh" content="0;url=/auteurs/">')

    # Fiches : gabarit Victor Hugo du brief, adapté aux valeurs de chaque livre.
    deposit={1:'décembre 2025',2:'décembre 2025',3:'février 2026',4:'février 2026',5:'avril 2026',6:'avril 2026',7:'juin 2026',8:'juillet 2026',9:'juillet 2026',10:'octobre 2026',11:'août 2026'}
    for index,b in enumerate(books):
        bt=book_title(b); available_now=b['available']; collector=b['number'] in [10,20,30]
        meta=f'Découvrez {b["title"]} avec les enfants dès 5 ans : sa vie, un extrait de son œuvre, des jeux. Livre carré 18×18, tome {b["number"]} de la collection. {b["pages"]} pages, {b["price"]} €.' if available_now else 'Les plus grands racontés aux plus petits · '+bt+' · À paraître.'
        if b['number']==2:meta=t(156).split(' : ',1)[1]
        price=str(b['price'])+' €' if available_now else ('Prix à confirmer' if collector else 'À paraître')
        product='<section class="section product"><div><a class="backlink" href="/livres/">← La collection</a><div class="product-visual">'+cover(b,True)+'</div></div><div class="product-copy"><h1>'+esc(bt)+'</h1><p>Livre n° '+str(b['number'])+' de la collection '+series+' · dès 5 ans</p><div class="product-price">'+price+'</div>'
        product+=book_order(b,shop) if available_now else '<p>À paraître.</p>'+link('Être informé de la parution','/contact/?sujet=Parution%20'+b['slug'],'text')
        product+='<p>Disponible chez votre libraire</p>'+ (buying_help() if available_now else '')+'<h2>Fiche pratique</h2><dl class="specs">'
        specs=[('Collection',series),('Auteurs','Hervélina Vyskoc et Valérie Lemoine'),('Édition','Sur le chemin des arts'),('Numéro',b['number']),('Âge', 'Dès 5 ans'),('Format','18 × 18 cm'),('Pages',b['pages']),('Fabrication','Couture solide'),('Prix',price),('ISBN',b.get('isbn') or 'À renseigner'),('Dépôt légal BnF',deposit.get(b['number'],'À préciser'))]
        product+=''.join('<div><dt>'+label+'</dt><dd>'+esc(value)+'</dd></div>' for label,value in specs if value not in ('À renseigner','À préciser'))+'</dl><p class="muted">TVA non applicable, article 293 B du CGI</p><p>Hervélina Vyskoc et Valérie Lemoine<br>Illustrateur : John<br>Sur le Chemin des Arts</p></div></section>'
        detail=b.get('description') or ('Livre de 32 pages avec jeux et exercices.' if collector else '')
        if detail:product+='<section class="section copy-section"><h2>Dans ce livre</h2>'+para(detail)+'</section>'
        product+=excerpts(root,b)
        if b['number']==2: product+='<section class="section copy-section"><h2>Pour aller plus loin</h2><p>La Maison de Victor Hugo à Paris et Hauteville House à Guernesey [à vérifier et compléter].</p></section>'
        if b['number']==11:product+='<section class="section copy-section"><h2>Bonus</h2>'+link('Écouter le bonus de Molière','/bonus/moliere/')+'</section>'
        product+='<section class="section copy-section"><h2>Pourquoi 15 € ?</h2>'+''.join(p(n) for n in [471,472,473,474,475,476])+link('Fabriqué en France, avec soin','/fabrique-en-france/','text')+'</section>' if b['pages']==24 else '<section class="section copy-section"><h2>Fabriqué en France, avec soin</h2>'+p(471)+p(473)+link('Pourquoi ces livres valent leur prix','/fabrique-en-france/','text')+'</section>'
        product+='<section class="section"><h2>Les autres livres de la collection</h2><div class="book-grid">'+cards([books[i] for i in [index-1,index+1] if 0<=i<len(books)])+'</div>'+link('Pour les professionnels','/professionnels/','text')+'</section>'
        schema={'@context':'https://schema.org','@type':['Product','Book'],'name':bt,'author':[{'@type':'Person','name':n} for n in ['Hervélina Vyskoc','Valérie Lemoine']],'illustrator':{'@type':'Person','name':'John'},'publisher':{'@type':'Organization','name':'Sur le Chemin des Arts'},'isPartOf':{'@type':'BookSeries','name':series},'numberOfPages':b['pages'],'inLanguage':'fr','typicalAgeRange':'5-'}
        if b.get('isbn'):schema['isbn']=b['isbn']
        if b.get('cover'):schema['image']=urljoin(base+'/',b['cover'])
        if available_now:schema['offers']={'@type':'Offer','price':f'{b["price"]:.2f}','priceCurrency':'EUR','availability':'https://schema.org/InStock','url':base+'/livres/'+b['slug']+'/'}
        page('livres/'+b['slug'],bt+' dès 5 ans | Livre jeunesse',product,description=meta,active='La collection',structured=schema)

    # Professionnels : une section et une ancre par public, sans condenser les conditions.
    prof=heading('Professionnels','Libraires, bibliothèques, musées, salons : travaillons ensemble',"Nous sommes une maison d'édition indépendante : vous parlez directement aux auteurs de la collection.")+quote()
    publics=[('libraires',250,252),('bibliotheques',253,255),('musees',256,258),('ecoles',259,261),('salons',262,264),('presse',265,267)]
    prof+='<nav class="public-nav" aria-label="Publics professionnels">'+''.join('<a href="#'+anchor+'">'+esc(t(label))+'</a>' for anchor,label,_ in publics)+'</nav>'
    for anchor,label,copy in publics:
        prof+='<section class="section copy-section" id="'+anchor+'"><h2>'+esc(t(label))+'</h2>'+(para('Dépôt-vente : règlement trimestriel par virement avec état des ventes, dépôt de 6 mois, reprise des invendus avec 10 jours de préavis. Commande aussi possible par Dilicom (référencé via CyberScribe) ou en direct. Conditions commerciales et franco de port sur devis.') if anchor=='libraires' else para('Vente ferme, sans dépôt. Pour votre boutique, choisissez le livre consacré à l’auteur qui vous intéresse. Conditions commerciales et visuels sur demande.') if anchor=='musees' else p(copy))
        if anchor=='bibliotheques':prof+='<div class="table-scroll"><table class="shipping-table"><thead><tr><th>Titre</th><th>ISBN</th><th>Prix</th></tr></thead><tbody>'+''.join('<tr><td><a href="/livres/'+b['slug']+'/">'+esc(b['title'])+'</a></td><td>'+esc(b['isbn'])+'</td><td>'+str(b['price'])+' €</td></tr>' for b in available)+'</tbody></table></div>'
        if anchor=='ecoles':prof+=link('Tarifs d’envoi Europe et international','/livraison/#tarifs','text')+'<p><a class="button primary" href="/assets/documents/dossier-alliances-francaises-lpgrapp.pdf" download>Télécharger le dossier pour les Alliances françaises (PDF)</a></p>'
        if anchor=='musees':prof+='<figure class="museum-photo"><img src="/assets/photos/musee-jules-verne-nantes.jpg" alt="Le livre consacré à Jules Verne présenté dans la boutique du musée de Nantes" width="1361" height="765" loading="lazy"><figcaption>Le livre Jules Verne dans la boutique du musée de Nantes.</figcaption></figure>'
        if anchor=='presse':prof+=link('Revue de presse','/presse/','text')
        prof+='</section>'
    prof+='<section class="section copy-section"><h2>À télécharger</h2><ul class="brief-list">'+''.join('<li>'+esc(t(n).replace(', remises.','.'))+'</li>' for n in [269,270,271])+'</ul><p><a class="button light" href="/assets/documents/dossier-alliances-francaises-lpgrapp.pdf" download>Télécharger le dossier pour les Alliances françaises (PDF)</a></p></section><section class="section form-section"><h2>Formulaire de contact</h2><p>Les commandes de plus de 12 livres se font sur devis.</p><p>Un projet de rencontre ? Parlez-nous-en</p>'+contact_form(professional=True)+'</section>'
    page('professionnels','Libraires et bibliothèques : la collection jeunesse',prof,active='Professionnels')

    # Offrir : prix et composition conservés, aucune promesse cadeau non confirmée.
    offer_defs=[('duo','Duo','2 livres au choix à 15 €','30 €','7 €','37 €'),('trio','Trio','3 livres au choix à 15 €','45 €','7 €','52 €'),('quatre-premiers','Les quatre premiers','Rimbaud, Hugo, Ségur, Proust','48 €','9 €','57 €'),('collection-parue','La collection parue','10 livres (n° 1 à 9 et n° 11)','138 €','11 €','149 €')]
    offers='<section class="section gift-hero"><div>'+heading('L’abonnement cadeau','Une idée cadeau pour un enfant ou un petit-enfant')+'<p>Six livres à choisir, une belle aventure à partager.</p>'+link('Découvrir les packs','/offrir/#abonnement')+'</div><img src="/assets/photos/enfant-lecture-fauteuil.png" alt="Une enfant découvre un livre de la collection, installée dans un fauteuil" width="806" height="1069" loading="eager"></section>'+'<section class="section copy-section"><h2>Offre de Noël : port groupé et dédicace</h2>'+quote()+'<div class="offer-grid">'
    for key,name,contents,price,port,total in offer_defs:
        offers+='<article class="offer"><h3>'+name+'</h3><p>'+contents+'</p><strong class="offer-price">'+total+'</strong><p>'+price+' de livres + '+port+' de port (France)</p>'+offer_order(key,settings,subject=name)+'</article>'
    offers+='</div><p>Pour un abonnement cadeau : une carte et dédicace d’un des auteurs.</p></section>'+buying_help()
    split=offers.index('<section class="section copy-section"><h2>Offre de Noël')
    offers=offers[:split]+subscription_builder(books,esc)+offers[split:]
    page('offrir','Offrir les livres Les plus grands racontés aux plus petits',offers,active='Abonnement cadeau')
    manufacture=heading('La fabrication','Fabriqué en France, avec soin')+'<figure class="section craft-photo"><img src="/assets/photos/collection-couture-bibliotheque.jpeg" alt="Les livres de la collection avec leurs tranches colorées et leur couture rose" width="546" height="1425" loading="lazy"></figure>'+'<section class="section copy-section"><h2>Pourquoi ces livres valent leur prix</h2>'+''.join(p(n) for n in [471,472,473,474,475,476])+'</section>'
    page('fabrique-en-france','Fabriqué en France, avec soin',manufacture)
    page('presse','Ils parlent de nous',heading('Presse','Ils parlent de nous')+quote()+'<section class="section copy-section">'+p(100)+press_cards()+'</section>')

    # Autres parcours déjà livrés, en cohérence avec les termes du brief.
    form=contact_form()
    page('contact','Contact',heading('Contact','Une question, une invitation à un salon, une commande pour une librairie ou une école ?')+'<section class="section form-section">'+form+'</section>')
    page('livraison','Livraison et questions sur votre commande',heading('Commander les livres','Livraison et questions pratiques')+shipping_body(settings))
    page('faq','Questions fréquentes',heading('Questions fréquentes','Commander les livres')+shipping_body(settings))
    bookstores='<section class="section copy-section" id="librairies"><h2>Chez votre libraire</h2><div class="bookstore-grid"><article class="bookstore"><h3>La Librairie Monocle</h3><address>16 place de la Liberté<br>22260 Pontrieux</address><p><a href="tel:+33296929562">02 96 92 95 62</a></p><a class="underlink" href="https://librairesenbretagne.com/presentation/librairie_monocle/">Découvrir la librairie ↗</a></article><article class="bookstore"><h3>Librairie Gwalarn</h3><address><a href="https://www.google.com/maps/search/?api=1&amp;query=15+Rue+des+Chapeliers+22300+Lannion">15 Rue des Chapeliers<br>22300 Lannion</a></address><p><a href="tel:+33296374053">02 96 37 40 53</a></p><a class="underlink" href="https://gwalarn.fr/">Découvrir la librairie ↗</a></article></div><p>Demandez-le à votre libraire : disponible via Dilicom.</p></section>'
    page('ou-nous-trouver','Où nous trouver',heading('Librairies et rencontres','Où nous trouver')+bookstores+'<section class="section"><h2>Salons et dédicaces</h2>'+event_cards+'<div class="empty-panel">'+link('Un projet de rencontre ? Parlez-nous-en','/contact/','text')+'</div></section>',active='Où nous trouver')
    page('agenda','Où nous trouver',heading('Où nous trouver','Cette page a changé d’adresse.')+link('Où nous trouver','/ou-nous-trouver/'),extra='<meta http-equiv="refresh" content="0;url=/ou-nous-trouver/">')
    page('actualites','Blog et actualités',heading('La collection','Blog et actualités')+'<section class="section copy-section">'+(news_cards or '<p>Retrouvez les prochaines parutions dans la collection et les rencontres dans « Où nous trouver ».</p>')+'</section>')
    page('bonus','Bonus et activités',heading('Bonus et activités','Les bonus de la collection')+'<section class="section"><article class="bonus-card"><span class="sound-icon" aria-hidden="true">♫</span><div><h2>Molière</h2><p>Lecture d’un texte sous forme d’interprétation théâtrale pour Molière</p>'+link('Accéder aux bonus',settings.get('bonus_page_url') or '/bonus/moliere/','text')+'</div></article></section>')
    page('bonus/moliere','Molière : le bonus audio',heading('Tome 11','Lecture d’un texte sous forme d’interprétation théâtrale pour Molière')+audio_body(settings,root))
    mentions=heading('Informations','Mentions légales')+'<section class="section copy-section"><h2>Éditeur du site</h2><p>Micro-entreprise « Sur le Chemin des Arts ».</p><p>Nom : Sur le Chemin des Arts<br>SIRET : 953 755 477 00015<br>Adresse : 22 Rue de Lassun, 64800 Montaut</p><p>TVA non applicable, article 293 B du CGI.</p><p>Directeur de la publication : Hervélina Vyskoc-Lemoine</p><h2>Hébergement</h2><p>Le site est hébergé par Vercel Inc., 440 N Barranca Avenue #4133, Covina, CA 91723, États-Unis. Le domaine peut être géré séparément chez OVH.</p></section>'
    page('mentions-legales','Mentions légales',mentions)
    cgv=heading('Informations','Conditions générales de vente')+'<section class="section copy-section"><p>Sur le Chemin des Arts — SIRET : 953 755 477 00015 — 22 Rue de Lassun, 64800 Montaut.</p><p>TVA non applicable, article 293 B du CGI.</p><h2>Abonnements</h2><p>Six titres au choix selon le pack : Pack Découverte, Arthur Rimbaud et Victor Hugo à 9 € avec quatre titres à 15 € (78 € de livres) ; Pack Passion, six titres à 15 € (90 € de livres). Les numéros Collector sont exclus. Paiement en une fois, sans prélèvement récurrent.</p><p>Pack Découverte : Éco 92 € (78 € + 14 € de port), Équilibre 99 € (78 € + 21 €), Plaisir 105 € (78 € + 27 €). Pack Passion : Éco 104 € (90 € + 14 €), Équilibre 111 € (90 € + 21 €), Plaisir 117 € (90 € + 27 €). En France, en Lettre suivie : 2 envois de 3 livres, 3 envois de 2 livres ou 6 envois individuels. Un envoi individuel coûte 4,50 € ; un envoi de deux ou trois livres coûte 7 €.</p><p>Chaque abonnement comprend une carte et une dédicace d’un des auteurs.</p><p>Les dates de parution prévues et le calendrier d’envoi des titres sélectionnés sont communiqués et confirmés avant le paiement. Les titres à paraître sont signalés dans la sélection.</p><p>Remboursement du solde si un titre n’est pas livré.</p><p>Droit de rétractation de 14 jours.</p><h2>Commandes et paiement</h2><p>Les achats sont réalisés sur la boutique SumUp de Sur le Chemin des Arts. Les prix, frais de livraison et conditions applicables sont présentés avant le paiement. Une demande de devis ou de formule transmise par le site ne constitue pas une commande payée.</p><p><a href="https://sur-le-chemin-des-arts.sumupstore.com/page/conditions-generales">Consulter les conditions de vente de la boutique SumUp</a>.</p><h2>Rétractation et contact</h2><p>Pour exercer votre droit de rétractation ou signaler une difficulté de livraison, contactez Sur le Chemin des Arts par le formulaire de contact ou à son adresse postale en indiquant votre numéro de commande. Pour les modalités de retour et les exceptions éventuelles, consultez les conditions de vente de la boutique avant votre achat.</p></section>'
    page('cgv','Conditions générales de vente',cgv)
    privacy=heading('Informations','Confidentialité et cookies')+'<section class="section copy-section"><p>Le formulaire utilise votre nom, votre e-mail et votre message pour répondre à votre demande. Lorsqu’il est activé, l’envoi est assuré par Brevo. Votre demande ne vous inscrit pas à une newsletter.</p><p>Votre sélection d’abonnement est temporairement conservée dans votre navigateur pour être transférée dans votre demande de contact. Aucun outil de mesure d’audience n’est activé.</p><h2>Responsable du traitement et droits</h2><p>Sur le Chemin des Arts, 22 Rue de Lassun, 64800 Montaut, est responsable du traitement des demandes. Vous pouvez demander l’accès, la rectification ou l’effacement de vos données et exercer vos droits auprès de cette adresse ou par le formulaire de contact. Vous pouvez également adresser une réclamation à la CNIL.</p><h2>Conservation</h2><p>Les demandes sont conservées pendant le traitement et jusqu’à trois ans après le dernier échange, sauf obligation légale imposant une autre durée. Les coordonnées de la lettre d’information sont conservées jusqu’au désabonnement ou jusqu’à trois ans après le dernier contact. Chaque lettre contient un lien de désabonnement.</p><h2>Destinataires</h2><p>Les auteurs traitent les demandes. Vercel assure l’hébergement ; Brevo assure l’envoi des messages et la confirmation d’inscription lorsque ces services sont activés. Les informations ne sont pas revendues.</p></section>'
    if settings.get('analytics_enabled'):privacy=privacy.replace('Aucun outil de mesure d’audience n’est activé.', 'Vercel Web Analytics mesure les visites de façon agrégée sans cookie de suivi. Le service ne suit pas les visiteurs d’un site à l’autre.')
    page('confidentialite','Confidentialité et cookies',privacy)
    page('newsletter-confirmee','Lettre d’information',heading('Lettre d’information','Votre demande de confirmation')+'<section class="section copy-section"><p>Si vous venez de cliquer sur le lien de confirmation reçu par e-mail, votre inscription est confirmée. Vous pourrez vous désabonner dans chaque lettre.</p>'+link('Découvrir les livres','/livres/')+'</section>')
    editor='''<section class="section form-section"><p class="notice">Prototype local : les modifications restent dans ce navigateur. Exportez le fichier pour les intégrer au site ; cet atelier ne publie pas directement les changements.</p><div class="editor-grid"><form id="editor"><label>Livre<select id="editor-book"></select></label><label>Description<textarea id="editor-description" rows="6"></textarea></label><label>Adresse de la couverture<input id="editor-cover" type="url" placeholder="https://…"></label><label>Ou sélectionner une image<input id="editor-file" type="file" accept="image/png,image/jpeg,image/webp"></label><button class="button primary" type="submit">Enregistrer dans ce navigateur</button><p id="editor-status" role="status"></p></form><div id="editor-preview"></div></div><div class="actions"><button id="export-content" class="button primary">Exporter les contenus JSON ↓</button><label class="button light">Importer un fichier JSON<input id="import-content" type="file" accept="application/json" hidden></label></div><p id="import-status" role="status"></p></section>'''
    page('atelier','Atelier de contenu',heading('Préparation des contenus','Atelier de contenu')+editor)
