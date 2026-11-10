import unittest,json,sys,shutil,tempfile,subprocess,re,os
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from publication import Publication
class V18Tests(unittest.TestCase):
 def test_forty_readable_pages_and_collector_status(self):
  books=json.loads((ROOT/'content.json').read_text())['books'];catalog=(ROOT/'dist/livres/index.html').read_text()
  collectors=[book for book in books if book['slug'].startswith('collector-')]
  self.assertTrue(collectors)
  for book in collectors:
   marker=re.escape('id="'+book['slug']+'"')
   status='available' if book['available'] else 'future'
   hidden='' if book['available'] else 'hidden'
   self.assertEqual(len(re.findall(marker,catalog)),1)
   self.assertRegex(catalog,r'<div data-book data-status="'+status+r'" data-title="[^"]+" '+hidden+r'><article class="book-card" '+marker)
  for book in books:
   if book['number'] in [1,2,3,4,5,6,7,8,9,11]:
    self.assertEqual(len(book['excerpts']),4)
    for src in book['excerpts']:self.assertTrue((ROOT/'dist'/src.lstrip('/')).is_file())
    html=(ROOT/'dist/livres'/book['slug']/'index.html').read_text();self.assertEqual(html.count(' data-flip-page '),4)
  for html in (ROOT/'dist').rglob('*.html'):
   self.assertNotRegex(html.read_text(),r'\bJohn\b|Dans ce livre|Disponible chez votre libraire')
 def test_home_stops_before_press_and_notify_opens_contact(self):
  home=(ROOT/'dist/index.html').read_text().split('<main id="main">')[1].split('</main>')[0]
  for phrase in ['Ils parlent de nous','Lettre d’information']:self.assertNotIn(phrase,home)
  catalog=(ROOT/'dist/livres/index.html').read_text();self.assertIn('/contact/?sujet=Parution%20-',catalog)
  self.assertNotIn('/offrir/?reserver=',catalog)
  for page in [home,catalog]:
   self.assertIn('En découvrant notre collection, l’écrivain Amélie Nothomb',page)
   self.assertIn('On n’est jamais trop petit pour découvrir les plus grands.',page)
 def test_press_and_contact_changes(self):
  press=(ROOT/'dist/presse/index.html').read_text()
  self.assertLess(press.index('tant aimés.'),press.index('l’écrivain Amélie Nothomb'))
  self.assertLess(press.index('l’écrivain Amélie Nothomb'),press.index('Agrandir la coupure'))
  self.assertEqual(press.count('« On n’est jamais trop petit pour découvrir les plus grands. »'),1)
  offer=(ROOT/'dist/offrir/index.html').read_text()
  self.assertNotIn('Droit de rétractation de 14 jours',offer)
  self.assertIn('href="/cgv/"',offer)
 def test_indexation_switch_and_confirmed_events(self):
  for path in (ROOT/'dist').rglob('index.html'):self.assertIn('content="noindex,nofollow"',path.read_text())
  with patch.dict(os.environ,{'INDEXATION_ENABLED':'true'}):
   p=object.__new__(Publication);p.settings={'publication_mode':'draft'};self.assertTrue(p.indexable('livres'));self.assertFalse(p.indexable('administration'))
  self.assertTrue(all(e['confirmed'] for e in json.loads((ROOT/'content.json').read_text())['events']))
 def test_real_build_removes_deleted_routes_and_uses_uploaded_images(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)/'site';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','.build-venv','__pycache__','node_modules','__qa'))
   original=json.loads((root/'content.json').read_text());deleted=[b['slug'] for b in original['books']];events=[e['slug'] for e in original['events']]
   source=(ROOT/'dist/assets/photos/hervelina-portrait.jpg').read_bytes()
   import base64
   photo='data:image/jpeg;base64,'+base64.b64encode(source).decode()
   original['books']=[dict(number=99,title='Livre ajouté',slug='livre-ajoute',available=True,price=15,pages=24,color='#704575',description='',cover=photo,excerpts=[photo],commande_url='',release_month='')]
   original['events']=[dict(slug='nouveau-salon',title='Salon ajouté',start_date='2027-06-10',city='Montaut',image=photo,confirmed=True)]
   original['stores']=[]
   original['bonuses']=[dict(slug='bonus-test',author='Hugo & invités',title='Un film',type='video',url='https://example.org/film')]
   (root/'content.json').write_text(json.dumps(original),encoding='utf-8')
   subprocess.run([sys.executable,'build.py'],cwd=root,check=True,capture_output=True)
   bonus_page=(root/'dist/bonus/index.html').read_text()
   self.assertIn('<strong>Hugo &amp; invités</strong>',bonus_page)
   self.assertIn('🎞',bonus_page)
   self.assertIn('https://example.org/film',bonus_page)
   self.assertNotIn('<strong>Molière</strong>',bonus_page)
   for slug in deleted:self.assertFalse((root/'dist/livres'/slug/'index.html').exists())
   for slug in events:self.assertFalse((root/'dist/rencontres'/slug/'index.html').exists())
   for route in ['livres/livre-ajoute','rencontres/nouveau-salon']:
    page=(root/'dist'/route/'index.html').read_text();self.assertIn('/assets/optimized/',page);self.assertNotIn('data:image/',page)
   public=json.loads((root/'dist/content.json').read_text());self.assertTrue(public['books'][0]['cover'].startswith('/assets/optimized/'))
   self.assertNotIn('La Librairie Monocle',(root/'dist/ou-nous-trouver/index.html').read_text())

   original['books'][0].update(cover='',cover_hidden=True,excerpts=[])
   (root/'content.json').write_text(json.dumps(original),encoding='utf-8')
   subprocess.run([sys.executable,'build.py'],cwd=root,check=True,capture_output=True)
   public=json.loads((root/'dist/content.json').read_text());self.assertEqual(public['books'][0]['cover'],'')
   self.assertNotIn('data-flip-page',(root/'dist/livres/livre-ajoute/index.html').read_text())
