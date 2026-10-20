// Vercel et poste local : prépare les dépendances du générateur puis compile.
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
const root=resolve(import.meta.dirname,'..');
const python=process.env.LPGR_PYTHON || (process.platform==='win32'?'python':'python3');
function run(command,args){const result=spawnSync(command,args,{cwd:root,stdio:'inherit'});if(result.error)throw result.error;if(result.status!==0)process.exit(result.status||1);}
const probe=spawnSync(python,['-c','import PIL; assert int(PIL.__version__.split(".")[0]) >= 12'],{cwd:root,stdio:'ignore'});
if(probe.status===0){run(python,['build.py']);}else{
 const venvPython=resolve(root,'.build-venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
 if(!existsSync(venvPython))run(python,['-m','venv','.build-venv']);
 run(venvPython,['-m','pip','install','--disable-pip-version-check','-r','requirements.txt']);
 run(venvPython,['build.py']);
}
