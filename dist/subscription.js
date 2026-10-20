(function(root){
  'use strict';
  function calculate(count,group){
    if(!Number.isInteger(count)||count<0||count>6||![1,2,3].includes(group))throw new Error('Sélection invalide');
    const shipments=Math.ceil(count/group);
    const shipping=shipments*(group===1?5:7);
    return {count,books:count*15,shipments,shipping,total:count*15+shipping};
  }
  if(typeof module==='object'&&module.exports)module.exports={calculate};
  root.LPGRSubscription={calculate};
  if(typeof document==='undefined')return;
  const form=document.querySelector('#subscription-builder');if(!form)return;
  const boxes=Array.from(form.querySelectorAll('[name="subscription-title"]'));
  const result=document.querySelector('#subscription-summary');
  const submit=document.querySelector('#subscription-submit');
  const selected=()=>boxes.filter(box=>box.checked);
  const group=()=>Number(form.querySelector('[name="subscription-shipping"]:checked').value);
  function update(){
    const count=selected().length;
    boxes.forEach(box=>{box.disabled=count===6&&!box.checked});
    submit.disabled=count!==6;
    const current=calculate(count,group());
    result.replaceChildren();
    const title=document.createElement('strong');title.textContent=`${count} livre${count>1?'s':''} sélectionné${count>1?'s':''} sur 6`;
    const text=document.createElement('p');
    text.textContent=count===6?`${current.books} € de livres + ${current.shipping} € de port et d’emballage = ${current.total} € au total. ${current.shipments} envoi${current.shipments>1?'s':''} de ${group()} livre${group()>1?'s':''}.`:`Choisissez encore ${6-count} titre${6-count>1?'s':''}. Le total sera calculé pour les six livres.`;
    result.append(title,text);
  }
  form.addEventListener('change',update);
  form.addEventListener('submit',event=>{
    event.preventDefault();if(selected().length!==6)return;
    const value=calculate(6,group());
    const titles=selected().map(box=>`- N° ${box.value} : ${box.dataset.title} (${box.dataset.available==='true'?'disponible':'à paraître'})`);
    const request={subject:'Abonnement personnalisé — six titres',message:`Bonjour, je souhaite composer cet abonnement :\n\n${titles.join('\n')}\n\n${value.books} € de livres + ${value.shipping} € de port et d’emballage = ${value.total} €.\n${value.shipments} envois de ${group()} livre(s).\nAbonnement cadeau : ${document.querySelector('#subscription-gift').checked?'oui':'non'}. Carte et dédicace d’un des auteurs pour l’abonnement cadeau.\n\nMerci de me confirmer les dates de parution et d’envoi ainsi que les modalités de paiement en une fois.`};
    try{sessionStorage.setItem('lpgr-subscription-request',JSON.stringify(request));location.href='/contact/?sujet=abonnement-personnalise';}
    catch{result.replaceChildren();const p=document.createElement('p');p.textContent=request.message;p.style.whiteSpace='pre-wrap';const a=document.createElement('a');a.href='/contact/';a.textContent='Ouvrir le formulaire de contact →';result.append(p,a);}
  });
  update();
})(typeof globalThis!=='undefined'?globalThis:this);
