(function(root){
 'use strict';
 const currentMonth=(now=new Date())=>new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Paris',year:'numeric',month:'2-digit'}).format(now);
 const validMonth=value=>typeof value==='string'&&/^\d{4}-(0[1-9]|1[0-2])$/.test(value);
 const nextMonth=month=>{
  const [year,n]=month.split('-').map(Number);
  return n===12?String(year+1).padStart(4,'0')+'-01':month.slice(0,5)+String(n+1).padStart(2,'0');
 };
 const monthLabel=month=>new Intl.DateTimeFormat('fr-FR',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(month+'-01T12:00:00Z'));
 const scheduleKey=q=>JSON.stringify(q.schedule.map(s=>[s.book.number,s.month]));
 function quote(catalog,lines,reservedIds=[],config={},month=currentMonth()){
  const min=config.min_books||3,max=config.max_books||12;
  if(!validMonth(month))throw Error('Mois de départ invalide.');
  if(!Array.isArray(lines)||!Array.isArray(reservedIds)||lines.length>120||reservedIds.length>500||(!lines.length&&!reservedIds.length))throw Error('Choisissez vos livres ou une réservation.');
  const byId=new Map(catalog.map(b=>[b.number,b])),selection=[],seen=new Set();
  let count=0;
  for(const line of lines){
   const book=byId.get(line?.number),quantity=line?.quantity??1;
   if(!book||!book.subscription_payable||!Number.isFinite(book.price)||book.price<=0||(!book.available&&!validMonth(book.release_month)))throw Error('Vérifiez les titres et les quantités.');
   if(quantity!==1||seen.has(book.number))throw Error('Un seul exemplaire par titre est possible. Pour une demande particulière, contactez l’éditeur.');
   seen.add(book.number);
   count++;
   if(count>max)throw Error(`L’abonnement comprend de ${min} à ${max} titres différents.`);
   selection.push({book,earliest:!book.available&&book.release_month>month?book.release_month:month});
  }
  if(count&&count<min)throw Error(`L’abonnement comprend de ${min} à ${max} titres différents.`);
  if(new Set(reservedIds).size!==reservedIds.length)throw Error('Réservation en double.');
  const reserved=reservedIds.map(id=>{const b=byId.get(id);if(!b||b.subscription_payable)throw Error('Réservation invalide.');return b;});
  // Use available titles first, then earliest releases; never ship two copies in the same month.
  selection.sort((a,b)=>a.earliest.localeCompare(b.earliest)||Number(b.book.available)-Number(a.book.available)||a.book.number-b.book.number);
  const schedule=[];
  let cursor=month;
  for(const {book,earliest} of selection){
   if(cursor<earliest)cursor=earliest;
   schedule.push({month:cursor,book});cursor=nextMonth(cursor);
  }
  const paid=schedule.map(s=>s.book);
  const bookCents=paid.reduce((sum,b)=>sum+Math.round(b.price*100),0),shippingCents=450*count;
  return {paid,reserved,schedule,books:bookCents/100,shipping:shippingCents/100,total:(bookCents+shippingCents)/100};
 }
 function summary(q){
  const money=n=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR'}).format(n);const out=['Demande d’abonnement — sans paiement à ce stade',''];
  if(q.schedule.length){out.push('Calendrier prévisionnel : un livre par mois d’envoi');for(const {month,book} of q.schedule)out.push(`- ${monthLabel(month)} : n° ${book.number} — ${book.title} — ${money(book.price)}`);out.push('');}
  out.push(`Livres : ${money(q.books)}`,`Port : ${money(q.shipping)}`,`Total estimatif : ${money(q.total)}`);
  if(q.reserved.length){out.push('','Réservations sans paiement, exclues du calendrier et du total :');for(const b of q.reserved)out.push('- '+b.title);}
  out.push('','Carte personnalisée et dédicace d’Hervélina ou de Valérie.','Après vérification : facture valable 15 jours, paiement unique par virement. Aucun prélèvement ni reconduction. Le contrat est conclu à réception du paiement.');return out.join('\n');
 }
 const api={quote,summary,currentMonth,monthLabel,scheduleKey};if(typeof module==='object'&&module.exports)module.exports=api;root.LPGRSubscriptionRules=api;
})(typeof globalThis!=='undefined'?globalThis:this);
