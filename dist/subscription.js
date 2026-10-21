(()=>{
 'use strict';
 const form=document.querySelector('#subscription-builder');if(!form)return;
 const R=globalThis.LPGRSubscriptionRules,result=document.querySelector('#subscription-summary'),parcels=document.querySelector('#subscription-parcels'),shipping=document.querySelector('#subscription-shipments');
 const submit=document.querySelector('#subscription-submit'),status=document.querySelector('#subscription-availability'),responseText=document.querySelector('#subscription-result'),recipient=document.querySelector('#recipient-fields');
 let catalog=[],ready=false,enabled=false,busy=false,startedAt=Date.now(),current=null;
 const ids=name=>Array.from(form.querySelectorAll(`[name="${name}"]:checked`),b=>Number(b.value));
 const money=value=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR'}).format(value);
 function update(){
  const paid=ids('subscription-title'),reserved=ids('reserve-title');const previous=Number(shipping.value)||1;shipping.replaceChildren();
  if(paid.length){for(let i=1;i<=paid.length;i++){const option=document.createElement('option');option.value=i;option.textContent=`${i} envoi${i>1?'s':''}`;shipping.append(option);}shipping.value=String(Math.min(previous,paid.length));}
  else{const option=document.createElement('option');option.value='0';option.textContent=reserved.length?'Réservations : aucun envoi à régler':'Choisissez vos livres';shipping.append(option);}
  shipping.disabled=paid.length===0;recipient.hidden=paid.length===0;recipient.disabled=paid.length===0;
  current=null;result.replaceChildren();parcels.replaceChildren();document.querySelector('#reservation-summary').textContent='';
  if(!ready||(!paid.length&&!reserved.length)){result.textContent='Choisissez vos livres pour afficher le détail : livres, port, total.';submit.disabled=true;return;}
  try{current=R.quote(catalog,paid,reserved,Number(shipping.value));}catch(error){result.textContent=error.message;submit.disabled=true;return;}
  const total=document.createElement('strong');total.textContent=current.requiresQuote?`${money(current.books)} de livres · port et total sur devis`:`Livres : ${money(current.books)} · Port : ${money(current.shipping)} · Total : ${money(current.total)}`;result.append(total);
  if(current.requiresQuote){const p=document.createElement('p');p.textContent='Un colis dépasse 12 livres : nous vous communiquerons le port avant tout paiement. Vous pouvez augmenter le nombre d’envois pour obtenir un tarif calculé.';result.append(p);}
  for(const [i,parcel] of current.parcels.entries()){
   const card=document.createElement('article');card.className='parcel-card';const h=document.createElement('h3');h.textContent=`Envoi ${i+1} — ${parcel.books.length} livre(s)`;const list=document.createElement('ul');
   for(const book of parcel.books){const item=document.createElement('li');item.textContent=`${book.title} — ${money(book.price)}${book.release_month?' · '+book.release_month:''}`;list.append(item);}
   const p=document.createElement('p');p.textContent=`Port : ${parcel.shipping===null?'sur devis':money(parcel.shipping)}. `+(parcel.release?`Ce colis attend la parution prévue en ${parcel.release} ; envoi sous 10 jours après cette parution.`:'Livres déjà parus ; calendrier à confirmer.');card.append(h,list,p);parcels.append(card);
  }
  document.querySelector('#reservation-summary').textContent=current.reserved.length?`Réservations sans paiement, exclues du total : ${current.reserved.map(b=>b.title).join(', ')}.`:'';
  submit.disabled=!enabled||busy;submit.textContent=current.paid.length?'Envoyer ma demande':'Demander ces réservations sans paiement';
 }
 function request(){
  if(!current)throw Error('Choisissez au moins un livre ou une réservation.');if(!form.reportValidity())return null;
  const values=Object.fromEntries(new FormData(form));return {...values,paidIds:ids('subscription-title'),reservedIds:ids('reserve-title'),shipments:Number(shipping.value),expectedTotal:current.total,consent:values.consent==='on',startedAt};
 }
 function message(data){return R.summary(current)+`\n\nAcheteur : ${data.nom}\nE-mail : ${data.email}\nTéléphone : ${data.phone||'Non renseigné'}\n\nDestinataire : ${data.recipient_name||'À confirmer'}\n${data.address||''}\n${data.address_extra||''}\n${data.postal_code||''} ${data.city||''}\nFrance\n\nMot pour la carte :\n${data.card_message||'Aucun'}\n\nAccord d’utilisation des données donné pour traiter cette demande.`;}
 form.addEventListener('change',event=>{if(['subscription-title','reserve-title'].includes(event.target.name)||event.target===shipping)update();});
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(!enabled||busy||!ready)return;let data;try{data=request();}catch(error){responseText.textContent=error.message;return;}if(!data)return;
  busy=true;submit.disabled=true;form.setAttribute('aria-busy','true');responseText.textContent='Envoi de votre demande…';
  try{const response=await fetch('/api/subscription',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(data),signal:AbortSignal.timeout(15000)});const answer=await response.json();if(!response.ok||answer.ok!==true)throw Error(answer.error||'L’envoi n’a pas pu être confirmé.');responseText.textContent='Votre demande a été transmise au service d’envoi. Nous vous confirmerons le montant et le calendrier par e-mail, avec le lien de paiement pour les livres retenus. Vos réservations restent sans paiement.';startedAt=Date.now();}
  catch(error){responseText.textContent=error.name==='TimeoutError'?'L’envoi n’a pas pu être confirmé à temps. Votre saisie est conservée.':error.message;}
  finally{busy=false;form.removeAttribute('aria-busy');update();responseText.focus();}
 });
 document.querySelector('#subscription-email').addEventListener('click',()=>{try{const data=request();if(data)location.href='mailto:contact@lesplusgrandsracontes.fr?subject='+encodeURIComponent('Demande d’abonnement / réservation')+'&body='+encodeURIComponent(message(data));}catch(error){responseText.textContent=error.message;}});
 document.querySelector('#subscription-download').addEventListener('click',()=>{try{const data=request();if(!data)return;const url=URL.createObjectURL(new Blob([message(data)],{type:'text/plain;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='demande-abonnement.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){responseText.textContent=error.message;}});
 Promise.all([fetch('/content.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}),fetch('/api/subscription',{headers:{Accept:'application/json'},cache:'no-store',signal:AbortSignal.timeout(10000)}).then(r=>r.ok?r.json():{enabled:false}).catch(()=>({enabled:false}))]).then(([data,service])=>{catalog=data.books;ready=true;enabled=service.enabled===true;const requested=Number(new URLSearchParams(location.search).get('reserver'));if(Number.isInteger(requested)&&requested>0){const box=Array.from(form.querySelectorAll('input[type=checkbox][value]')).find(input=>Number(input.value)===requested);if(box)box.checked=true;}status.textContent=enabled?'Votre demande sera envoyée à contact@lesplusgrandsracontes.fr.':'L’envoi direct est indisponible. Utilisez « Préparer un e-mail » pour écrire à contact@lesplusgrandsracontes.fr ou téléchargez votre récapitulatif.';update();}).catch(()=>{status.textContent='Le catalogue n’a pas pu être chargé. Rechargez la page ou contactez contact@lesplusgrandsracontes.fr.';});
})();
