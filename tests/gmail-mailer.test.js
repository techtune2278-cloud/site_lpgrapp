'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {createGmailMailer,isConfigured}=require('../lib/gmail-mailer');
const env={GMAIL_USER:'site@gmail.com',GMAIL_APP_PASSWORD:'abcd efgh ijkl mnop'};
test('Gmail utilise TLS, le compte authentifié comme expéditeur et conserve le Reply-To et les CGV',async()=>{
 let options,message;
 const send=createGmailMailer(env,config=>{options=config;return{sendMail:async data=>{message=data;return{accepted:['client@example.org']};}};});
 const attachments=[{filename:'CGV.txt',content:'CGV'}];
 assert.equal(await send({to:'client@example.org',replyTo:{address:'client@example.org'},subject:'Confirmation',text:'Demande reçue',attachments}),true);
 assert.equal(options.host,'smtp.gmail.com');assert.equal(options.port,465);assert.equal(options.secure,true);
 assert.equal(options.auth.pass,'abcdefghijklmnop');
 assert.equal(message.from.address,env.GMAIL_USER);assert.equal(message.to.address,'client@example.org');assert.equal(message.replyTo.address,'client@example.org');assert.deepEqual(message.attachments,attachments);
});
test('Configuration incomplète, destinataire invalide et refus SMTP ne sont jamais un succès',async()=>{
 assert.equal(isConfigured({...env,GMAIL_APP_PASSWORD:''}),false);
 const send=createGmailMailer(env,()=>({sendMail:async()=>({accepted:[],rejected:['client@example.org']})}));
 assert.equal(await send({to:'client@example.org'}),false);
 assert.equal(await send({to:'client@example.org,autre@example.org'}),false);
});
