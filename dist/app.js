const menu=document.querySelector('.menu-toggle');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));document.querySelector('#nav').classList.toggle('open',open)});
const fold=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let filter='available';
function filterBooks(){const query=fold(document.querySelector('#book-search')?.value||'');let count=0;document.querySelectorAll('[data-book]').forEach(el=>{el.hidden=!(filter==='all'||el.dataset.status===filter)||!fold(el.dataset.title).includes(query);if(!el.hidden)count++});const empty=document.querySelector('#empty-results');if(empty)empty.hidden=count>0;}
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button))});filterBooks()}));
document.querySelector('#book-search')?.addEventListener('input',filterBooks);
const form=document.querySelector('#contact-form');
if(form){
  const subject=new URLSearchParams(location.search).get('sujet');
  if(subject)form.elements.sujet.value=subject.slice(0,160);
  if(subject==='abonnement-personnalise'){try{const saved=JSON.parse(sessionStorage.getItem('lpgr-subscription-request')||'null');if(saved&&typeof saved.subject==='string'&&typeof saved.message==='string'){form.elements.sujet.value=saved.subject.slice(0,160);form.elements.message.value=saved.message.slice(0,5000);sessionStorage.removeItem('lpgr-subscription-request')}}catch{}}
  let startedAt=Date.now();let enabled=false;let sending=false;
  const sendButton=document.querySelector('#send-message');
  const result=document.querySelector('#message-result');
  const availability=document.querySelector('#contact-availability');
  async function checkContact(){
    try{
      const response=await fetch('/api/contact',{headers:{Accept:'application/json'},cache:'no-store',signal:AbortSignal.timeout(10000)});
      if(!response.ok)throw new Error();
      enabled=(await response.json()).enabled===true;
    }catch{enabled=false;}
    sendButton.disabled=sending;
    availability.textContent=enabled?'Votre demande sera envoyée aux auteurs. Votre adresse permet de vous répondre ; elle ne vous inscrit pas à une newsletter.':'Le bouton ouvre votre messagerie avec le message préparé. Envoyez ensuite ce message pour nous le transmettre.';
  }
  function openEmail(){if(!form.reportValidity())return;const data=new FormData(form);location.href='mailto:contact@lesplusgrandsracontes.fr?subject='+encodeURIComponent(data.get('sujet'))+'&body='+encodeURIComponent(data.get('nom')+' — '+data.get('email')+'\n'+data.get('profil')+'\n\n'+data.get('message'));result.textContent='Votre messagerie s’ouvre : envoyez le message pour nous le transmettre. Votre saisie est conservée.';}
  document.querySelector('#contact-email')?.addEventListener('click',e=>{e.preventDefault();openEmail();});
  checkContact();
  document.querySelector('#save-draft').addEventListener('click',()=>{
    const data=new FormData(form);
    const text=`${data.get('nom')} — ${data.get('profil')}\n${data.get('email')}\n\n${data.get('sujet')}\n\n${data.get('message')}`;
    const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download='demande-collection.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(sending)return;
    if(!form.reportValidity())return;
    if(!enabled){openEmail();return;}
    const data=new FormData(form);const body=Object.fromEntries(data);body.consent=data.get('consent')==='on';body.devis=data.get('devis')==='on';body.startedAt=startedAt;
    sending=true;sendButton.disabled=true;sendButton.textContent='Envoi en cours…';form.setAttribute('aria-busy','true');result.textContent='';
    try{
      const response=await fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)});
      let answer;try{answer=await response.json()}catch{throw new Error('L’envoi n’a pas pu être confirmé. Votre texte est conservé.');}
      if(!response.ok||answer.ok!==true)throw new Error(answer.error||'Votre message n’a pas été envoyé. Réessayez plus tard.');
      result.textContent=answer.message;form.reset();startedAt=Date.now();
    }catch(error){result.textContent=error.name==='TimeoutError'?'L’envoi n’a pas pu être confirmé à temps. Votre texte est conservé.':(error.message||'L’envoi a échoué. Votre texte est conservé.');}
    finally{sending=false;sendButton.disabled=sending;sendButton.textContent='Envoyer mon message ↗';form.removeAttribute('aria-busy');result.focus();}
  });
}
const moliereAudio=document.querySelector('#moliere-audio');
if(moliereAudio){
  document.querySelector('#audio-back')?.addEventListener('click',()=>{moliereAudio.currentTime=Math.max(0,moliereAudio.currentTime-10)});
  document.querySelector('#audio-speed')?.addEventListener('change',event=>{moliereAudio.playbackRate=Number(event.target.value)});
  moliereAudio.addEventListener('error',()=>{document.querySelector('#audio-status').textContent='Le fichier ne peut pas être lu pour le moment. Essayez le lien direct ci-dessous.'});
}
