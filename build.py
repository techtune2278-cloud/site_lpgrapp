"""Générateur statique LPGR — textes du brief du 20 octobre 2026."""
import html
import json
from pathlib import Path
from urllib.parse import urljoin
from editorial_pages import render_site
from image_assets import apply_book_images
from page_helpers import external_links
from subscription_content import prepare_catalog
from publication import Publication, site_url, public_copy

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
books = json.loads((ROOT / 'content.json').read_text(encoding='utf-8-sig'))['books']
settings = json.loads((ROOT / 'site-settings.json').read_text(encoding='utf-8-sig'))
paragraphs = json.loads((ROOT / 'textes-brief.json').read_text(encoding='utf-8'))['paragraphs']
SUMUP = settings['shop_url']
SITE_URL = site_url(settings)
VERSION = '1.6.0'
SERIES = 'Les plus grands racontés aux plus petits'


def esc(value):
    return html.escape(str(value), quote=True)


def text(number):
    return public_copy(paragraphs[str(number)])


def heading(kicker, title, intro=''):
    return '<div class="page-heading"><p class="eyebrow">'+esc(kicker)+'</p><h1>'+esc(title)+'</h1>'+('<p class="lead">'+esc(intro)+'</p>' if intro else '')+'</div>'


def link(label, url, kind='primary'):
    return f'<a class="button {kind}" href="{esc(url)}">{esc(label)} <span aria-hidden="true">↗</span></a>'


def book_title(book):
    if book['number'] in [10, 20, 30]:
        return book['title']
    feminine = book['number'] in [3, 5, 9, 26, 27]
    return book['title'] + (' racontée aux enfants' if feminine else ' raconté aux enfants')


def cover(book, hero=False):
    title = book_title(book)
    alt = f'Couverture du livre {title}, collection {SERIES}'
    if book.get('cover'):
        return f'<img class="real-cover {"cover-hero" if hero else ""}" src="{esc(book["cover"])}" alt="{esc(alt)}" width="720" height="720" loading="lazy">'
    return f'<div class="book-cover {"big" if hero else ""}" style="--book:{esc(book["color"])}" role="img" aria-label="{esc(alt)}"><span class="series">Les plus grands racontés<br>aux plus petits</span><div class="cover-art"><span class="orbit" aria-hidden="true">✳</span><span class="initial">{esc(book["title"].split()[-1][0])}</span></div><strong>{esc(book["title"])}</strong><span class="cover-bottom">N° {book["number"]:02}</span></div>'


def cards(items):
    result = []
    for book in items:
        price = str(book['price'])+' €' if book['available'] else 'À paraître'
        detail = f'<a class="book-card-link" href="/livres/{book["slug"]}/">{cover(book)}<h3>{esc(book_title(book))}</h3></a>' if book['has_page'] else cover(book)+'<h3>'+esc(book_title(book))+'</h3>'
        notify = '' if book['available'] else link('Me prévenir', '/offrir/?reserver='+str(book['number'])+'#choisir-livres','text')
        result.append(f'<article class="book-card" id="{book["slug"]}">'+detail+f'<div class="card-meta"><span>N° {book["number"]:02}</span><span>{price}</span></div>'+notify+'</article>')
    return ''.join(result)


