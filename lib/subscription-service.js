'use strict';
const {quote,summary}=require('./subscription-rules');
const {createContactService}=require('./contact-service');
function createSubscriptionService({catalog,env=process.env,fetchImpl=globalThis.fetch,now=Date.now}={}){
 const contact=createContactService({env:{...env,CONTACT_TO_EMAIL:'contact@lesplusgrandsracontes.fr'},fetchImpl,now});
 return async function handle(request){
  if(request.method!=='POST')return contact(request);
  const fail=(status,error)=>({status,data:{error},headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
  let data;
  try{if(Number(request.headers?.['content-length'])>24000||Buffer.byteLength(JSON.stringify(request.body)||'')>24000)return fail(413,'Demande trop volumineuse.');data=typeof request.body==='string'?JSON.parse(request.body):request.body;}catch{return fail(400,'Demande illisible.');}
  if(!data||typeof data!=='object'||Array.isArray(data))return fail(400,'Demande invalide.');
  let value;try{value=quote(catalog,data.paidIds,data.reservedIds,data.shipments);}catch(error){return fail(400,error.message);}
  if(data.expectedTotal!==value.total)return fail(409,'Le montant a changé. Rechargez la page avant d’envoyer votre demande.');
  const fields={phone:40,recipient_name:120,address:200,address_extra:200,postal_code:5,city:120,card_message:1000};
  for(const [key,max] of Object.entries(fields))if(data[key]!==undefined&&(typeof data[key]!=='string'||data[key].length>max||(key!=='card_message'&&/[\r\n]/.test(data[key]))))return fail(400,'Vérifiez les coordonnées et le mot pour la carte.');
  if(value.paid.length){
   for(const key of ['recipient_name','address','postal_code','city'])if(!data[key]?.trim())return fail(400,'Complétez les coordonnées du destinataire.');
   if(!/^\d{5}$/.test(data.postal_code)||data.country!=='France')return fail(400,'Les tarifs affichés concernent une livraison en France. Contactez-nous pour une autre destination.');
  }
  const message=summary(value)+`\n\nDestinataire : ${data.recipient_name||'À confirmer lors de la réservation'}\nAdresse : ${data.address||''}\n${data.address_extra||''}\n${data.postal_code||''} ${data.city||''}\nPays : ${data.country||'France'}\n\nMot pour la carte :\n${data.card_message||'Aucun'}\n\nTéléphone de l’acheteur : ${data.phone||'Non renseigné'}`;
  return contact({...request,body:{nom:data.nom,email:data.email,profil:'Un particulier',sujet:value.paid.length?'Demande d’abonnement libre':'Réservation sans paiement',message,consent:data.consent,website:data.website,startedAt:data.startedAt}});
 };
}
module.exports={createSubscriptionService};
