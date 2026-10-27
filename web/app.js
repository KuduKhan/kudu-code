/* KUDU CODE — zero-dependency, accessible control dashboard */
'use strict';
const state = { view: 'dashboard', projects: [], tasks: [], agents: [], integrations: [], events: [], overview: null, openTask: null, busy: false };
const $ = id => document.getElementById(id);
const e = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtDate = value => value ? new Date(value).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'}) : '—';
const short = (s,max=100) => String(s||'').length>max ? String(s).slice(0,max)+'…' : String(s||'');
const titleCase = s => String(s||'').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
const buttons = (label,kind='secondary',attrs='') => `<button type="button" class="btn ${kind} small" ${attrs}>${e(label)}</button>`;
const empty = (title,body,btn,action) => `<div class="empty"><div class="empty-glyph">✳</div><h3>${e(title)}</h3><p>${e(body)}</p>${btn?buttons(btn,'secondary',`data-action="${action}"`):''}</div>`;
let toastTimer;
function toast(message,error=false){const box=$('toast');box.textContent=message;box.className='toast show'+(error?' error':'');clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.classList.remove('show'),5000)}
async function api(path,options={}){
 const token=sessionStorage.getItem('kudu-control-token')||'';
 const headers={'Content-Type':'application/json',...(token?{'Authorization':`Bearer ${token}`}:{})};
 const res=await fetch(path,{...options,headers:{...headers,...(options.headers||{})},cache:'no-store'});
 let data;try{data=await res.json()}catch{data={detail:`HTTP ${res.status}`}}
 if(!res.ok){let detail=data.detail; if(Array.isArray(detail)) detail=detail.map(x=>x.msg).join('; '); const error=new Error(String(detail||`Request failed (${res.status})`));error.status=res.status;throw error}
 return data;
}
const get = path => api(path);
const post = (path,data) => api(path,{method:'POST',body:JSON.stringify(data)});
async function load(){
 try{
  const [overview,projects,tasks,agents,integrations,events]=await Promise.all([
   get('/api/overview'),get('/api/projects'),get('/api/tasks'),get('/api/agents'),get('/api/integrations'),get('/api/events')
  ]);
  Object.assign(state,{overview,projects,tasks,agents,integrations,events});
  $('api-status').innerHTML='<span class="signal"></span> Connected';
  $('engine-health').textContent='API operational';
  $('footer-version').textContent='v'+overview.version+' · Local control';
  render();
 }catch(error){
  $('api-status').innerHTML='<span class="signal" style="background:#ff8195"></span> Offline / locked';
  $('engine-health').textContent=error.status===401?'Access token required':'Unavailable';
  if(error.status===401){showTokenModal()}else{$('view').innerHTML=`<div class="note"><strong>Unable to connect to the control plane.</strong><p>${e(error.message)}. Check that the FastAPI server is running. Your project data has not been altered.</p>${buttons('Retry connection','primary','data-action="refresh"')}</div>`}
 }
}
function pageHeading(kicker,title,sub,actions=''){
 return `<div class="page-heading"><div><div class="eyebrow">${e(kicker)}</div><h1>${e(title)}</h1><p>${e(sub)}</p></div><div class="heading-actions">${actions}</div></div>`
}
function projectRow(p){return `<div class="project-row"><div class="project-icon">${e(p.name.slice(0,2).toUpperCase())}</div><div class="item-main"><b>${e(p.name)}</b><span>${e(p.stack)} · ${e(p.workspace)}</span></div><span class="pill">Registered</span></div>`}
function taskRow(t){return `<div class="task-row"><div class="project-icon">◈</div><div class="item-main"><b>${e(t.title)}</b><span>${e(projectName(t.project_id))} · ${e(fmtDate(t.created_at))}</span></div><span class="pill ${e(t.status)}">${e(titleCase(t.status))}</span></div>`}
function projectName(id){return state.projects.find(p=>p.id===id)?.name||'Unknown project'}
function eventRow(a){return `<div class="event-row"><span class="event-dot"></span><div class="item-main"><b>${e(titleCase(a.kind))}</b><span>${e(a.message)}</span></div><span class="event-time">${e(fmtDate(a.created_at))}</span></div>`}
function overviewView(){
 const o=state.overview||{projects:0,tasks:0,active:0,completed:0};
 const stats=[['Total projects',o.projects,'▣','Connected engineering workspaces'],['Engineering tasks',o.tasks,'◈','Persisted task history'],['Active pipeline',o.active,'◷','Pending, planned or running'],['Completed tasks',o.completed,'✓','Branch pushed after verification']];
 return pageHeading('ENGINEERING COMMAND CENTER','Welcome to KUDU CODE','A centralized workspace to plan, build, test and govern your software projects.',buttons('＋ Register project','secondary','data-action="new-project"'))+
 `<div class="grid stats">${stats.map(a=>`<div class="card stat"><div class="stat-head"><span>${e(a[0])}</span><span class="stat-icon">${e(a[2])}</span></div><div class="stat-number">${a[1]}</div><div class="stat-note">${e(a[3])}</div></div>`).join('')}</div>`+
 `<div class="hero"><div class="hero-copy"><span class="hero-label">MEET YOUR ENGINEERING COMMANDER</span><h2>From idea to implementation.<br>Under your control.</h2><p>Orchestrate specialist agents, review proposed changes, verify results and deliver to GitHub with transparent approval gates.</p><button class="btn primary" data-action="new-task">✳ &nbsp; Launch an engineering task</button></div><div class="hero-art" aria-hidden="true"><div class="orb"></div><span class="orb-center">K</span><span class="spark one"></span><span class="spark two"></span></div></div>`+
 `<div class="grid workspace-grid"><section class="card section"><div class="section-head"><div><h2 class="section-title">Your projects</h2><p class="section-subtitle">Registered workspaces, organized in one place</p></div><button class="linkbutton" data-view="projects">View all →</button></div>${state.projects.length?state.projects.slice(0,5).map(projectRow).join(''):empty('No projects connected','Register a repository to begin orchestrating engineering work.','Register project','new-project')}</section>`+
 `<section class="card section"><div class="section-head"><div><h2 class="section-title">Execution snapshot</h2><p class="section-subtitle">Live task status from your control database</p></div><span class="pill">${o.tasks} total</span></div><div class="mini-metric"><span>Completed tasks</span><strong>${o.completed} / ${o.tasks}</strong></div><div class="progress-track"><div class="progress-fill" style="width:${o.tasks?o.completed/o.tasks*100:0}%"></div></div><div class="line"></div><h3 class="section-title">Recent activity</h3>${state.events.length?state.events.slice(0,4).map(eventRow).join(''):empty('No activity yet','New projects and task events will appear here.')}</section></div>`+
 `<div style="margin-top:22px" class="card section"><div class="section-head"><div><h2 class="section-title">Task pipeline</h2><p class="section-subtitle">Current engineering work</p></div><button class="linkbutton" data-view="tasks">Open tasks →</button></div>${state.tasks.length?state.tasks.slice(0,4).map(taskRow).join(''):empty('No engineering tasks','Create a task to produce a structured engineering plan.','Create task','new-task')}</div>`;
}
function projectsView(){
 return pageHeading('WORKSPACES','Project registry','Manage scoped repositories, inspect local checkouts and launch engineering tasks.',buttons('＋ Add project','primary','data-action="new-project"'))+
 (state.projects.length?`<div class="collection two">${state.projects.map(p=>`<article class="card project-card"><div class="project-card-head"><div class="project-icon">${e(p.name.slice(0,2).toUpperCase())}</div><span class="pill">${e(p.stack)}</span></div><div><h3>${e(p.name)}</h3><p>Workspace: <strong>${e(p.workspace)}</strong></p></div><div class="repo-link">${p.repo_url?`<a href="${e(p.repo_url)}" target="_blank" rel="noopener noreferrer">${e(p.repo_url)}</a>`:'No GitHub repository assigned'}</div><div class="project-card-footer">${buttons('＋ New task','primary',`data-action="new-task" data-id="${e(p.id)}"`)}${buttons('Inspect checkout','secondary',`data-action="inspect-repo" data-id="${e(p.id)}"`)}${p.repo_url?buttons('Clone','secondary',`data-action="clone-repo" data-id="${e(p.id)}"`):''}</div></article>`).join('')}</div>`:empty('Start with your first project','Register a scoped project workspace and optional GitHub repository.','Register project','new-project'));
}
function taskCard(t){
 const open=state.openTask===t.id;
 let actions=buttons(open?'Hide details':'View plan','secondary',`data-action="toggle-task" data-id="${e(t.id)}"`);
 if(t.status==='planned'||t.status==='failed') actions+=buttons('Generate AI proposal','primary',`data-action="propose" data-id="${e(t.id)}"`);
 if(t.status==='awaiting_approval') actions+=buttons('Review & apply','primary',`data-action="review" data-id="${e(t.id)}"`);
 if(t.status==='implemented'||t.status==='verification_failed') actions+=buttons('Verify in Docker','primary',`data-action="verify" data-id="${e(t.id)}"`);
 if(t.status==='verified') actions+=buttons('Push task branch','primary',`data-action="push" data-id="${e(t.id)}"`);
 if(['planned','awaiting_approval','failed'].includes(t.status))actions+=buttons('Cancel','danger',`data-action="cancel" data-id="${e(t.id)}"`);
 return `<article class="card task-card"><div class="task-meta"><span class="pill ${e(t.status)}">${e(titleCase(t.status))}</span><span class="muted" style="font-size:11px">${e(fmtDate(t.created_at))}</span></div><h3>${e(t.title)}</h3><p>${e(short(t.instruction,220))}</p><p style="font-size:11px">Project: <strong>${e(projectName(t.project_id))}</strong> ${t.branch?'· Branch: '+e(t.branch):''}</p><div class="task-actions">${actions}</div><div class="task-plan ${open?'show':''}">${t.plan?.length?t.plan.map(s=>`<div class="step"><div class="step-num">${e(s.id)}</div><div><strong>${e(s.title)}</strong><br>${e(s.objective)}</div></div>`).join(''):'No plan'}${t.result?`<div class="note">${e(t.result)}</div>`:''}</div></article>`;
}
function tasksView(){
 return pageHeading('OPERATIONS','Engineering tasks','Plan, review and execute bounded AI-assisted development workflows.',buttons('＋ New task','primary','data-action="new-task"'))+
 (state.tasks.length?`<div class="collection">${state.tasks.map(taskCard).join('')}</div>`:empty('Your pipeline is clear','Create an engineering task to generate a role-based work plan.','Create task','new-task'));
}
function agentsView(){
 const glyphs={architect:'⬡',frontend:'▤',backend:'⌘',database:'▥',devops:'⟁',qa:'✓',security:'⛨',review:'⌕'};
 return pageHeading('COORDINATION','Agent studio','Specialist roles operate under the same policy layer. Execution requires configured AI and operator approval.')+
 `<div class="card section"><div class="section-head"><div><h2 class="section-title">Engineering specialists</h2><p class="section-subtitle">${state.agents.length} roles available for task planning</p></div><span class="pill">Policy controlled</span></div><div class="agent-list">${state.agents.map(a=>`<div class="agent-item"><div class="agent-emoji">${e(glyphs[a.id]||'✳')}</div><div><h3>${e(a.name)} Agent</h3><p>${e(a.mission)}</p><span class="agent-cap">${e(a.execution)}</span></div></div>`).join('')}</div></div><div style="margin-top:18px" class="note"><strong>Execution model:</strong> This milestone uses deterministic specialist task decomposition and an optional model-backed code proposal service. Parallel independent coding workers and true multi-agent delegation are future implementation work, not enabled features.</div>`;
}
function integrationsView(){const symbols={github:'GH',vercel:'V',supabase:'S',openai:'AI'};
 return pageHeading('CONNECTED INFRASTRUCTURE','Integrations','Credential-based provider diagnostics without exposing secrets or performing infrastructure mutations.')+
 `<div class="collection two">${state.integrations.map(i=>`<div class="card connect-card"><div class="connect-icon">${e(symbols[i.name]||'◇')}</div><div class="item-main"><h3>${e(i.name)}</h3><p>${e(i.mode)}</p></div><div class="connect-status"><span class="pill ${i.configured?'verified':''}">${i.configured?'Configured':'Not configured'}</span>${i.name!=='openai'?buttons('Check','secondary',`data-action="check-provider" data-id="${e(i.name)}"`):''}</div></div>`).join('')}</div><div class="note" style="margin-top:18px"><strong>How to connect:</strong> Set provider credentials in your server-side environment only, then restart KUDU CODE. A configured token is not proof of a working connection; use the Check action to verify. Production deploys and database writes are not enabled by these diagnostics.</div>`;
}
function activityView(){return pageHeading('TRACEABILITY','Audit activity','An append-only application event timeline. Protect the underlying database with backups and restricted filesystem permissions.')+
 `<section class="card section">${state.events.length?state.events.map(eventRow).join(''):empty('No recorded events','Project and execution events will appear as you work.')}</section>`}
