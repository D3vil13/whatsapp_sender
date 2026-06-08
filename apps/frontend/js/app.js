/* ================================================================
   BulkPing — App Router & Core
   ================================================================ */

const app = {
  currentPage: 'login',
  sidebarCollapsed: false,

  async init() {
    api.init();
    this.render();
    this.bindEvents();
    this.route();
    window.addEventListener('hashchange', () => this.route());
  },

  render() {
    document.getElementById('app-shell').innerHTML = this.shellHTML();
    this.renderSidebar();
  },

  shellHTML() {
    return `
      <div id="shell-login" class="login-page hidden"></div>
      <div id="shell-authed" class="hidden">
        <div class="app">
          <aside id="sidebar" class="sidebar"></aside>
          <div class="main">
            <header id="header" class="header">
              <span id="page-title" class="header-title">Dashboard</span>
              <div id="header-actions" class="header-actions"></div>
            </header>
            <div id="content" class="content">
              <div id="page-dashboard" class="page active"></div>
              <div id="page-connect" class="page"></div>
              <div id="page-campaigns" class="page"></div>
              <div id="page-contacts" class="page"></div>
              <div id="page-analytics" class="page"></div>
              <div id="page-settings" class="page"></div>
            </div>
            <footer class="footer">
              <span>© ${new Date().getFullYear()} BulkPing — WhatsApp BSP</span>
              <span><a href="#" onclick="event.preventDefault();app.showAbout()">v1.0.0</a></span>
            </footer>
          </div>
        </div>
      </div>
    `;
  },

  renderSidebar() {
    const sidebar = document.getElementById('sidebar');
    const collapsed = this.sidebarCollapsed ? ' collapsed' : '';
    sidebar.innerHTML = `
      <div class="sidebar-header">
        <div class="logo">BP</div>
        <span class="brand-name">BulkPing</span>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Main</div>
        ${this.navItem('dashboard', 'Dashboard', '#/dashboard', this.icon('dashboard'))}
        ${this.navItem('connect', 'Connect', '#/connect', this.icon('connect'))}
        ${this.navItem('campaigns', 'Campaigns', '#/campaigns', this.icon('campaigns'))}
        ${this.navItem('contacts', 'Contacts', '#/contacts', this.icon('contacts'))}
        ${this.navItem('analytics', 'Analytics', '#/analytics', this.icon('analytics'))}
        <div class="nav-section-label">System</div>
        ${this.navItem('settings', 'Settings', '#/settings', this.icon('settings'))}
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-toggle" onclick="app.toggleSidebar()">
          ${this.icon('collapse')}
          <span class="sidebar-footer-text">Collapse</span>
        </div>
      </div>
    `;
  },

  navItem(id, label, href, iconHTML) {
    const active = this.currentPage === id ? ' active' : '';
    const onclick = `onclick="event.preventDefault();app.navigate('${id}')"`;
    return `<a href="${href}" class="nav-item${active}" ${onclick} data-nav="${id}">
      <span class="nav-icon">${iconHTML}</span>
      <span class="nav-label">${label}</span>
    </a>`;
  },

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
    document.getElementById('sidebar').classList.toggle('collapsed', this.sidebarCollapsed);
  },

  navigate(page) {
    this.currentPage = page;
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelector(`.nav-item[data-nav="${page}"]`)?.classList.add('active');
    document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
    document.getElementById(`page-${page}`)?.classList.add('active');
    this.updateHeader(page);
    this.renderPage(page);
  },

  updateHeader(page) {
    const titles = { dashboard: 'Dashboard', connect: 'Connect WhatsApp', campaigns: 'Campaigns', contacts: 'Contacts & Groups', analytics: 'Analytics', settings: 'Settings' };
    document.getElementById('page-title').textContent = titles[page] || page;
    document.getElementById('header-actions').innerHTML = page === 'campaigns'
      ? '<button class="btn btn-primary btn-sm" onclick="app.navigate(\'campaigns\');campaigns.openNew()">+ New Campaign</button>'
      : '';
  },

  async renderPage(page) {
    const el = document.getElementById(`page-${page}`);
    if (!el) return;
    el.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';
    try {
      if (typeof this[`render_${page}`] === 'function') await this[`render_${page}`](el);
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  route() {
    const hash = location.hash.slice(1) || '/dashboard';
    const path = hash.split('?')[0];
    const pageMap = {
      '/login': 'login',
      '/dashboard': 'dashboard',
      '/connect': 'connect',
      '/campaigns': 'campaigns',
      '/contacts': 'contacts',
      '/analytics': 'analytics',
      '/settings': 'settings',
      '/campaign-detail': 'campaigns',
    };

    if (!api.isLoggedIn() && path !== '/login') {
      location.hash = '#/login';
      return;
    }

    const page = pageMap[path] || 'dashboard';
    if (path === '/login') {
      document.getElementById('shell-login').classList.remove('hidden');
      document.getElementById('shell-authed').classList.add('hidden');
      this.renderLogin();
    } else {
      document.getElementById('shell-login').classList.add('hidden');
      document.getElementById('shell-authed').classList.remove('hidden');
      this.navigate(page);
    }
  },

  /* --- Icon SVGs --- */
  icon(name) {
    const icons = {
      dashboard: '<svg viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>',
      connect: '<svg viewBox="0 0 24 24"><path d="M3.4 20.4l17.45-7.48a1 1 0 000-1.84L3.4 3.6a.99.99 0 00-1.39 1.06L3.77 12 2.01 19.34a1 1 0 001.39 1.06z"/></svg>',
      campaigns: '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>',
      contacts: '<svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
      analytics: '<svg viewBox="0 0 24 24"><path d="M5 9.2h3V19H5V9.2zM10.6 5h2.8v14h-2.8V5zm5.6 8H19v6h-2.8v-6z"/></svg>',
      settings: '<svg viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.488.488 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 1115.6 12 3.611 3.611 0 0112 15.6z"/></svg>',
      collapse: '<svg viewBox="0 0 24 24" width="18" height="18"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>',
    };
    return icons[name] || '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg>';
  },

  /* --- Toast --- */
  toast(message, type = 'success') {
    const div = document.createElement('div');
    div.style.cssText = `position:fixed;bottom:80px;right:20px;padding:12px 20px;border-radius:8px;font-size:13px;z-index:9999;animation:fadeIn 0.3s;background:${type === 'error' ? 'rgba(239,83,80,0.95)' : type === 'warning' ? 'rgba(255,167,38,0.95)' : 'rgba(37,211,102,0.95)'};color:#000;font-weight:500;box-shadow:0 4px 16px rgba(0,0,0,0.5);max-width:400px`;
    div.textContent = message;
    document.body.appendChild(div);
    setTimeout(() => { div.style.opacity = '0'; div.style.transition = 'opacity 0.3s'; setTimeout(() => div.remove(), 300); }, 4000);
  },

  showAbout() {
    alert('BulkPing v1.0.0\nWhatsApp BSP Dashboard\nBuilt with ❤️');
  },

  bindEvents() {},

  /* ================================================================
     RENDER FUNCTIONS — each takes the container element
     ================================================================ */

  /* --- LOGIN --- */
  renderLogin() {
    const el = document.getElementById('shell-login');
    el.innerHTML = `
      <div class="login-card">
        <div class="login-logo">BP</div>
        <div class="login-title">BulkPing</div>
        <div class="login-subtitle">WhatsApp BSP Dashboard</div>
        <div id="g_id_onload" style="display:none"></div>
        <div class="google-btn-wrapper">
          <div id="g_id_button"></div>
        </div>
        <div class="login-divider"><span>or</span></div>
        <div class="tabs" id="login-tabs">
          <div class="tab active" data-tab="login">Login</div>
          <div class="tab" data-tab="signup">Sign Up</div>
        </div>
        <div id="auth-form-login">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input class="form-input" id="login-email" type="email" placeholder="you@example.com" autocomplete="email"/>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input class="form-input" id="login-pass" type="password" placeholder="••••••••" autocomplete="current-password"/>
          </div>
          <button class="btn btn-primary w-full btn-lg" id="login-btn">Sign In</button>
          <div id="login-error" class="hidden" style="color:var(--color-disconnected);font-size:13px;margin-top:12px"></div>
        </div>
        <div id="auth-form-signup" class="hidden">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input class="form-input" id="signup-email" type="email" placeholder="you@example.com" autocomplete="email"/>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input class="form-input" id="signup-pass" type="password" placeholder="••••••••" autocomplete="new-password"/>
          </div>
          <label class="form-checkbox" style="margin-bottom:16px">
            <input type="checkbox" id="signup-disclaimer"/>
            <span>I understand BulkPing uses an unofficial WhatsApp bridge (Baileys). This may violate Meta ToS. I accept full responsibility.</span>
          </label>
          <button class="btn btn-primary w-full btn-lg" id="signup-btn">Create Account</button>
          <div id="signup-error" class="hidden" style="color:var(--color-disconnected);font-size:13px;margin-top:12px"></div>
        </div>
      </div>
    `;
    document.getElementById('login-btn').onclick = () => this.login();
    document.getElementById('signup-btn').onclick = () => this.signup();
    document.getElementById('login-pass').onkeydown = e => { if (e.key === 'Enter') this.login(); };
    document.getElementById('signup-pass').onkeydown = e => { if (e.key === 'Enter') this.signup(); };
    document.querySelectorAll('#login-tabs .tab').forEach(t => {
      t.onclick = () => this.switchAuthTab(t.dataset.tab);
    });

    this.initGoogleSignIn();
  },

  async initGoogleSignIn() {
    if (typeof google === 'undefined' || !google.accounts) {
      setTimeout(() => this.initGoogleSignIn(), 500);
      return;
    }
    try {
      const cfg = await api.get('/api/auth/config/');
      const clientId = cfg.google_client_id;
      if (!clientId) return;
      google.accounts.id.initialize({
        client_id: clientId,
        callback: this.handleGoogleCredential.bind(this),
        cancel_on_tap_outside: false,
      });
      google.accounts.id.renderButton(
        document.getElementById('g_id_button'),
        { theme: 'outline', size: 'large', width: '100%', text: 'signin_with' }
      );
    } catch {}
  },

  handleGoogleCredential(response) {
    const btn = document.getElementById('g_id_button');
    if (btn) btn.style.pointerEvents = 'none';
    api.googleLogin(response.credential).then(() => {
      document.getElementById('shell-login').classList.add('hidden');
      location.hash = '#/dashboard';
    }).catch(err => {
      const el = document.getElementById('login-error');
      el.textContent = err.message;
      el.classList.remove('hidden');
    }).finally(() => {
      if (btn) btn.style.pointerEvents = '';
    });
  },

  switchAuthTab(tab) {
    document.querySelectorAll('#login-tabs .tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`#login-tabs .tab[data-tab="${tab}"]`).classList.add('active');
    document.getElementById('auth-form-login').classList.toggle('hidden', tab !== 'login');
    document.getElementById('auth-form-signup').classList.toggle('hidden', tab !== 'signup');
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('signup-error').classList.add('hidden');
  },

  async login() {
    const btn = document.getElementById('login-btn');
    btn.disabled = true; btn.textContent = 'Signing in...';
    document.getElementById('login-error').classList.add('hidden');
    try {
      await api.login(
        document.getElementById('login-email').value,
        document.getElementById('login-pass').value
      );
      document.getElementById('shell-login').classList.add('hidden');
      location.hash = '#/dashboard';
    } catch (err) {
      const el = document.getElementById('login-error');
      el.textContent = err.message;
      el.classList.remove('hidden');
    } finally { btn.disabled = false; btn.textContent = 'Sign In'; }
  },

  async signup() {
    const btn = document.getElementById('signup-btn');
    btn.disabled = true; btn.textContent = 'Creating...';
    document.getElementById('signup-error').classList.add('hidden');
    if (!document.getElementById('signup-disclaimer').checked) {
      document.getElementById('signup-error').textContent = 'You must accept the disclaimer.';
      document.getElementById('signup-error').classList.remove('hidden');
      btn.disabled = false; btn.textContent = 'Create Account';
      return;
    }
    try {
      await api.signup(
        document.getElementById('signup-email').value,
        document.getElementById('signup-pass').value,
        true
      );
      document.getElementById('shell-login').classList.add('hidden');
      location.hash = '#/dashboard';
    } catch (err) {
      const el = document.getElementById('signup-error');
      el.textContent = err.message;
      el.classList.remove('hidden');
    } finally { btn.disabled = false; btn.textContent = 'Create Account'; }
  },

  /* --- DASHBOARD --- */
  async render_dashboard(el) {
    try {
      const [instance, analytics] = await Promise.all([
        api.get('/api/instance/status/').catch(() => ({ status: '—', daily_sent_count: 0, daily_cap: 50 })),
        api.get('/api/campaigns/analytics/').catch(() => ({ total_campaigns: 0, total_recipients: 0, total_sent: 0, total_delivered: 0, total_read: 0, total_failed: 0, campaigns: [] })),
      ]);

      const status = instance.status || '—';
      const isConnected = status === 'connected';
      const sent = instance.daily_sent_count || 0;
      const cap = instance.daily_cap || 50;
      const capPct = Math.min(sent / Math.max(cap, 1) * 100, 100);
      const phone = instance.phone_number || '';

      el.innerHTML = `
        <div class="metrics-grid">
          <div class="metric-card">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
              <div class="metric-icon" style="background:${isConnected ? 'rgba(37,211,102,0.15)' : 'rgba(239,83,80,0.15)'}">
                <span style="font-size:20px">${isConnected ? '🟢' : '🔴'}</span>
              </div>
              <div>
                <div class="metric-label">Instance</div>
                <div style="font-size:13px;font-weight:600;color:var(--text-primary)">${isConnected ? 'Connected' : status}</div>
                ${phone ? `<div style="font-size:11px;color:var(--text-muted)">${phone}</div>` : ''}
              </div>
            </div>
          </div>
          <div class="metric-card">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
              <div class="metric-icon" style="background:rgba(66,165,245,0.15)">📊</div>
              <div>
                <div class="metric-label">Daily Sends</div>
                <div class="metric-value">${sent} <span style="font-size:14px;font-weight:400;color:var(--text-muted)">/ ${cap}</span></div>
              </div>
            </div>
            <div style="height:4px;background:var(--input-bg);border-radius:2px;overflow:hidden">
              <div style="height:100%;width:${capPct}%;background:var(--brand-accent);border-radius:2px;transition:width 0.5s"></div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Total Campaigns</div>
            <div class="metric-value">${analytics.total_campaigns || 0}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Total Recipients</div>
            <div class="metric-value">${analytics.total_recipients || 0}</div>
          </div>
        </div>

        <div class="metrics-grid" style="grid-template-columns:repeat(5,1fr)">
          <div class="metric-card"><div class="metric-label">Sent</div><div class="metric-value" style="color:var(--msg-sent)">${analytics.total_sent || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Delivered</div><div class="metric-value" style="color:var(--msg-delivered)">${analytics.total_delivered || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Read</div><div class="metric-value" style="color:var(--msg-read)">${analytics.total_read || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Failed</div><div class="metric-value" style="color:var(--msg-failed)">${analytics.total_failed || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Open Rate</div><div class="metric-value" style="color:var(--brand-accent)">${analytics.total_delivered ? Math.round(analytics.total_read / analytics.total_delivered * 100) : 0}%</div></div>
        </div>

        <div class="card" style="margin-top:24px">
          <div class="card-header"><span class="card-title">Recent Campaigns</span></div>
          ${analytics.campaigns?.length ? this.campaignTable(analytics.campaigns) : '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No campaigns yet</div><div class="empty-state-text">Create your first campaign to start sending messages.</div></div>'}
        </div>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  campaignTable(campaigns) {
    const rows = campaigns.slice(0, 10).map(c => `
      <tr>
        <td><a href="#" onclick="event.preventDefault();app.navigate('campaigns');return false" style="font-weight:500">${this.esc(c.name)}</a></td>
        <td><span class="badge badge-${c.status}"><span class="badge-dot" style="background:currentColor"></span>${c.status}</span></td>
        <td>${c.total_count || 0}</td>
        <td style="color:var(--msg-sent)">${c.sent_count || 0}</td>
        <td style="color:var(--msg-delivered)">${c.delivered_count || 0}</td>
        <td style="color:var(--msg-read)">${c.read_count || 0}</td>
        <td style="color:var(--msg-failed)">${c.failed_count || 0}</td>
        <td style="color:var(--brand-accent);font-weight:600">${c.open_rate ?? 0}%</td>
      </tr>
    `).join('');
    return `<div class="table-container"><table><thead><tr><th>Name</th><th>Status</th><th>Total</th><th>Sent</th><th>Delivered</th><th>Read</th><th>Failed</th><th>Rate</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  },

  /* --- CONNECT PAGE --- */
  async render_connect(el) {
    el.innerHTML = `
      <div style="display:flex;gap:24px;flex-wrap:wrap">
        <div style="flex:1;min-width:300px">
          <div class="card">
            <div class="card-header"><span class="card-title">WhatsApp Connection</span></div>
            <div id="connect-status" style="margin-bottom:16px">
              <div class="loading"><div class="spinner"></div> Checking status...</div>
            </div>
            <div id="connect-actions" style="display:flex;gap:8px">
              <button class="btn btn-primary" onclick="connectPage.showQR()">Show QR Code</button>
              <button class="btn btn-secondary" onclick="connectPage.refresh()">Refresh Status</button>
            </div>
          </div>
          <div id="connect-qr-section" class="card" style="margin-top:16px;display:none">
            <div class="card-header"><span class="card-title">Scan QR Code</span></div>
            <div id="connect-qr" class="qr-container">
              <div class="loading"><div class="spinner"></div> Generating QR...</div>
            </div>
            <p class="qr-hint">Open WhatsApp on your phone → Linked devices → Link a device → Scan this QR code</p>
          </div>
        </div>
        </div>
    `;
    await connectPage.refresh();
  },

  /* --- CAMPAIGNS PAGE --- */
  async render_campaigns(el) {
    el.innerHTML = `
      <div style="display:flex;gap:16px;margin-bottom:20px">
        <button class="btn btn-primary" onclick="campaigns.openNew()">+ New Campaign</button>
        <button class="btn btn-secondary" onclick="app.renderPage('campaigns')">Refresh</button>
      </div>
      <div class="tabs">
        <div class="tab active" data-tab="list" onclick="campaigns.switchTab('list')">All Campaigns</div>
        <div class="tab" data-tab="quick" onclick="campaigns.switchTab('quick')">Quick Send</div>
      </div>
      <div class="tab-content active" id="tab-list">
        <div id="campaigns-list"><div class="loading"><div class="spinner"></div></div></div>
      </div>
      <div class="tab-content" id="tab-quick">
        <div id="campaigns-quick"><div class="loading"><div class="spinner"></div></div></div>
      </div>
    `;
    await Promise.all([campaigns.renderList(), campaigns.renderQuick()]);
  },

  /* --- CONTACTS PAGE --- */
  async render_contacts(el) {
    el.innerHTML = `
      <div class="tabs">
        <div class="tab active" data-tab="contacts-tab" onclick="contacts.switchTab('contacts-tab')">Contacts</div>
        <div class="tab" data-tab="groups-tab" onclick="contacts.switchTab('groups-tab')">Groups</div>
      </div>
      <div class="tab-content active" id="tab-contacts-tab"><div id="contacts-list"><div class="loading"><div class="spinner"></div></div></div></div>
      <div class="tab-content" id="tab-groups-tab"><div id="groups-list"><div class="loading"><div class="spinner"></div></div></div></div>
    `;
    await Promise.all([contacts.renderContacts(), contacts.renderGroups()]);
  },

  /* --- ANALYTICS PAGE --- */
  async render_analytics(el) {
    el.innerHTML = '<div class="loading"><div class="spinner"></div> Loading analytics...</div>';
    try {
      const data = await api.get('/api/campaigns/analytics/');
      const campaigns = data.campaigns || [];
      el.innerHTML = `
        <div class="metrics-grid" style="grid-template-columns:repeat(4,1fr)">
          <div class="metric-card"><div class="metric-label">Campaigns</div><div class="metric-value">${data.total_campaigns || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Recipients</div><div class="metric-value">${data.total_recipients || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Sent</div><div class="metric-value" style="color:var(--msg-sent)">${data.total_sent || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Delivered</div><div class="metric-value" style="color:var(--msg-delivered)">${data.total_delivered || 0}</div></div>
        </div>
        <div class="metrics-grid" style="grid-template-columns:repeat(5,1fr);margin-bottom:24px">
          <div class="metric-card"><div class="metric-label">Read</div><div class="metric-value" style="color:var(--msg-read)">${data.total_read || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Failed</div><div class="metric-value" style="color:var(--msg-failed)">${data.total_failed || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Replied</div><div class="metric-value" style="color:#AB47BC">${data.total_replied || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Stopped</div><div class="metric-value" style="color:var(--text-muted)">${data.total_stopped || 0}</div></div>
          <div class="metric-card"><div class="metric-label">Open Rate</div><div class="metric-value" style="color:var(--brand-accent)">${data.total_delivered ? Math.round(data.total_read / data.total_delivered * 100) : 0}%</div></div>
        </div>
        <div class="card"><div class="card-header"><span class="card-title">Per-Campaign Analytics</span></div>
        ${campaigns.length ? `
          <div class="table-container">
            <table>
              <thead><tr><th>Campaign</th><th>Status</th><th>Total</th><th>Sent</th><th>Delivered</th><th>Read</th><th>Failed</th><th>Ignored</th><th>Replied</th><th>Rate</th><th></th></tr></thead>
              <tbody>${campaigns.map(c => `
                <tr>
                  <td style="font-weight:500">${this.esc(c.name)}</td>
                  <td><span class="badge badge-${c.stopped ? 'stopped' : c.status}">${c.stopped ? 'STOPPED' : c.status}</span></td>
                  <td>${c.total_count || 0}</td>
                  <td style="color:var(--msg-sent)">${c.sent_count || 0}</td>
                  <td style="color:var(--msg-delivered)">${c.delivered_count || 0}</td>
                  <td style="color:var(--msg-read)">${c.read_count || 0}</td>
                  <td style="color:var(--msg-failed)">${c.failed_count || 0}</td>
                  <td style="color:var(--text-muted)">${c.ignored_count ?? '-'}</td>
                  <td style="color:#AB47BC">${c.reply_count || 0}</td>
                  <td style="color:var(--brand-accent);font-weight:600">${c.open_rate ?? 0}%</td>
                  <td>${!c.stopped ? `<button class="btn btn-sm btn-danger" onclick="analytics.stopCampaign('${c.campaign_id}')">Stop</button>` : ''}</td>
                </tr>
              `).join('')}</tbody>
            </table>
          </div>
          <div style="margin-top:24px">
            <div id="analytics-funnel"><div class="loading"><div class="spinner"></div> Loading funnel...</div></div>
          </div>
        ` : '<div class="empty-state"><div class="empty-state-icon">📊</div><div class="empty-state-title">No data</div><div class="empty-state-text">Create campaigns to see analytics.</div></div>'}
        </div>
      `;
      if (campaigns.length) analytics.renderFunnel(data);
    } catch (err) { el.innerHTML = `<div class="alert alert-error">${err.message}</div>`; }
  },

  /* --- SETTINGS PAGE --- */
  async render_settings(el) {
    el.innerHTML = `
      <div class="card" style="max-width:600px">
        <div class="card-header"><span class="card-title">Settings</span></div>
        <div class="form-group">
          <label class="form-label">API Base URL</label>
          <input class="form-input" id="settings-api-url" value="${API_BASE || window.location.origin}" disabled />
        </div>
        <div class="form-group">
          <label class="form-label">Theme Config</label>
          <div style="font-size:13px;color:var(--text-secondary)">Edit <code>config/theme.json</code> to customize colors and layout.</div>
        </div>
        <hr style="border:none;border-top:1px solid var(--card-border);margin:16px 0">
        <button class="btn btn-danger" onclick="if(confirm('Logout?')){api.logout();location.hash='#/login'}">Logout</button>
      </div>
    `;
  },

  esc(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  },
};

/* ================================================================
   Page Controllers
   ================================================================ */

/* --- Connect Page --- */
const connectPage = {
  pollTimer: null,

  async refresh() {
    const el = document.getElementById('connect-status');
    if (!el) return;
    el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    try {
      const data = await api.get('/api/instance/status/');
      const connected = data.status === 'connected';
      const phone = data.phone_number || '';
      el.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;padding:12px 0">
          <span style="font-size:32px">${connected ? '🟢' : '🔴'}</span>
          <div>
            <div style="font-weight:600;font-size:17px">${connected ? 'Connected' : data.status || 'Disconnected'}</div>
            ${phone ? `<div style="font-size:13px;color:var(--text-muted)">${phone}</div>` : ''}
            ${data.daily_sent_count !== undefined ? `<div style="font-size:12px;color:var(--text-muted);margin-top:4px">Daily: ${data.daily_sent_count} / ${data.daily_cap || 50}</div>` : ''}
          </div>
        </div>
      `;
      if (connected) {
        if (this.pollTimer) { clearInterval(this.pollTimer); this.pollTimer = null; }
        document.getElementById('connect-qr-section').style.display = 'none';
      }
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  async showQR() {
    const section = document.getElementById('connect-qr-section');
    const qrEl = document.getElementById('connect-qr');
    section.style.display = '';
    qrEl.innerHTML = '<div class="loading"><div class="spinner"></div> Generating QR...</div>';
    try {
      const data = await api.post('/api/instance/create/');
      const qr = (data.qr_base64 || '').replace(/\s/g, '');
      if (qr) {
        qrEl.innerHTML = `<img src="data:image/png;base64,${qr}" class="qr-image" alt="QR Code" onerror="this.parentElement.innerHTML='<div class=alert-alert-warning>QR failed to load. Try again.</div>'"/>`;
        this.startPolling();
      } else {
        qrEl.innerHTML = '<div class="alert alert-warning">No QR returned. Try again.</div>';
      }
    } catch (err) {
      qrEl.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  startPolling() {
    if (this.pollTimer) clearInterval(this.pollTimer);
    this.pollTimer = setInterval(() => this.refresh(), 5000);
  },
};

/* --- Campaigns Page --- */
const campaigns = {
  switchTab(tab) {
    document.querySelectorAll('#page-campaigns .tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#page-campaigns .tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector(`#page-campaigns .tab[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById(`tab-${tab}`)?.classList.add('active');
  },

  async renderList() {
    const el = document.getElementById('campaigns-list');
    try {
      const campaigns = await api.get('/api/campaigns/');
      if (!campaigns.length) {
        el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-title">No campaigns</div><div class="empty-state-text">Create a campaign to start sending messages.</div></div>';
        return;
      }
      el.innerHTML = `
        <div class="table-container">
          <table>
            <thead><tr><th>Name</th><th>Status</th><th>Total</th><th>Sent</th><th>Delivered</th><th>Read</th><th>Failed</th><th>Rate</th><th></th></tr></thead>
            <tbody>${campaigns.map(c => `
              <tr>
                <td style="font-weight:500">${app.esc(c.name)}</td>
                <td><span class="badge badge-${c.status}">${c.status}</span></td>
                <td>${c.total_count || 0}</td>
                <td style="color:var(--msg-sent)">${c.sent_count || 0}</td>
                <td style="color:var(--msg-delivered)">${c.delivered_count || 0}</td>
                <td style="color:var(--msg-read)">${c.read_count || 0}</td>
                <td style="color:var(--msg-failed)">${c.failed_count || 0}</td>
                <td style="color:var(--brand-accent);font-weight:600">${c.open_rate ?? 0}%</td>
                <td><button class="btn btn-sm btn-secondary" onclick="campaigns.showDetail('${c.id}')">View</button></td>
              </tr>
            `).join('')}</tbody>
          </table>
        </div>
      `;
    } catch (err) { el.innerHTML = `<div class="alert alert-error">${err.message}</div>`; }
  },

  async renderQuick() {
    const el = document.getElementById('campaigns-quick');
    try {
      const contacts = await api.get('/api/contacts/');
      el.innerHTML = `
        <div class="card" style="max-width:500px">
          <div class="card-header"><span class="card-title">Quick Send</span></div>
          <div class="form-group">
            <label class="form-label">Contact</label>
            <select class="form-select" id="qs-contact">
              <option value="">Select a contact...</option>
              ${contacts.map(c => `<option value="${c.id}" data-phone="${c.phone}">${app.esc(c.name)} — ${c.phone}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Message</label>
            <textarea class="form-textarea" id="qs-message" placeholder="Type your message..."></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Media URL (optional)</label>
            <input class="form-input" id="qs-media" placeholder="https://example.com/image.jpg" />
          </div>
          <button class="btn btn-primary" onclick="campaigns.sendQuick()">Send Message</button>
        </div>
      `;
    } catch (err) { el.innerHTML = `<div class="alert alert-error">${err.message}</div>`; }
  },

  async sendQuick() {
    const sel = document.getElementById('qs-contact');
    const contactId = sel.value;
    if (!contactId) { app.toast('Select a contact', 'warning'); return; }
    const msg = document.getElementById('qs-message').value.trim();
    if (!msg) { app.toast('Enter a message', 'warning'); return; }
    const opt = sel.options[sel.selectedIndex];
    const name = opt.text.split(' — ')[0];
    const phone = opt.dataset.phone;
    const media = document.getElementById('qs-media').value.trim();
    try {
      await api.post('/api/campaigns/quick-send/', { name, phone, message_text: msg, ...(media ? { media_url: media } : {}) });
      app.toast('Message sent!');
      document.getElementById('qs-message').value = '';
    } catch (err) { app.toast(err.message, 'error'); }
  },

  async showDetail(id) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal-body');
    overlay.classList.add('open');
    modal.innerHTML = '<div class="loading"><div class="spinner"></div> Loading...</div>';
    try {
      const stats = await api.get(`/api/campaigns/${id}/stats/`);
      const byStatus = stats.by_status || {};
      const statusOrder = ['failed', 'pending', 'sent', 'delivered', 'read'];
      modal.innerHTML = `
        <div style="margin-bottom:16px">
          <div style="font-size:20px;font-weight:700;color:var(--text-primary)">${app.esc(stats.name)}</div>
          <div style="font-size:13px;color:var(--text-muted);margin-top:4px">ID: ${id}</div>
        </div>
        <div class="grid-4" style="margin-bottom:16px">
          <div><div class="text-sm text-secondary">Status</div><div style="font-weight:600">${stats.status}</div></div>
          <div><div class="text-sm text-secondary">Total</div><div style="font-weight:600">${stats.total_count || 0}</div></div>
          <div><div class="text-sm text-secondary">Sent</div><div style="font-weight:600;color:var(--msg-sent)">${stats.sent_count || 0}</div></div>
          <div><div class="text-sm text-secondary">Delivered</div><div style="font-weight:600;color:var(--msg-delivered)">${stats.delivered_count || 0}</div></div>
          <div><div class="text-sm text-secondary">Read</div><div style="font-weight:600;color:var(--msg-read)">${stats.read_count || 0}</div></div>
          <div><div class="text-sm text-secondary">Failed</div><div style="font-weight:600;color:var(--msg-failed)">${stats.failed_count || 0}</div></div>
          <div><div class="text-sm text-secondary">Open Rate</div><div style="font-weight:600;color:var(--brand-accent)">${stats.open_rate ?? 0}%</div></div>
          <div><div class="text-sm text-secondary">Replied</div><div style="font-weight:600;color:#AB47BC">${stats.reply_count || 0}</div></div>
        </div>
        <hr style="border:none;border-top:1px solid var(--card-border);margin:12px 0">
        <div style="font-weight:600;margin-bottom:8px">Per-Contact Status</div>
        ${statusOrder.map(s => {
          const items = byStatus[s] || [];
          return items.length ? `
            <div class="expander open">
              <div class="expander-header" onclick="this.parentElement.classList.toggle('open')">
                <span class="expander-arrow">▶</span>
                <span>${s.charAt(0).toUpperCase() + s.slice(1)} <span style="color:var(--text-muted);font-weight:400">(${items.length})</span></span>
              </div>
              <div class="expander-body">${items.map(item => `<div class="expander-item"><span>${app.esc(item.contact_name)} — ${item.contact_phone}</span><span style="color:var(--text-muted);font-size:11px">${item.status_updated_at || ''}</span></div>`).join('')}</div>
            </div>
          ` : '';
        }).join('')}
        ${!stats.stopped ? `<div style="margin-top:12px"><button class="btn btn-sm btn-danger" onclick="analytics.stopCampaign('${id}')">Stop Campaign</button></div>` : ''}
      `;
    } catch (err) { modal.innerHTML = `<div class="alert alert-error">${err.message}</div>`; }
  },

  openNew() {
    this.switchTab('list');
    const el = document.getElementById('campaigns-list');
    const html = el.innerHTML;
    el.innerHTML = `
      <div class="card" style="max-width:500px;margin-bottom:16px" id="new-campaign-form">
        <div class="card-header"><span class="card-title">New Campaign</span></div>
        <div class="form-group">
          <label class="form-label">Campaign Name</label>
          <input class="form-input" id="nc-name" placeholder="e.g., Welcome Offer" />
        </div>
        <div class="form-group">
          <label class="form-label">Message</label>
          <textarea class="form-textarea" id="nc-msg" placeholder="Type your broadcast message..."></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Target Group</label>
          <select class="form-select" id="nc-group"><option>Loading groups...</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">Media URL (optional)</label>
          <input class="form-input" id="nc-media" placeholder="https://example.com/image.jpg" />
        </div>
        <button class="btn btn-primary" onclick="campaigns.create()">Send Broadcast</button>
        <button class="btn btn-secondary" style="margin-left:8px" onclick="campaigns.cancelNew()">Cancel</button>
      </div>
    `;
    api.get('/api/groups/').then(groups => {
      const sel = document.getElementById('nc-group');
      sel.innerHTML = groups.map(g => `<option value="${g.id}">${app.esc(g.name)} (${g.member_count || 0} members)</option>`).join('');
    }).catch(() => {
      document.getElementById('nc-group').innerHTML = '<option>No groups available</option>';
    });
  },

  cancelNew() {
    app.renderPage('campaigns');
  },

  async create() {
    const name = document.getElementById('nc-name').value.trim();
    const msg = document.getElementById('nc-msg').value.trim();
    const groupId = document.getElementById('nc-group').value;
    const media = document.getElementById('nc-media').value.trim();
    if (!name) { app.toast('Enter a campaign name', 'warning'); return; }
    if (!msg) { app.toast('Enter a message', 'warning'); return; }
    try {
      await api.post('/api/campaigns/', { name, message_text: msg, group_id: groupId, ...(media ? { media_url: media } : {}) });
      app.toast('Campaign created!');
      app.renderPage('campaigns');
    } catch (err) { app.toast(err.message, 'error'); }
  },
};

/* --- Contacts Page --- */
const contacts = {
  switchTab(tab) {
    document.querySelectorAll('#page-contacts .tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#page-contacts .tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector(`#page-contacts .tab[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById(`tab-${tab}`)?.classList.add('active');
  },

  async renderContacts() {
    const el = document.getElementById('contacts-list');
    try {
      const list = await api.get('/api/contacts/');
      el.innerHTML = `
        <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px">
          <div class="card" style="flex:1;min-width:280px">
            <div class="card-header"><span class="card-title">Add Contact</span></div>
            <div class="form-row">
              <div class="form-group"><input class="form-input" id="add-c-name" placeholder="Name" /></div>
              <div class="form-group"><input class="form-input" id="add-c-phone" placeholder="Phone (+91...)" /></div>
            </div>
            <button class="btn btn-primary btn-sm" onclick="contacts.add()">Add Contact</button>
          </div>
          <div class="card" style="flex:1;min-width:280px">
            <div class="card-header"><span class="card-title">Import CSV</span></div>
            <div class="form-group">
              <input type="file" class="form-input" id="csv-file" accept=".csv" />
              <div style="font-size:11px;color:var(--text-muted);margin-top:4px">Columns: name, phone</div>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="contacts.importCSV()">Import</button>
          </div>
        </div>
        <div class="card">
          <div class="card-header"><span class="card-title">All Contacts</span></div>
          ${list.length ? `
            <div class="table-container">
              <table>
                <thead><tr><th>Name</th><th>Phone</th><th></th></tr></thead>
                <tbody>${list.map(c => `
                  <tr>
                    <td style="font-weight:500">${app.esc(c.name)}</td>
                    <td style="color:var(--text-secondary)">${c.phone}</td>
                    <td><button class="btn btn-sm btn-danger" onclick="contacts.delete('${c.id}')">Delete</button></td>
                  </tr>
                `).join('')}</tbody>
              </table>
            </div>
          ` : '<div class="empty-state"><div class="empty-state-title">No contacts</div><div class="empty-state-text">Add contacts manually or import a CSV.</div></div>'}
        </div>
      `;
    } catch (err) { el.innerHTML = `<div class="alert alert-error">${err.message}</div>`; }
  },

  async renderGroups() {
    const el = document.getElementById('groups-list');
    try {
      const [groups, contacts] = await Promise.all([api.get('/api/groups/'), api.get('/api/contacts/')]);
      el.innerHTML = `
        <div class="card" style="margin-bottom:16px;max-width:400px">
          <div class="card-header"><span class="card-title">Create Group</span></div>
          <div class="form-group"><input class="form-input" id="add-g-name" placeholder="Group name" /></div>
          <button class="btn btn-primary btn-sm" onclick="contacts.createGroup()">Create Group</button>
        </div>
        ${groups.map(g => `
          <div class="expander open">
            <div class="expander-header" onclick="this.parentElement.classList.toggle('open')">
              <span class="expander-arrow">▶</span>
              <span>${app.esc(g.name)} <span style="color:var(--text-muted);font-weight:400">(${g.member_count || 0} members)</span></span>
            </div>
            <div class="expander-body" id="group-body-${g.id}">
              <div class="loading"><div class="spinner"></div></div>
            </div>
          </div>
        `).join('')}
      `;
      groups.forEach(g => contacts.loadGroup(g.id));
    } catch (err) { el.innerHTML = `<div class="alert alert-error">${err.message}</div>`; }
  },

  async loadGroup(groupId) {
    const body = document.getElementById(`group-body-${groupId}`);
    try {
      const [members, allContacts] = await Promise.all([api.get(`/api/groups/${groupId}/members/`), api.get('/api/contacts/')]);
      const memberIds = new Set(members.map(m => m.id));
      const available = allContacts.filter(c => !memberIds.has(c.id));
      body.innerHTML = `
        ${members.length ? members.map(m => `
          <div class="expander-item">
            <span>${app.esc(m.name)} — ${m.phone}</span>
            <button class="btn btn-sm btn-danger" onclick="contacts.removeMember('${groupId}','${m.id}')">Remove</button>
          </div>
        `).join('') : '<div style="padding:8px;color:var(--text-muted);font-size:13px">No members</div>'}
        <hr style="border:none;border-top:1px solid var(--card-border);margin:8px 0">
        ${available.length ? `
          <div style="display:flex;gap:8px;padding:4px 0">
            <select class="form-select" id="add-member-sel-${groupId}" style="flex:1">
              ${available.map(c => `<option value="${c.id}">${app.esc(c.name)} — ${c.phone}</option>`).join('')}
            </select>
            <button class="btn btn-sm btn-primary" onclick="contacts.addMember('${groupId}')">Add</button>
          </div>
        ` : '<div style="font-size:13px;color:var(--text-muted);padding:4px 0">All contacts already in this group.</div>'}
      `;
    } catch { body.innerHTML = '<div class="alert alert-error">Failed to load</div>'; }
  },

  async add() {
    const name = document.getElementById('add-c-name').value.trim();
    const phone = document.getElementById('add-c-phone').value.trim();
    if (!name || !phone) { app.toast('Enter name and phone', 'warning'); return; }
    try {
      await api.post('/api/contacts/', { name, phone });
      app.toast('Contact added');
      document.getElementById('add-c-name').value = '';
      document.getElementById('add-c-phone').value = '';
      contacts.renderContacts();
    } catch (err) { app.toast(err.message, 'error'); }
  },

  async delete(id) {
    if (!confirm('Delete this contact?')) return;
    try { await api.delete(`/api/contacts/${id}/`); contacts.renderContacts(); app.toast('Deleted'); }
    catch (err) { app.toast(err.message, 'error'); }
  },

  async createGroup() {
    const name = document.getElementById('add-g-name').value.trim();
    if (!name) { app.toast('Enter a group name', 'warning'); return; }
    try { await api.post('/api/groups/', { name }); document.getElementById('add-g-name').value = ''; contacts.renderGroups(); app.toast('Group created'); }
    catch (err) { app.toast(err.message, 'error'); }
  },

  async addMember(groupId) {
    const sel = document.getElementById(`add-member-sel-${groupId}`);
    if (!sel) return;
    try { await api.post(`/api/groups/${groupId}/members/`, { contact_ids: [sel.value] }); contacts.loadGroup(groupId); app.toast('Member added'); }
    catch (err) { app.toast(err.message, 'error'); }
  },

  async removeMember(groupId, contactId) {
    try { await api.delete(`/api/groups/${groupId}/members/`, { contact_ids: [contactId] }); contacts.loadGroup(groupId); app.toast('Member removed'); }
    catch (err) { app.toast(err.message, 'error'); }
  },

  async importCSV() {
    const fileInput = document.getElementById('csv-file');
    if (!fileInput.files.length) { app.toast('Select a CSV file', 'warning'); return; }
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    try {
      const resp = await fetch(`${API_BASE}/api/contacts/import/`, { method: 'POST', headers: { 'Authorization': `Bearer ${api.token}` }, body: formData });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      app.toast(`Imported ${data.imported || 0} / ${data.total || 0} contacts`);
      contacts.renderContacts();
    } catch (err) { app.toast(err.message, 'error'); }
  },
};

/* --- Analytics Page --- */
const analytics = {
  async stopCampaign(id) {
    if (!confirm('Stop this campaign? This cannot be undone.')) return;
    try { await api.post(`/api/campaigns/${id}/stop/`); app.toast('Campaign stopped'); app.renderPage('analytics'); }
    catch (err) { app.toast(err.message, 'error'); }
  },

  renderFunnel(data) {
    const el = document.getElementById('analytics-funnel');
    const campaigns = data.campaigns || [];
    if (!campaigns.length) { el.innerHTML = ''; return; }
    const total = c => [c.sent_count || 0, c.delivered_count || 0, c.read_count || 0, c.failed_count || 0];
    const maxVal = Math.max(...campaigns.flatMap(total), 1);
    const names = campaigns.map(c => app.esc(c.name));
    const selectOpts = campaigns.map((c, i) => `<option value="${i}">${app.esc(c.name)}</option>`).join('');
    el.innerHTML = `
      <div class="card-header" style="margin-bottom:12px"><span class="card-title">Delivery Funnel</span>
        <select class="form-select" id="funnel-select" style="width:auto" onchange="analytics.updateFunnel(${JSON.stringify(campaigns).replace(/"/g, "'")})">
          ${selectOpts}
        </select>
      </div>
      <div id="funnel-chart"></div>
    `;
    this.updateFunnel(campaigns);
  },

  updateFunnel(campaigns) {
    const idx = parseInt(document.getElementById('funnel-select')?.value || '0');
    const c = campaigns[idx];
    if (!c) return;
    const chart = document.getElementById('funnel-chart');
    const items = [
      { label: 'Sent', count: c.sent_count || 0, color: 'var(--msg-sent)' },
      { label: 'Delivered', count: c.delivered_count || 0, color: 'var(--msg-delivered)' },
      { label: 'Read', count: c.read_count || 0, color: 'var(--msg-read)' },
      { label: 'Failed', count: c.failed_count || 0, color: 'var(--msg-failed)' },
    ];
    const maxVal = Math.max(...items.map(i => i.count), 1);
    chart.innerHTML = '<div class="funnel">' + items.map(i => `
      <div class="funnel-row">
        <div class="funnel-label">${i.label}</div>
        <div class="funnel-bar-wrapper">
          <div class="funnel-bar" style="width:${i.count / maxVal * 100}%;background:${i.color};min-width:${i.count ? '60px' : '0'}">
            <span class="funnel-count">${i.count}</span>
          </div>
        </div>
        <div class="funnel-pct">${i.count ? Math.round(i.count / (c.total_count || 1) * 100) : 0}%</div>
      </div>
    `).join('') + '</div>';
  },
};

/* --- Boot --- */
document.addEventListener('DOMContentLoaded', () => app.init());
