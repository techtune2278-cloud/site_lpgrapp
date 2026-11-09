const test=require('node:test'),assert=require('node:assert/strict');
const {quote,summary,scheduleKey,currentMonth}=require('../lib/subscription-rules');
const catalog=Array.from({length:12},(_,i)=>({number:i+1,title:'Livre '+(i+1),price:i<2?9:15,available:true,subscription_payable:true}));
catalog.push({number:21,title:'Collector',price:16.5,available:false,release_month:'2027-03',subscription_payable:true},{number:30,title:'À réserver',subscription_payable:false});
test('Six livres, six mois et six frais d’envoi, y compris le passage à janvier',()=>{
 const q=quote(catalog,Array.from({length:6},(_,i)=>({number:i+3,quantity:1})),[],{},'2026-11');
 assert.deepEqual(q.schedule.map(x=>x.month),['2026-11','2026-12','2027-01','2027-02','2027-03','2027-04']);
 assert.equal(q.shipping,27);assert.equal(q.total,117);
});
test('Livres parus d’abord, pause jusqu’à la parution, aucun mois imposé par le client',()=>{
 const q=quote(catalog,[{number:21,month:'2026-01',parcel:1},{number:1},{number:2}],[],{},'2026-11');
 assert.equal(scheduleKey(q),'[[1,"2026-11"],[2,"2026-12"],[21,"2027-03"]]');
 assert.match(summary(q),/mars 2027/);assert.equal(q.total,48);
 const future=quote(catalog,[{number:21}],[],{min_books:1},'2026-11');
 assert.equal(future.schedule[0].month,'2027-03');assert.equal(future.schedule.length,1);
});
test('Bornes de quantité et réservation sans date hors total et calendrier',()=>{
 assert.throws(()=>quote(catalog,[{number:1,quantity:2}],[],{},'2026-11'),/Un seul exemplaire/);
 assert.throws(()=>quote(catalog,[{number:1},{number:1},{number:2}],[],{},'2026-11'),/Un seul exemplaire/);
 assert.throws(()=>quote(catalog,[{number:1,quantity:12},{number:2,quantity:1}],[],{},'2026-11'));
 const q=quote(catalog,[],[30],{},'2026-11');assert.equal(q.total,0);assert.equal(q.schedule.length,0);
 assert.match(summary(q),/Réservations sans paiement/);
 assert.equal(currentMonth(new Date('2026-11-30T23:30:00Z')),'2026-12');
});