function settingsView(){const connected=!!sessionStorage.getItem('kudu-control-token');return pageHeading('CONFIGURATION','Control settings','Manage local console access and inspect enabled capabilities.')+
 `<section class="card section"><div class="settings-line"><div><h3>API access token</h3><p>${connected?'Token stored in this browser tab session':'Using local-only access unless server requires authentication'}</p></div>${buttons(connected?'Update / clear token':'Set token','secondary','data-action="auth-token"')}</div><div class="settings-line"><div><h3>AI proposal provider</h3><p>Configure OPENAI_API_KEY and KUDU_MODEL on the server; no model key is sent through the web UI.</p></div><span class="pill">${state.integrations.find(i=>i.name==='openai')?.configured?'Configured':'Disabled'}</span></div><div class="settings-line"><div><h3>Approval mode</h3><p>Explicit approval required before modifying a project branch or pushing code.</p></div><span class="pill verified">Enforced</span></div><div class="settings-line"><div><h3>Software release</h3><p>Deployed version of the KUDU CODE control plane</p></div><span class="kbd">v${e(state.overview?.version||'–')}</span></div></section><div class="note" style="margin-top:18px"><strong>Production restriction:</strong> This single-operator preview is not production-multi-tenant ready. Put it behind secure identity authentication, secret management, protected networking and durable job orchestration before hosting it publicly.</div>`}
