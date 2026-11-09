'use strict';

const EMAIL = /^[^\s<>@,;:"\\()\[\]]+@[^\s<>@,;:"\\()\[\]]+\.[^\s<>@,;:"\\()\[\]]+$/;
function settings(env) {
  const user = (env.GMAIL_USER || '').trim();
  return {user, password:(env.GMAIL_APP_PASSWORD || '').replace(/\s/g,''), recipient:(env.CONTACT_TO_EMAIL || user).trim()};
}
function isConfigured(env) {
  const {user,password,recipient}=settings(env);
  return EMAIL.test(user) && /^[a-z0-9]{16}$/i.test(password) && EMAIL.test(recipient);
}
function createGmailMailer(env, createTransport) {
  let transport;
  return async ({to,replyTo,subject,text,attachments})=>{
    if(!isConfigured(env)||!EMAIL.test(to))return false;
    const {user,password}=settings(env);
    if(!transport){
      const factory=createTransport||require('nodemailer').createTransport;
      transport=factory({host:'smtp.gmail.com',port:465,secure:true,auth:{user,pass:password},connectionTimeout:5000,greetingTimeout:5000,socketTimeout:8000,disableFileAccess:true,disableUrlAccess:true});
    }
    const result=await transport.sendMail({from:{name:env.CONTACT_FROM_NAME||'Les plus grands racontés aux plus petits',address:user},to:{address:to},replyTo,subject,text,attachments});
    return Array.isArray(result.accepted)&&result.accepted.some(address=>address.toLowerCase()===to.toLowerCase());
  };
}
module.exports={createGmailMailer,isConfigured,settings,EMAIL};
