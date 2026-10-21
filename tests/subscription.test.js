const test=require('node:test'),assert=require('node:assert/strict');
const {quote,summary}=require('../lib/subscription-rules');
const catalog=Array.from({length:20},(_,i)=>({number:i+1,title:'Livre '+(i+1),price:i<2?9:15,status:'paru',subscription_payable:true,release_month:''}));
const six=[3,4,5,6,7,8];
test('Six livres : tous les rythmes, y compris un seul colis à 9 euros',()=>{
 for(const [n,port,total] of [[1,9,99],[2,14,104],[3,21,111],[6,27,117]]){const q=quote(catalog,six,[],n);assert.equal(q.shipping,port);assert.equal(q.total,total);assert.equal(q.parcels.length,n);}
});
test('Rimbaud et Hugo sont libres et font baisser le montant de 12 euros',()=>{
 assert.equal(quote(catalog,[1,2,3,4,5,6],[],6).total,105);assert.equal(quote(catalog,[1],[],1).total,13.5);assert.equal(quote(catalog,[1,2],[],2).total,27);
});
test('Grille 7 à 12 livres et devis au-delà de 12 par colis',()=>{
 assert.equal(quote(catalog,[1,2,3,4,5,6,7],[],1).shipping,11);
 assert.equal(quote(catalog,Array.from({length:12},(_,i)=>i+1),[],1).shipping,11);
 const q=quote(catalog,Array.from({length:13},(_,i)=>i+1),[],1);assert.equal(q.total,null);assert.equal(q.requiresQuote,true);
 assert.equal(quote(catalog,Array.from({length:13},(_,i)=>i+1),[],2).shipping,20);
});
test('Réservations exclues du total ; envoi groupé attend le dernier mois',()=>{
 const future=[{number:21,title:'Futur',price:15,status:'prochain',release_month:'2027-03',subscription_payable:true},{number:22,title:'Plus tard',price:15,status:'plus_tard',subscription_payable:false}];
 const q=quote([...catalog,...future],[1,21],[22],1);assert.equal(q.books,24);assert.equal(q.shipping,7);assert.equal(q.parcels[0].release,'2027-03');assert.match(summary(q),/Réservations sans paiement/);
 const reservation=quote(future,[],[22],0);assert.equal(reservation.total,0);assert.equal(reservation.parcels.length,0);
});
test('Sélections incohérentes, doublons et quantités d’envois invalides sont rejetés',()=>{
 for(const args of [[[],[],0],[[1,1],[],1],[[1],[1],1],[[1],[],0],[[1],[],2],[[99],[],1],[[],[1],0]])assert.throws(()=>quote(catalog,...args));
});