function render(){
 const labels={dashboard:'Overview',projects:'Projects',tasks:'Engineering tasks',agents:'Agent studio',integrations:'Integrations',activity:'Activity log',settings:'Settings'};
 const views={dashboard:overviewView,projects:projectsView,tasks:tasksView,agents:agentsView,integrations:integrationsView,activity:activityView,settings:settingsView};
 $('breadcrumb').textContent=labels[state.view]||'Overview';
 document.querySelectorAll('.nav').forEach(n=>{n.classList.toggle('active',n.dataset.view===state.view);n.setAttribute('aria-current',n.dataset.view===state.view?'page':'false')});
 $('view').innerHTML=(views[state.view]||overviewView)();
}
function openModal(content){$('overlay').innerHTML=`<div class="modal" role="dialog" aria-modal="true" aria-label="KUDU CODE dialog">${content}</div>`;$('overlay').classList.remove('hidden');$('overlay').querySelector('input,select,textarea,button')?.focus()}
function closeModal(){$('overlay').classList.add('hidden');$('overlay').innerHTML=''}
function modalHeader(title,sub){return `<div class="modal-head"><div><h2>${e(title)}</h2><p>${e(sub)}</p></div><button class="close" data-action="close-modal" aria-label="Close dialog">×</button></div>`}
function newProjectModal(){openModal(modalHeader('Register a project','Create an isolated workspace for your source repository.')+`<form id="project-form"><div class="field"><label for="project-name">Project name</label><input id="project-name" name="name" maxlength="80" placeholder="e.g. KHANIVERSITY" required></div><div class="field"><label for="project-slug">Workspace slug</label><input id="project-slug" name="workspace" pattern="[a-z][a-z0-9-]{1,47}" placeholder="e.g. khaniversity" required><small>Lowercase letters, digits and dashes.</small></div><div class="field"><label for="project-repo">GitHub HTTPS URL (optional)</label><input id="project-repo" name="repo_url" type="url" placeholder="https://github.com/owner/repository"></div><div class="field"><label for="project-stack">Technology stack</label><input id="project-stack" name="stack" maxlength="80" placeholder="Next.js / Python / PostgreSQL"></div><div class="modal-actions">${buttons('Cancel','secondary','data-action="close-modal"')}<button class="btn primary" type="submit">Register project</button></div></form>`)}
function newTaskModal(selected=''){if(!state.projects.length){toast('Register a project before creating a task.',true);newProjectModal();return}
 openModal(modalHeader('Launch engineering task','Define the exact change, then inspect the generated execution plan.')+`<form id="task-form"><div class="field"><label for="task-project">Target project</label><select id="task-project" name="project_id" required>${state.projects.map(p=>`<option value="${e(p.id)}" ${selected===p.id?'selected':''}>${e(p.name)}</option>`).join('')}</select></div><div class="field"><label for="task-title">Task title</label><input id="task-title" name="title" maxlength="120" placeholder="e.g. Improve mobile learner dashboard" required></div><div class="field"><label for="task-instruction">Engineering instruction</label><textarea id="task-instruction" name="instruction" minlength="12" maxlength="12000" placeholder="Describe the requirements, constraints, target behavior, quality expectations and acceptance criteria..." required></textarea><small>AI-generated file changes require configuration and separate approval.</small></div><div class="modal-actions">${buttons('Cancel','secondary','data-action="close-modal"')}<button class="btn primary" type="submit">Create task plan</button></div></form>`)}
