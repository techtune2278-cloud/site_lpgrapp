const test = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { runInNewContext } = require('node:vm');
const source = readFileSync(require.resolve('../dist/audience.js'), 'utf8');
const site = 'https://www.lesplusgrandsracontes.fr';
const id = 'G-R0SJSXH16B';
function boot({origin = site, existing = null, writable = true} = {}) {
  let entry = existing;
  let reloads = 0;
  const elements = Object.fromEntries(['script','choice','settings','accept','refuse'].map(name => [
    'audience-' + name, {dataset:{gaId:id}, hidden:true, addEventListener(k,f){this[k]=f;}, setAttribute(){}, focus(){}}
  ]));
  const scripts = [], cookies = [];
  const window = {addEventListener(){}};
  const location = {origin, pathname:'/livres/', hostname:new URL(origin).hostname, reload(){reloads++;}};
  const document = {getElementById:name=>elements[name], head:{append:tag=>scripts.push(tag)}, createElement:()=>({}),
    referrer:site+'/?email=test', set cookie(value){cookies.push(value);}};
  const localStorage = {getItem:()=>entry,setItem(k,v){if (!writable) throw Error('stockage indisponible');entry=v;}};
  runInNewContext(source, {window,location,document,localStorage,URL});
  return {window,elements,scripts,cookies,entry:()=>entry,reloads:()=>reloads};
}
test('Sans choix ou avec refus, aucune balise Google ne se charge',()=>{
  const p=boot();
  assert.equal(p.elements['audience-choice'].hidden,false);
  assert.equal(p.scripts.length,0);
  p.elements['audience-refuse'].click();
  assert.equal(p.scripts.length,0);
  assert.equal(p.elements['audience-choice'].hidden,true);
  assert.equal(boot({existing:p.entry()}).scripts.length,0);
});
test('Acceptation, navigation, puis retrait sans envoi supplémentaire',()=>{
  const p=boot();
  p.elements['audience-accept'].click();
  assert.equal(p.scripts[0].src,'https://www.googletagmanager.com/gtag/js?id='+id);
  assert.equal(p.window.dataLayer[3][2].page_referrer,site+'/');
  assert.equal(p.window.dataLayer[3][2].allow_google_signals,false);
  const next=boot({existing:p.entry()});
  assert.equal(next.scripts.length,1);
  next.elements['audience-settings'].click();
  next.elements['audience-refuse'].click();
  assert.equal(next.window['ga-disable-'+id],true);
  assert.equal(next.reloads(),1);
  assert.ok(next.cookies.some(v=>v.startsWith('_ga_R0SJSXH16B=; Max-Age=0')));
  assert.equal(boot({existing:next.entry()}).scripts.length,0);
});
test('Choix expiré et autres domaines : aucune balise',()=>{
  assert.equal(boot({existing:JSON.stringify({value:'yes',until:1})}).scripts.length,0);
  assert.equal(boot({origin:'https://sitelpgrapp.vercel.app',existing:JSON.stringify({value:'yes',until:Date.now()+1e6})}).scripts.length,0);
});
