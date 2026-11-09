(()=>{
 const form=document.querySelector('#subscription-builder');if(!form)return;const R=globalThis.LPGRSubscriptionRules;
 const summary=document.querySelector('#subscription-summary'),schedule=document.querySelector('#subscription-schedule'),status=document.querySelector('#subscription-availability'),result=document.querySelector('#subscription-result'),submit=document.querySelector('#subscription-submit');
 let catalog=[],config={},ready=false,enabled=false,busy=false,current=null,startedAt=Date.now();
 const money=n=>new Intl.NumberFormat('fr-FR',{style:'currency',currency:'EUR'}).format(n);
 const reservations=()=>[...form.querySelectorAll('[name="reserve-title"]:checked')].map(x=>Number(x.value));
 const contact=document.querySelector('#subscription-contact');
 form.noValidate=true;
 function notice(text,focus=true){result.textContent=text;if(focus)result.focus();}
 function lines(){return [...form.querySelectorAll('[name="subscription-title"]:checked')].map(box=>({number:Number(box.value)}));}
 function update(){
  current=null;summary.textContent='';schedule.replaceChildren();document.querySelector('#reservation-summary').textContent='';submit.disabled=busy||!ready;if(!ready)return;
  const selected=lines(),reserved=reservations();const billing=form.elements.billing_address;billing.required=selected.length>0;billing.disabled=!selected.length;billing.closest('label').hidden=!selected.length;document.querySelector('#recipient-fields').hidden=!selected.length;document.querySelector('#recipient-fields').disabled=!selected.length;
  if(!selected.length&&!reserved.length){summary.textContent='Choisissez vos livres pour afficher les envois prévus.';return;}
  try{current=R.quote(catalog,selected,reserved,config);}catch(error){summary.textContent=error.message;return;}
  summary.textContent=`${current.paid.length} titre(s) · Livres : ${money(current.books)} · Port : ${money(current.shipping)} · Total estimatif : ${money(current.total)}`;
  for(const {month,book} of current.schedule){const row=document.createElement('li'),date=document.createElement('time');date.dateTime=month;date.textContent=R.monthLabel(month);row.append(date,document.createTextNode(' — '+book.title));schedule.append(row);}
  document.querySelector('#reservation-summary').textContent=current.reserved.length?'Réservations sans paiement, hors calendrier : '+current.reserved.map(x=>x.title).join(', '):'';submit.disabled=busy;
 }
 function request(){if(!current)throw Error(summary.textContent||'Vérifiez votre sélection de livres.');if(!form.checkValidity()){notice('Complétez vos coordonnées et cochez les deux cases obligatoires avant l’envoi.',false);form.reportValidity();return null;}const values=Object.fromEntries(new FormData(form));return {...values,terms:values.terms==='on',acknowledge:values.acknowledge==='on',lines:lines(),reservedIds:reservations(),expectedTotal:current.total,expectedSchedule:R.scheduleKey(current),startedAt};}
 function message(data){return R.summary(current)+`\n\nAcheteur : ${data.nom}\nE-mail : ${data.email}\nFacturation : ${data.billing_address||''}\nDestinataire : ${data.recipient_name||''}\n${data.address||''}\n${data.postal_code||''} ${data.city||''}\nMot pour la carte : ${data.card_message||''}\nCGV acceptées et demande sans paiement comprise.`;}
 function prepareContact(data){
  try{sessionStorage.setItem('lpgr-subscription-request',JSON.stringify({subject:'Demande d’abonnement',message:message(data),nom:data.nom,email:data.email}));}catch{}
 }
 form.addEventListener('change',e=>{if(['subscription-title','reserve-title'].includes(e.target.name)){contact.hidden=true;notice('',false);update();}});
 form.addEventListener('submit',async e=>{
  e.preventDefault();if(busy)return;
  let data;try{data=request();}catch(error){notice(error.message);return;}
  if(!data)return;
  if(!enabled){
   prepareContact(data);
   contact.hidden=false;
   notice('L’envoi direct est indisponible. Aucune demande n’a été envoyée. Ouvrez le formulaire de contact ci-dessous pour transmettre votre récapitulatif.');
   return;
  }
  busy=true;submit.disabled=true;contact.hidden=true;notice('Envoi de votre demande…',false);
  try{
   const r=await fetch('/api/subscription',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data),signal:AbortSignal.timeout(55000)});
   const answer=await r.json().catch(()=>null);
   if(!r.ok||answer?.ok!==true)throw Error(answer?.error||'L’envoi n’a pas pu être confirmé.');
   notice(answer.message);
   startedAt=Date.now();
  }catch(error){
   notice((error.name==='TimeoutError'?'L’envoi n’a pas pu être confirmé à temps.':error.message)+' Votre saisie est conservée.');
   prepareContact(data);contact.hidden=false;
  }finally{busy=false;update();result.focus();}
 });
 document.querySelector('#subscription-download').addEventListener('click',()=>{try{const data=request();if(!data)return;const url=URL.createObjectURL(new Blob([message(data)],{type:'text/plain;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='demande-abonnement.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){result.textContent=error.message;}});
 Promise.all([fetch('/content.json',{cache:'no-store'}).then(r=>r.json()),fetch('/api/subscription',{cache:'no-store'}).then(r=>r.ok?r.json():{}).catch(()=>({}))]).then(([data,service])=>{catalog=data.books;config=data.subscription||{};ready=true;enabled=service.enabled===true;const selected=Number(new URLSearchParams(location.search).get('reserver'));for(const box of form.querySelectorAll('input[type=checkbox][value]'))if(Number(box.value)===selected)box.checked=true;status.textContent=enabled?'Votre demande sera transmise aux auteurs.':'Si l’envoi direct est indisponible, vous pourrez transmettre le récapitulatif depuis le formulaire de contact.';update();}).catch(()=>status.textContent='Catalogue indisponible ; contactez contact@lesplusgrandsracontes.fr.');
})();