function showTokenModal(){openModal(modalHeader('Authenticate control console','Enter the operator token configured on the API server. It is stored only for this browser tab session.')+`<form id="token-form"><div class="field"><label for="control-token">Bearer token</label><input id="control-token" name="token" type="password" autocomplete="off" placeholder="KUDU_CONTROL_TOKEN" required></div><div class="modal-actions"><button class="btn secondary" type="button" data-action="clear-token">Clear token</button><button class="btn primary" type="submit">Connect securely</button></div></form>`)}
function reviewModal(t){const p=t.proposal;if(!p){toast('No proposed files to review.',true);return}openModal(modalHeader('Review proposed changes','Approve only if the listed files and content are expected. Changes are committed to a new task branch.')+`<div class="note"><strong>${e(p.summary)}</strong></div><p class="warning-text" style="margin:17px 0 10px">${p.files.length} file(s) will be written to the checkout on explicit approval.</p><div class="code-preview">${p.files.map(f=>`${f.new?'NEW':'EDIT'}  ${f.path}\n${short(f.content,600)}`).map(e).join('\n\n')}</div><div class="modal-actions">${buttons('Reject / close','secondary','data-action="close-modal"')}<button class="btn primary" data-action="apply" data-id="${e(t.id)}">Approve & commit branch</button></div>`)}
async function executeAction(action,id){
 if(state.busy)return;
 state.busy=true;
 try{
  if(action==='propose') {await post(`/api/tasks/${id}/propose`,{});toast('Proposal generated and awaiting approval.')}
  if(action==='clone-repo'){if(!confirm('Clone this repository into its local isolated workspace?'))return;await post(`/api/projects/${id}/clone`,{});toast('Repository cloned.')}
  if(action==='inspect-repo'){const result=await get(`/api/projects/${id}/repository`);toast(result.cloned?`Branch: ${result.branch||'detached'} · ${result.files} tracked files · ${result.dirty?'Dirty':'Clean'}`:'Repository is not cloned yet.')}
  if(action==='cancel'){if(!confirm('Cancel this task?'))return;await post(`/api/tasks/${id}/cancel`,{});toast('Task cancelled.')}
  if(action==='apply'){if(!confirm('Commit these AI-proposed file changes to a new task branch?'))return;await post(`/api/tasks/${id}/apply`,{confirm:true});closeModal();toast('Approved changes committed to task branch. Verification is still required.')}
  if(action==='verify'){await post(`/api/tasks/${id}/verify`,{command:'python-syntax'});toast('Docker verification finished. Inspect task result for details.')}
  if(action==='push'){if(!confirm('Push the verified task branch to GitHub? This will not merge or deploy production.'))return;await post(`/api/tasks/${id}/push`,{confirm:true});toast('Task branch pushed to GitHub.')}
  if(action==='check-provider'){const res=await get(`/api/integrations/${id}/check`);toast(`${titleCase(id)}: ${res.reason}`,!res.connected)}
  if(action!=='check-provider' && action!=='inspect-repo')await load();
 }catch(err){toast(err.message,true)}finally{state.busy=false}
}
document.addEventListener('click',event=>{
 const view=event.target.closest('[data-view]');
 if(view){state.view=view.dataset.view;state.openTask=null;render();$('sidebar').classList.remove('open');window.scrollTo({top:0,behavior:'instant'});return}
 const act=event.target.closest('[data-action]');if(!act)return;
 const action=act.dataset.action,id=act.dataset.id;
 if(action==='close-modal')closeModal();
 else if(action==='new-project')newProjectModal();
 else if(action==='new-task')newTaskModal(id);
 else if(action==='refresh')load();
 else if(action==='auth-token')showTokenModal();
 else if(action==='clear-token'){sessionStorage.removeItem('kudu-control-token');closeModal();load()}
 else if(action==='toggle-task'){state.openTask=state.openTask===id?null:id;render()}
 else if(action==='review')reviewModal(state.tasks.find(t=>t.id===id));
 else executeAction(action,id);
});
document.addEventListener('submit',async event=>{
 if(!['project-form','task-form','token-form'].includes(event.target.id))return;
 event.preventDefault();const form=event.target;const submit=form.querySelector('[type=submit]');submit.disabled=true;
 const values=Object.fromEntries(new FormData(form).entries());
 try{
  if(form.id==='token-form'){sessionStorage.setItem('kudu-control-token',values.token);closeModal();await load();return}
  if(form.id==='project-form'){await post('/api/projects',values);toast('Workspace registered successfully.');state.view='projects'}
  if(form.id==='task-form'){await post('/api/tasks',values);toast('Engineering plan created.');state.view='tasks'}
  closeModal();await load();
 }catch(err){toast(err.message,true);submit.disabled=false}
});
$('menu').addEventListener('click',()=>{$('sidebar').classList.toggle('open')});
$('header-new').addEventListener('click',()=>newTaskModal());
$('overlay').addEventListener('click',event=>{if(event.target===$('overlay'))closeModal()});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){$('sidebar').classList.remove('open');closeModal()}});
load();
