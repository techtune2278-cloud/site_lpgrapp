"""Corrige le numéro du Collector 2 dans le catalogue déjà présent."""
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'content.json'
catalog = json.loads(path.read_text(encoding='utf-8-sig'))
books = catalog['books']
matches = [book for book in books if book['slug'] == 'collector-n-2']
if len(matches) != 1:
    raise SystemExit('Collector n° 2 introuvable ou en double : catalogue laissé intact.')
book = matches[0]
if any(other is not book and other['number'] == 20 for other in books):
    raise SystemExit('Le numéro 20 est déjà attribué à une autre fiche : catalogue laissé intact.')
if book['number'] == 20:
    print('Collector n° 2 : numéro 20 déjà enregistré.')
elif book['number'] == 34:
    book['number'] = 20
    temp = path.with_suffix('.json.tmp')
    temp.write_bytes((json.dumps(catalog, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    temp.replace(path)
    print('Collector n° 2 : numéro 34 corrigé en 20.')
else:
    raise SystemExit('Numéro inattendu pour le Collector n° 2 : catalogue laissé intact.')
