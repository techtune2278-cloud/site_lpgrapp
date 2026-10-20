const test=require('node:test');
const assert=require('node:assert/strict');
const {calculate,validSelection}=require('../dist/subscription');

test('Passion : tarifs du document, port à 4,50 euros par envoi individuel',()=>{
  assert.deepEqual(calculate(6,1),{count:6,books:90,shipments:6,shipping:27,total:117});
  assert.deepEqual(calculate(6,2),{count:6,books:90,shipments:3,shipping:21,total:111});
  assert.deepEqual(calculate(6,3),{count:6,books:90,shipments:2,shipping:14,total:104});
});
test('Découverte : 78 euros de livres, totaux 92, 99 et 105 euros',()=>{
  assert.equal(calculate(6,3,78).total,92);
  assert.equal(calculate(6,2,78).total,99);
  assert.equal(calculate(6,1,78).total,105);
});
test('Les deux compositions restent cohérentes avec les prix des livres cochés',()=>{
 const starter=[{number:1,price:9},{number:2,price:9}],standard=[3,4,5,6,7,8].map(number=>({number,price:15}));
 assert.equal(validSelection([...starter,...standard.slice(0,4)],'decouverte'),true);
 assert.equal(validSelection(standard,'passion'),true);
 assert.equal(validSelection(standard,'decouverte'),false);
 assert.equal(validSelection([...starter,...standard.slice(0,4)],'passion'),false);
 assert.equal(validSelection([...starter,...standard.slice(0,3)],'decouverte'),false);
 assert.equal(validSelection([...standard.slice(0,5),standard[0]],'passion'),false);
 assert.equal(validSelection([...standard.slice(0,5),{number:10,price:15}],'passion'),false);
 assert.equal(validSelection([...standard.slice(0,5),{number:10,price:18}],'passion'),false);
});
test('Une sélection vide ne coûte rien ; les paramètres invalides sont rejetés',()=>{
 assert.equal(calculate(0,1).total,0);
 for(const args of [[7,1],[6,6],[-1,1],[6,1,NaN],[6,1,-10],[0,1,10]])assert.throws(()=>calculate(...args));
});
