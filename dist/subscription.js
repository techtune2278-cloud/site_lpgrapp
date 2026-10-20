(function(root){
  'use strict';
  function calculate(count,group,books=count*15){
    if(!Number.isInteger(count)||count<0||count>6||![1,2,3].includes(group)||!Number.isFinite(books)||books<0||(count===0&&books!==0))throw new Error('Sélection invalide');
    const shipments=Math.ceil(count/group),shipping=shipments*(group===1?4.5:7);
    return {count,books,shipments,shipping,total:books+shipping};
  }
  function validSelection(books,pack){
    if(!['decouverte','passion'].includes(pack)||books.length!==6||new Set(books.map(b=>b.number)).size!==6)return false;
    const cheap=books.filter(b=>[1,2].includes(b.number));
    if(books.some(b=>[10,20,30].includes(b.number)))return false;
    if(pack==='passion')return cheap.length===0&&books.every(b=>b.price===15);
    return cheap.length===2&&cheap.every(b=>b.price===9)&&books.filter(b=>![1,2].includes(b.number)).every(b=>b.price===15);
  }
  if(typeof module==='object'&&module.exports)module.exports={calculate,validSelection};
  root.LPGRSubscription={calculate,validSelection};
  if(typeof document==='undefined')return;
  const form=document.querySelector('#subscription-builder');if(!form)return;
  const boxes=Array.from(form.querySelectorAll('[name="subscription-title"]'));
  const result=document.querySelector('#subscription-summary'),submit=document.querySelector('#subscription-submit');
  const selected=()=>boxes.filter(box=>box.checked);
  const group=()=>Number(form.querySelector('[name="subscription-shipping"]:checked').value);
  const pack=()=>form.querySelector('[name="subscription-pack"]:checked').value;
  const items=()=>selected().map(box=>({number:Number(box.value),price:Number(box.dataset.price)}));
  function configure(reset){
    for(const box of boxes){const starter=[1,2].includes(Number(box.value));if(starter){box.checked=pack()==='decouverte';box.closest('label').hidden=pack()!=='decouverte';}else if(reset)box.checked=false;}
    document.querySelector('#subscription-selection-help').textContent=pack()==='decouverte'?'Pack Découverte : Rimbaud et Hugo sont inclus ; choisissez quatre autres titres à 15 €.':'Pack Passion : choisissez six titres à 15 €, hors Rimbaud, Hugo et Collectors.';
    update();
  }
  function update(){
    const count=selected().length;
    for(const box of boxes)box.disabled=[1,2].includes(Number(box.value))||(count===6&&!box.checked);
    submit.disabled=!validSelection(items(),pack());
    result.replaceChildren();const title=document.createElement('strong');title.textContent=`${count} livre${count>1?'s':''} sélectionné${count>1?'s':''} sur 6`;
    const text=document.createElement('p');const value=calculate(count,group(),items().reduce((sum,b)=>sum+b.price,0));
    text.textContent=count===6?`${value.books} € de livres + ${value.shipping} € de port = ${value.total} € au total. ${value.shipments} envois en Lettre suivie de ${group()} livre(s). Carte et dédicace d’un des auteurs comprises.`:`Choisissez encore ${6-count} titre${6-count>1?'s':''}. Le total sera calculé pour les six livres.`;
    result.append(title,text);
  }
  form.addEventListener('change',event=>event.target.name==='subscription-pack'?configure(true):update());
  form.addEventListener('submit',event=>{
    event.preventDefault();if(!validSelection(items(),pack()))return;
    const value=calculate(6,group(),items().reduce((sum,b)=>sum+b.price,0));
    const name=pack()==='decouverte'?'Découverte':'Passion';
    const rhythm={1:'Plaisir',2:'Équilibre',3:'Éco'}[group()];
    const titles=selected().map(box=>`- N° ${box.value} : ${box.dataset.title}, ${box.dataset.price} € (${box.dataset.available==='true'?'disponible':'à paraître'})`);
    const request={subject:`Abonnement ${name} — formule ${rhythm}`,message:`Bonjour, je souhaite composer cet abonnement :\n\nPack ${name} — formule ${rhythm}\n${titles.join('\n')}\n\n${value.books} € de livres + ${value.shipping} € de port = ${value.total} €.\n${value.shipments} envois de ${group()} livre(s) en Lettre suivie, France.\nAbonnement cadeau : ${document.querySelector('#subscription-gift').checked?'oui':'non'}. Carte et dédicace d’un des auteurs comprises.\n\nMerci de me confirmer les dates de parution et d’envoi ainsi que les modalités de paiement en une fois.`};
    try{sessionStorage.setItem('lpgr-subscription-request',JSON.stringify(request));location.href='/contact/?sujet=abonnement-personnalise';}
    catch{result.replaceChildren();const p=document.createElement('p');p.textContent=request.message;p.style.whiteSpace='pre-wrap';const a=document.createElement('a');a.href='/contact/';a.textContent='Ouvrir le formulaire de contact →';result.append(p,a);}
  });
  configure(false);
})(typeof globalThis!=='undefined'?globalThis:this);
