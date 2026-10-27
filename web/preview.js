/* Hosted Vercel showcase: make read-only constraints clear to visitors.
   The backend independently denies every mutation; this is UX-only defense. */
(() => {
  'use strict';
  const blocked = new Set([
    'new-project', 'new-task', 'propose', 'review', 'verify', 'push',
    'create-pr', 'cancel', 'clone-repo', 'inspect-repo', 'auth-token',
    'clear-token', 'apply', 'approve', 'submit'
  ]);
  function notice(message) {
    const node = document.getElementById('toast');
    if (!node) return;
    node.textContent = message;
    node.className = 'toast show';
    window.setTimeout(() => node.classList.remove('show'), 4500);
  }
  async function setup() {
    try {
      const response = await fetch('/api/health', {cache:'no-store'});
      if (!response.ok || !(await response.json()).read_only) return;
    } catch { return; }
    document.body.dataset.hostedPreview = 'true';
    const header = document.querySelector('.topbar');
    if (header) {
      const banner = document.createElement('div');
      banner.className = 'hosted-preview-banner';
      banner.setAttribute('role', 'status');
      banner.textContent = 'VERCEL PREVIEW · READ-ONLY SHOWCASE — Agent execution, persistence and write operations are not active.';
      header.insertAdjacentElement('afterend', banner);
    }
    const status = document.getElementById('engine-health');
    if (status) status.textContent = 'Read-only demo API';
    const profile = document.querySelector('.profile b');
    if (profile) profile.textContent = 'Preview visitor';
    const version = document.getElementById('footer-version');
    if (version) version.textContent = 'v1.0.0-preview · Read-only Vercel';
    const newTask = document.getElementById('header-new');
    if (newTask) newTask.setAttribute('title', 'Disabled in read-only preview');
    document.addEventListener('click', event => {
      const button = event.target.closest('button');
      if (!button) return;
      const action = button.dataset.action;
      if (button.id === 'header-new' || blocked.has(action)) {
        event.preventDefault();
        event.stopImmediatePropagation();
        notice('This is a read-only Vercel preview. Run the secured local control plane for engineering actions.');
      }
    }, true);
    document.addEventListener('submit', event => {
      event.preventDefault();
      event.stopImmediatePropagation();
      notice('Forms are disabled in the read-only Vercel preview.');
    }, true);
  }
  setup();
})();
