/* ================================================================
   BulkPing API Client
   ================================================================ */

const API_BASE = (window.API_BASE_URL || '').replace(/\/+$/, '') || '';

const api = {
  token: null,
  refreshToken: null,

  init() {
    this.token = localStorage.getItem('bp_token');
    this.refreshToken = localStorage.getItem('bp_refresh');
  },

  isLoggedIn() {
    return !!this.token;
  },

  logout() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('bp_token');
    localStorage.removeItem('bp_refresh');
    location.hash = '#/login';
  },

  async _fetch(method, path, body) {
    const url = `${API_BASE}${path}`;
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

    const opts = { method, headers };
    if (body && method !== 'GET') opts.body = JSON.stringify(body);

    try {
      let resp = await fetch(url, opts);
      if (resp.status === 401 && this.refreshToken) {
        const refreshed = await this._refresh();
        if (refreshed) {
          headers['Authorization'] = `Bearer ${this.token}`;
          resp = await fetch(url, { ...opts, headers });
        } else {
          this.logout();
          throw new Error('Session expired. Please login again.');
        }
      }
      if (!resp.ok) {
        let errMsg = `HTTP ${resp.status}`;
        try {
          const errData = await resp.json();
          errMsg = errData.detail || errData.error || errData.message || JSON.stringify(Object.values(errData).flat().join(' ')) || errMsg;
        } catch {}
        throw new Error(errMsg);
      }
      const text = await resp.text();
      return text ? JSON.parse(text) : {};
    } catch (err) {
      if (err.message === 'Failed to fetch') throw new Error('Network error — is the server running?');
      throw err;
    }
  },

  async _refresh() {
    try {
      const resp = await fetch(`${API_BASE}/api/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });
      if (!resp.ok) return false;
      const data = await resp.json();
      this.token = data.access;
      localStorage.setItem('bp_token', data.access);
      return true;
    } catch { return false; }
  },

  get(path) { return this._fetch('GET', path); },
  post(path, data) { return this._fetch('POST', path, data); },
  patch(path, data) { return this._fetch('PATCH', path, data); },
  delete(path, data) { return this._fetch('DELETE', path, data); },

  /* --- Auth --- */
  async login(email, password) {
    const data = await this.post('/api/auth/login/', { email, password });
    this.token = data.access;
    this.refreshToken = data.refresh;
    localStorage.setItem('bp_token', data.access);
    localStorage.setItem('bp_refresh', data.refresh);
    return data;
  },

  async signup(email, password, disclaimer_accepted) {
    const data = await this.post('/api/auth/signup/', { email, password, disclaimer_accepted });
    this.token = data.access;
    this.refreshToken = data.refresh;
    localStorage.setItem('bp_token', data.access);
    localStorage.setItem('bp_refresh', data.refresh);
    return data;
  },

  async googleLogin(credential) {
    const data = await this.post('/api/auth/google/', { credential });
    this.token = data.access;
    this.refreshToken = data.refresh;
    localStorage.setItem('bp_token', data.access);
    localStorage.setItem('bp_refresh', data.refresh);
    return data;
  },

  async clerkLogin(token) {
    const data = await this.post('/api/auth/clerk/', { token });
    this.token = data.access;
    this.refreshToken = data.refresh;
    localStorage.setItem('bp_token', data.access);
    localStorage.setItem('bp_refresh', data.refresh);
    return data;
  },
};
