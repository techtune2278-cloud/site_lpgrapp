const test=require('node:test'),assert=require('node:assert/strict');const {createAdminService}=require('../lib/admin-service');
const env={ADMIN_PASSWORD:'mot-de-passe-de-test-assez-long',ADMIN_SESSION_SECRET:'secret-de-session-test-de-plus-de-trente-deux-caracteres',ADMIN_GITHUB_TOKEN:'fake',ADMIN_GITHUB_REPOSITORY:'test/repo'};
const headers={host:'example.org',origin:'https://example.org','content-type':'application/json'};
async function auth(handle){const r=await handle({method:'POST',headers,body:{action:'login',password:env.ADMIN_PASSWORD},ip:'test'});assert.equal(r.status,200);assert.match(r.headers['Set-Cookie'],/Secure; HttpOnly; SameSite=Strict/);return {...headers,cookie:r.headers['Set-Cookie'].split(';')[0]};}
test('Pas de lecture ou modification sans session ; origine étrangère refusée',async()=>{let calls=0;const h=createAdminService({env,fetchImpl:async()=>{calls++;}});assert.equal((await h({method:'GET',headers})).status,401);assert.equal((await h({method:'POST',headers:{...headers,origin:'https://evil.org'},body:{action:'login',password:env.ADMIN_PASSWORD}})).status,403);assert.equal(calls,0);});
test('Publication réelle via GitHub, conflit détecté et autres sections préservées',async()=>{let written;const original={books:[{title:'conservé'}],events:[],stores:[]};const h=createAdminService({env,now:()=>1000,fetchImpl:async(url,opt)=>{if(opt.method==='GET')return {ok:true,json:async()=>({sha:'old',content:Buffer.from(JSON.stringify(original)).toString('base64')})};written=JSON.parse(opt.body);return {ok:true,json:async()=>({content:{sha:'new'},commit:{sha:'commit'}})};}});const cookie=await auth(h);let r=await h({method:'POST',headers:cookie,body:{action:'save',section:'stores',sha:'stale',value:[]}});assert.equal(r.status,409);assert.equal(written,undefined);r=await h({method:'POST',headers:cookie,body:{action:'save',section:'stores',sha:'old',value:[{slug:'boutique',name:'Librairie',city:'Ville',url:'https://example.org'}]}});assert.equal(r.status,200);const saved=JSON.parse(Buffer.from(written.content,'base64'));assert.deepEqual(saved.books,original.books);assert.equal(saved.stores.length,1);assert.equal(written.branch,'main');assert.equal(written.sha,'old');});
test('Session falsifiée/expirée et chemin de rubrique non autorisé rejetés',async()=>{let time=1000;const h=createAdminService({env,now:()=>time,fetchImpl:async()=>({ok:true,json:async()=>({sha:'old',content:Buffer.from('{}').toString('base64')})})});const cookie=await auth(h);assert.equal((await h({method:'POST',headers:cookie,body:{action:'save',section:'.env',sha:'old',value:[]}})).status,400);assert.equal((await h({method:'GET',headers:{...cookie,cookie:cookie.cookie+'x'}})).status,401);time+=9*3600000;assert.equal((await h({method:'GET',headers:cookie})).status,401);});
test('Mot de passe incorrect : limitation et aucune fuite de secrets',async()=>{const h=createAdminService({env});for(let i=0;i<5;i++)assert.equal((await h({method:'POST',headers,body:{action:'login',password:'faux'},ip:'test'})).status,401);const r=await h({method:'POST',headers,body:{action:'login',password:env.ADMIN_PASSWORD},ip:'test'});assert.equal(r.status,429);assert.ok(!JSON.stringify(r).includes(env.ADMIN_SESSION_SECRET));});
test('Suppression de tous les livres, salons et points de vente dans une seule publication ; paramètres préservés',async()=>{
 let written,hookCalls=0;const original={books:[{title:'Livre'}],events:[{title:'Salon'}],stores:[{name:'Libraire'}],private_setting:'conserver'};
 const h=createAdminService({env:{...env,ADMIN_VERCEL_DEPLOY_HOOK:'https://api.vercel.com/v1/integrations/deploy/prj_test/test'},fetchImpl:async(url,opt)=>{
  if(url.startsWith('https://api.vercel.com/')){hookCalls++;return {ok:true};}
  if(opt.method==='GET')return {ok:true,json:async()=>({sha:'old',content:Buffer.from(JSON.stringify(original)).toString('base64')})};
  written=JSON.parse(opt.body);return {ok:true,json:async()=>({content:{sha:'new'},commit:{sha:'abc'}})};
 }});const cookie=await auth(h);const r=await h({method:'POST',headers:cookie,body:{action:'save',sha:'old',sections:{books:[],events:[],stores:[]}}});assert.equal(r.status,200);const raw=Buffer.from(written.content,'base64').toString();assert.deepEqual(JSON.parse(raw),{books:[],events:[],stores:[],private_setting:'conserver'});assert.equal(r.data.catalog_hash,require('node:crypto').createHash('sha256').update(raw).digest('hex'));assert.equal(hookCalls,1);assert.equal(r.data.deployment,'hook_requested');
});
test('Validation atomique : aucun commit si une autre rubrique est invalide ; échec du hook ne masque pas le commit',async()=>{
 let writes=0;const h=createAdminService({env:{...env,ADMIN_VERCEL_DEPLOY_HOOK:'https://api.vercel.com/v1/integrations/deploy/prj_test/test'},fetchImpl:async(url,opt)=>{if(url.startsWith('https://api.vercel.com/'))throw Error('injoignable');if(opt.method==='GET')return {ok:true,json:async()=>({sha:'old',content:Buffer.from('{"books":[],"events":[]}').toString('base64')})};writes++;return {ok:true,json:async()=>({content:{sha:'new'},commit:{sha:'abc'}})};}});const cookie=await auth(h);const invalid=await h({method:'POST',headers:cookie,body:{action:'save',sha:'old',sections:{events:[],books:[{number:1}]}}});assert.equal(invalid.status,400);assert.equal(writes,0);const r=await h({method:'POST',headers:cookie,body:{action:'save',sha:'old',sections:{events:[]}}});assert.equal(r.status,200);assert.equal(writes,1);assert.equal(r.data.deployment,'hook_failed');assert.ok(!JSON.stringify(r).includes('prj_test'));
});
test('Un bonus peut être chargé, publié ou supprimé sans modifier les livres',async()=>{
 let content={books:[{title:'Conservé'}]};
 const h=createAdminService({env,fetchImpl:async(url,opt)=>{
  if(opt.method==='GET')return {ok:true,json:async()=>({sha:'version',content:Buffer.from(JSON.stringify(content)).toString('base64')})};
  content=JSON.parse(Buffer.from(JSON.parse(opt.body).content,'base64'));return {ok:true,json:async()=>({content:{sha:'version'}})};
 }});
 const headers=await auth(h);
 const load=()=>h({method:'GET',headers});
 const save=value=>h({method:'POST',headers,body:{action:'save',sha:'version',sections:{bonuses:value}}});
 assert.equal((await load()).data.content.bonuses[0].author,'Molière');
 const bonus={slug:'hugo',author:'Victor Hugo',title:'Lecture',type:'audio',url:'https://example.org/lecture.mp3'};
 assert.equal((await save([{...bonus,url:'javascript:alert(1)'}])).status,400);
 assert.equal((await save([bonus])).status,200);
 assert.deepEqual((await load()).data.content.bonuses,[bonus]);
 assert.equal((await save([])).status,200);
 assert.deepEqual((await load()).data.content.bonuses,[]);
 assert.deepEqual(content.books,[{title:'Conservé'}]);
});
