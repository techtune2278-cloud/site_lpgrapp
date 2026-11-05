(()=>{for(const book of document.querySelectorAll('[data-flipbook]')){
 const pages=[...book.querySelectorAll('[data-flip-page]')],buttons=[...book.querySelectorAll('[data-flip-index]')];if(!pages.length)continue;let index=0,startX=null,startY=null;
 const prev=book.querySelector('[data-flip-prev]'),next=book.querySelector('[data-flip-next]'),counter=book.querySelector('[data-flip-counter]');
 function show(i){index=Math.max(0,Math.min(pages.length-1,i));pages.forEach((p,n)=>{p.hidden=n!==index;p.setAttribute('aria-hidden',String(n!==index));});buttons.forEach((b,n)=>{b.setAttribute('aria-pressed',String(n===index));b.classList.toggle('active',n===index);});prev.disabled=index===0;next.disabled=index===pages.length-1;counter.textContent=`Page ${index+1} sur ${pages.length}`;}
 book.classList.add('flipbook-ready');book.tabIndex=0;book.querySelector('.flipbook-controls').hidden=false;book.querySelector('.flipbook-thumbs').hidden=false;
 prev.addEventListener('click',()=>show(index-1));next.addEventListener('click',()=>show(index+1));buttons.forEach((b,n)=>b.addEventListener('click',()=>show(n)));
 book.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();show(index+(e.key==='ArrowLeft'?-1:1));}});
 book.querySelector('.flipbook-stage').addEventListener('touchstart',e=>{startX=e.changedTouches[0].clientX;startY=e.changedTouches[0].clientY;},{passive:true});
 book.querySelector('.flipbook-stage').addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-startX,dy=e.changedTouches[0].clientY-startY;if(startX!==null&&Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))show(index+(dx<0?1:-1));startX=null;},{passive:true});
 const dialog=document.createElement('dialog');dialog.className='flipbook-dialog';const close=document.createElement('button');close.type='button';close.textContent='Fermer ×';const image=document.createElement('img');dialog.append(close,image);document.body.append(dialog);let focus;
 function zoom(e){e?.preventDefault();focus=document.activeElement;image.src=pages[index].href;image.alt=pages[index].querySelector('img').alt;dialog.showModal();}
 close.addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});dialog.addEventListener('close',()=>focus?.focus());book.querySelector('[data-flip-zoom]').addEventListener('click',zoom);pages.forEach(p=>p.addEventListener('click',zoom));show(0);
}})();
