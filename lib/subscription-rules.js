(function(root){
 'use strict';
 function quote(catalog,paidIds,reservedIds,shipments){
  if(!Array.isArray(paidIds)||!Array.isArray(reservedIds)||paidIds.length+reservedIds.length===0)throw Error('Choisissez au moins un livre ou une réservation.');
  const all=[...paidIds,...reservedIds];if(all.some(n=>!Number.isInteger(n))||new Set(all).size!==all.length)throw Error('Sélection de titres invalide.');
  const byId=new Map(catalog.map(book=>[book.number,book]));
  const paid=paidIds.map(id=>{const book=byId.get(id);if(!book||book.subscription_payable!==true||!Number.isFinite(book.price)||book.price<=0)throw Error('Un titre n’est plus disponible dans cette sélection. Rechargez la page.');return book;});
  const reserved=reservedIds.map(id=>{const book=byId.get(id);if(!book||book.subscription_payable===true)throw Error('Réservation invalide. Rechargez la page.');return book;});
  if(!Number.isInteger(shipments)||(paid.length===0?shipments!==0:shipments<1||shipments>paid.length))throw Error('Choisissez un nombre d’envois compris entre un et le nombre de livres.');
  paid.sort((a,b)=>(a.status==='paru'?0:1)-(b.status==='paru'?0:1)||(a.release_month||'').localeCompare(b.release_month||'')||a.number-b.number);
  const parcels=[];let cursor=0;
  for(let i=0;i<shipments;i++){
   const count=Math.floor(paid.length/shipments)+(i<paid.length%shipments?1:0);
   const books=paid.slice(cursor,cursor+count);cursor+=count;
   const shipping=count===1?4.5:count<=3?7:count<=6?9:count<=12?11:null;
   const release=books.filter(b=>b.status==='prochain').map(b=>b.release_month).sort().at(-1)||'';
   parcels.push({books,shipping,release});
  }
  const bookCents=paid.reduce((sum,b)=>sum+Math.round(b.price*100),0),requiresQuote=parcels.some(p=>p.shipping===null);
  const shipping=requiresQuote?null:parcels.reduce((sum,p)=>sum+Math.round(p.shipping*100),0)/100;
  return {paid,reserved,parcels,shipments,books:bookCents/100,shipping,total:shipping===null?null:bookCents/100+shipping,requiresQuote};
 }
 function summary(q){
  const money=value=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR'}).format(value);
  const lines=['Demande d’abonnement — sans paiement à ce stade',''];
  for(const [i,p] of q.parcels.entries()){
   lines.push(`Envoi ${i+1} — ${p.books.length} livre(s) — port : ${p.shipping===null?'sur devis':money(p.shipping)}`);
   for(const b of p.books)lines.push(`- N° ${b.number} : ${b.title} — ${money(b.price)} (${b.status==='paru'?'paru':'parution prévue : '+b.release_month})`);
   lines.push(p.release?`Envoi après la parution du dernier titre du colis (${p.release}), sous 10 jours.`:'Livres déjà parus ; calendrier d’envoi à confirmer.','');
  }
  lines.push(`Livres : ${money(q.books)}`,`Port : ${q.shipping===null?'sur devis':money(q.shipping)}`,`Total : ${q.total===null?'sur devis, aucun montant définitif':money(q.total)}`);
  if(q.reserved.length){lines.push('','Réservations sans paiement — exclues du total :');for(const b of q.reserved)lines.push(`- N° ${b.number} : ${b.title}${b.release_month?' — '+b.release_month:' — date à confirmer'}`);}
  lines.push('','Carte et dédicace d’Hervélina ou de Valérie.','Un seul paiement, sans prélèvement, après confirmation du montant et du calendrier.');
  return lines.join('\n');
 }
 const api={quote,summary};if(typeof module==='object'&&module.exports)module.exports=api;root.LPGRSubscriptionRules=api;
})(typeof globalThis!=='undefined'?globalThis:this);
