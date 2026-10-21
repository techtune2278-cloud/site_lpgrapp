const test=require('node:test'),assert=require('node:assert/strict');
const {createSubscriptionService}=require('../lib/subscription-service');
const catalog=[{number:1,title:'Rimbaud',price:9,status:'paru',subscription_payable:true},{number:12,title:'Baudelaire',price:15,status:'prochain',subscription_payable:false}];
const env={BREVO_API_KEY:'fake-test',CONTACT_FROM_EMAIL:'sender@example.org'};
const body={nom:'Test lecteur',email:'test@example.net',consent:true,website:'',startedAt:1000,paidIds:[1],reservedIds:[12],shipments:1,expectedTotal:13.5,recipient_name:'Destinataire test',address:'Adresse de test',postal_code:'00000',city:'Ville de test',country:'France',card_message:'Bonne lecture !'};
const req={method:'POST',headers:{origin:'https://example.org',host:'example.org','content-type':'application/json'},body,ip:'test'};
test('Adresse, carte, sélection et réservations sont envoyées au contact fixe, total recalculé côté serveur',async()=>{
 let sent;const handle=createSubscriptionService({catalog,env,now:()=>5000,fetchImpl:async(url,options)=>{sent=JSON.parse(options.body);return {ok:true,json:async()=>({messageId:'test'})};}});
 const answer=await handle(req);assert.equal(answer.status,200);assert.equal(sent.to[0].email,'contact@lesplusgrandsracontes.fr');assert.match(sent.textContent,/13,50/);assert.match(sent.textContent,/Bonne lecture/);assert.match(sent.textContent,/Réservations sans paiement/);assert.equal(sent.replyTo.email,body.email);
});
test('Montant falsifié, réservation facturée et adresse invalide ne déclenchent aucun envoi',async()=>{
 let calls=0;const handle=createSubscriptionService({catalog,env,now:()=>5000,fetchImpl:async()=>{calls++;throw Error();}});
 for(const change of [{expectedTotal:1},{paidIds:[12],reservedIds:[]},{postal_code:'bad'},{consent:false},{country:'Italie'}])assert.ok((await handle({...req,body:{...body,...change}})).status>=400);
 assert.equal(calls,0);
});
test('Une réservation seule ne nécessite pas d’adresse et reste à zéro euro',async()=>{
 let sent;const handle=createSubscriptionService({catalog,env,now:()=>5000,fetchImpl:async(url,options)=>{sent=JSON.parse(options.body);return {ok:true,json:async()=>({messageId:'test'})};}});
 const answer=await handle({...req,body:{nom:body.nom,email:body.email,consent:true,startedAt:1000,paidIds:[],reservedIds:[12],shipments:0,expectedTotal:0}});assert.equal(answer.status,200);assert.match(sent.subject,/Réservation sans paiement/);assert.match(sent.textContent,/0,00/);
});
test('Erreur fournisseur ou absence de configuration ne signale pas un succès',async()=>{
 const disabled=createSubscriptionService({catalog,env:{},now:()=>5000});assert.equal((await disabled(req)).status,503);
 const denied=createSubscriptionService({catalog,env,now:()=>5000,fetchImpl:async()=>({ok:false})});assert.equal((await denied(req)).status,502);
});
