const test=require('node:test');
const assert=require('node:assert/strict');
const {calculate}=require('../dist/subscription');

test('six titres au prix public, six envois de cinq euros : 120 euros',()=>{
  assert.deepEqual(calculate(6,1),{count:6,books:90,shipments:6,shipping:30,total:120});
});
test('six titres, trois envois de deux livres à sept euros : 111 euros',()=>{
  assert.deepEqual(calculate(6,2),{count:6,books:90,shipments:3,shipping:21,total:111});
});
test('six titres, deux envois de trois livres à sept euros : 104 euros',()=>{
  assert.deepEqual(calculate(6,3),{count:6,books:90,shipments:2,shipping:14,total:104});
});
test('une sélection vide ne coûte rien et les regroupements non proposés sont rejetés',()=>{
  assert.equal(calculate(0,1).total,0);
  assert.throws(()=>calculate(7,1));
  assert.throws(()=>calculate(6,6));
  assert.throws(()=>calculate(-1,1));
});