def page(path, title, body, description='', active='', extra='', og_description='', structured=None):
    target = OUT / path.strip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    nav = ''.join(f'<a {"aria-current=page" if active==label else ""} href="{url}">{label}</a>' for label, url in [('La collection', '/livres/'), ('Abonnement cadeau', '/offrir/#abonnement'), ('Les auteurs', '/auteurs/'), ('Où nous trouver', '/ou-nous-trouver/'), ('Professionnels', '/professionnels/')])
    canonical_path = {'autrices':'auteurs', 'agenda':'ou-nous-trouver','faq':'livraison'}.get(path,path)
    canonical = SITE_URL + ('/' + canonical_path.strip('/') + '/' if canonical_path else '/')
    description = publication.description(path, description, title)
    seo_head, structured = publication.metadata(path, title, description, canonical, structured)
    robots = 'index,follow,max-image-preview:large' if publication.indexable(path) else 'noindex,follow'
    body = public_copy(body)
    if path in {'professionnels','presse'}:body=body.replace('class="nothomb-quote"', 'class="nothomb-quote quote-centered"')
    analytics = '<script defer src="/_vercel/insights/script.js"></script>' if settings.get('analytics_enabled') else ''
    schema = ''
    if structured:
        schema = '<script type="application/ld+json">'+json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c')+'</script>'
    markup = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="{robots}"><meta name="theme-color" content="#6d3d72"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(og_description or description)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:type" content="website"><link rel="stylesheet" href="/fonts.css?v={VERSION}"><link rel="stylesheet" href="/style.css?v={VERSION}">{seo_head}{schema}{extra}{analytics}</head><body class="editorial-version"><a class="skip" href="#main">Aller au contenu</a><div class="topline">Les plus grands racontés aux plus petits <span>Dès 5 ans</span></div><header><a class="brand" href="/" aria-label="Accueil"><span class="brand-mark" aria-hidden="true">✳</span><span>Les plus grands<br><em>racontés aux plus petits</em></span></a><button class="menu-toggle" aria-expanded="false" aria-controls="nav">Menu ☰</button><nav id="nav">{nav}<a class="nav-order" href="/livres/">Acheter ↗</a></nav></header><main id="main">{body}</main><footer><div class="footer-top"><a class="brand" href="/">Les plus grands<br><em>racontés aux plus petits</em></a><p>Sur le Chemin des Arts<br>Hervélina Vyskoc et Valérie Lemoine<br>TVA non applicable, article 293 B du CGI</p><div><a href="/offrir/">Offrir</a><a href="/bonus/">Bonus et activités</a><a href="/presse/">Ils parlent de nous</a><a href="/contact/">Contact</a><a href="mailto:contact@lesplusgrandsracontes.fr">contact@lesplusgrandsracontes.fr</a><a href="/livraison/">Livraison et questions</a><a href="https://www.lescompagnonsderoute.com/">Les Compagnons de Route ↗</a><a href="https://www.facebook.com/share/18nftz5tx8/">Facebook ↗</a><a href="https://www.instagram.com/lpgrapp/">Instagram ↗</a></div></div><div class="footer-bottom"><span>© 2026 Sur le Chemin des Arts · V{VERSION}</span><div><a href="/mentions-legales/">Mentions légales</a><a href="/cgv/">CGV</a><a href="/confidentialite/">Confidentialité et cookies</a></div></div></footer><script src="/app.js?v={VERSION}" defer></script><script src="/subscription-rules.js?v={VERSION}" defer></script><script src="/subscription.js?v={VERSION}" defer></script><script src="/newsletter.js?v={VERSION}" defer></script></body></html>'''
    target.write_text(publication.media.optimize_html(external_links(markup)), encoding='utf-8')


apply_book_images(books, ROOT)
prepare_catalog(books)
# Retirer uniquement les anciennes pages générées qui n’ont pas encore de contenu.
for book in books:
    if not book['has_page']:
        old=OUT/'livres'/book['slug']/'index.html'
        if old.is_file():old.unlink()
        if old.parent.is_dir() and not any(old.parent.iterdir()):old.parent.rmdir()
(OUT/'subscription-rules.js').write_text((ROOT/'lib/subscription-rules.js').read_text(encoding='utf-8'),encoding='utf-8')
publication = Publication(ROOT, settings, books, SITE_URL)
render_site(globals())
page('404', 'Page introuvable', heading('Erreur 404', 'Cette page est introuvable')+link('Retrouver les livres', '/livres/'))
(OUT / '404.html').write_text((OUT / '404/index.html').read_text(encoding='utf-8'), encoding='utf-8')
(OUT / 'content.json').write_text(json.dumps({'books': books}, ensure_ascii=False), encoding='utf-8')
publication.finalize()
print(f'{len(publication.pages)} pages générées — V{VERSION} — {SITE_URL}')
