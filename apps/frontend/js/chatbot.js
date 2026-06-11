/* ================================================================
   BulkPing — Chatbot Page Controller
   ================================================================ */

const chatbot = {
  currentTab: 'flows',

  async render(el) {
    el.innerHTML = `
      <div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap">
        <button class="btn btn-primary" onclick="chatbot.newFlow()">+ New Flow</button>
        <button class="btn btn-secondary" onclick="chatbot.render(chatbot._container)">Refresh</button>
      </div>
      <div class="tabs">
        <div class="tab active" data-tab="flows" onclick="chatbot.switchTab('flows')">Flows</div>
        <div class="tab" data-tab="rules" onclick="chatbot.switchTab('rules')">Rules</div>
        <div class="tab" data-tab="sessions" onclick="chatbot.switchTab('sessions')">Sessions</div>
        <div class="tab" data-tab="logs" onclick="chatbot.switchTab('logs')">Match Logs</div>
      </div>
      <div class="tab-content active" id="tab-chatbot-flows"></div>
      <div class="tab-content" id="tab-chatbot-rules"></div>
      <div class="tab-content" id="tab-chatbot-sessions"></div>
      <div class="tab-content" id="tab-chatbot-logs"></div>
    `;
    this._container = el;
    await Promise.all([
      this.renderFlows(),
      this.renderRules(),
      this.renderSessions(),
      this.renderLogs(),
    ]);
  },

  switchTab(tab) {
    this.currentTab = tab;
    const parent = document.getElementById('page-chatbot');
    parent.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    parent.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    parent.querySelector(`.tab[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById(`tab-chatbot-${tab}`)?.classList.add('active');
  },

  /* ================================================================
     FLOWS
     ================================================================ */

  async renderFlows() {
    const el = document.getElementById('tab-chatbot-flows');
    el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    try {
      const flows = await api.get('/api/chatbot/flows/');
      el.innerHTML = `
        <div class="card">
          <div class="table-container">
            <table>
              <thead><tr>
                <th>Name</th>
                <th>Active</th>
                <th>Welcome Message</th>
                <th>Created</th>
                <th></th>
              </tr></thead>
              <tbody>
                ${flows.length ? flows.map(f => `
                  <tr>
                    <td style="font-weight:500">${app.esc(f.name)}</td>
                    <td><span class="badge ${f.is_active ? 'badge-connected' : 'badge-disconnected'}">${f.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td style="color:var(--text-secondary);max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${app.esc(f.welcome_message || '—')}</td>
                    <td style="color:var(--text-muted);font-size:11px">${new Date(f.created_at).toLocaleDateString()}</td>
                    <td>
                      <button class="btn btn-sm btn-secondary" onclick="chatbot.editFlow('${f.id}')">Edit</button>
                      <button class="btn btn-sm btn-danger" onclick="chatbot.deleteFlow('${f.id}')">Delete</button>
                    </td>
                  </tr>
                `).join('') : `
                  <tr><td colspan="5"><div class="empty-state"><div class="empty-state-icon">🗂️</div><div class="empty-state-title">No flows yet</div><div class="empty-state-text">Create a flow to organize your chatbot rules.</div></div></td></tr>
                `}
              </tbody>
            </table>
          </div>
        </div>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  async newFlow() {
    this._showFlowModal(null);
  },

  async editFlow(id) {
    this._showFlowModal(id);
  },

  async deleteFlow(id) {
    if (!confirm('Delete this flow and all its rules?')) return;
    try {
      await api.delete(`/api/chatbot/flows/${id}/`);
      app.toast('Flow deleted');
      this.renderFlows();
    } catch (err) {
      app.toast(err.message, 'error');
    }
  },

  async _showFlowModal(flowId) {
    let flow = {};
    if (flowId) {
      try {
        flow = await api.get(`/api/chatbot/flows/${flowId}/`);
      } catch { return; }
    }
    const isEdit = !!flowId;
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal-body');
    overlay.classList.add('open');
    document.getElementById('modal-title').textContent = isEdit ? 'Edit Flow' : 'New Flow';
    modal.innerHTML = `
      <div class="form-group">
        <label class="form-label">Flow Name</label>
        <input class="form-input" id="f-name" value="${app.esc(flow.name || '')}" placeholder="e.g., Customer Support" />
      </div>
      <div class="form-group">
        <label class="form-label">Welcome Message</label>
        <textarea class="form-textarea" id="f-welcome" placeholder="Optional welcome message when flow starts" style="min-height:60px">${app.esc(flow.welcome_message || '')}</textarea>
      </div>
      <div class="form-group">
        <label class="form-checkbox">
          <input type="checkbox" id="f-active" ${(!flowId || flow.is_active) ? 'checked' : ''} />
          <span>Active</span>
        </label>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="document.getElementById('modal-overlay').classList.remove('open')">Cancel</button>
        <button class="btn btn-primary" onclick="chatbot._saveFlow('${flowId || ''}')">${isEdit ? 'Update' : 'Create'} Flow</button>
      </div>
    `;
  },

  async _saveFlow(flowId) {
    const payload = {
      name: document.getElementById('f-name').value.trim(),
      welcome_message: document.getElementById('f-welcome').value.trim(),
      is_active: document.getElementById('f-active').checked,
    };
    if (!payload.name) { app.toast('Enter a flow name', 'warning'); return; }
    try {
      if (flowId) {
        await api.patch(`/api/chatbot/flows/${flowId}/`, payload);
      } else {
        await api.post('/api/chatbot/flows/', payload);
      }
      app.toast(flowId ? 'Flow updated' : 'Flow created');
      document.getElementById('modal-overlay').classList.remove('open');
      this.renderFlows();
    } catch (err) {
      app.toast(err.message, 'error');
    }
  },

  /* ================================================================
     RULES
     ================================================================ */

  _rulesCache: [],

  async renderRules() {
    const el = document.getElementById('tab-chatbot-rules');
    el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    try {
      const [rules, flows] = await Promise.all([
        api.get('/api/chatbot/rules/'),
        api.get('/api/chatbot/flows/'),
      ]);
      this._rulesCache = rules;
      el.innerHTML = `
        <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;align-items:center">
          <button class="btn btn-primary btn-sm" onclick="chatbot.newRule()">+ New Rule</button>
          <select class="form-select" id="rule-flow-filter" style="width:auto;min-width:180px" onchange="chatbot.filterRules()">
            <option value="">All Flows</option>
            ${flows.map(f => `<option value="${f.id}">${app.esc(f.name)}</option>`).join('')}
          </select>
          <select class="form-select" id="rule-match-filter" style="width:auto;min-width:140px" onchange="chatbot.filterRules()">
            <option value="">All Match Types</option>
            <option value="keyword_contains">Keyword Contains</option>
            <option value="keyword_exact">Keyword Exact</option>
            <option value="keyword_regex">Keyword Regex</option>
            <option value="button_id">Button ID</option>
            <option value="list_selection">List Selection</option>
            <option value="always">Always</option>
          </select>
        </div>
        <div id="rules-table-wrapper">
          ${this._rulesTable(rules)}
        </div>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  filterRules() {
    const flowFilter = document.getElementById('rule-flow-filter').value;
    const matchFilter = document.getElementById('rule-match-filter').value;
    let filtered = this._rulesCache;
    if (flowFilter) filtered = filtered.filter(r => r.flow === flowFilter);
    if (matchFilter) filtered = filtered.filter(r => r.match_type === matchFilter);
    document.getElementById('rules-table-wrapper').innerHTML = this._rulesTable(filtered);
  },

  _rulesTable(rules) {
    if (!rules.length) {
      return '<div class="empty-state"><div class="empty-state-icon">📋</div><div class="empty-state-title">No rules</div><div class="empty-state-text">Create a rule to start building your chatbot.</div></div>';
    }
    return `
      <div class="table-container">
        <table>
          <thead><tr>
            <th>Flow</th>
            <th>Match Type</th>
            <th>Keyword / Trigger</th>
            <th>Response Type</th>
            <th>Active</th>
            <th>Priority</th>
            <th>Fallback</th>
            <th></th>
          </tr></thead>
          <tbody>
            ${rules.map(r => `
              <tr>
                <td style="color:var(--text-secondary);font-size:12px">${r.flow ? r.flow.substring(0, 8) + '...' : '—'}</td>
                <td><span class="badge badge-${r.match_type === 'always' ? 'qr' : r.match_type === 'keyword_contains' ? 'sent' : r.match_type === 'button_id' ? 'delivered' : 'pending'}">${r.match_type.replace(/_/g, ' ')}</span></td>
                <td style="font-weight:500;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${app.esc(r.keyword || (r.is_fallback ? '(fallback)' : '—'))}</td>
                <td><span class="badge badge-${r.response_type === 'text' ? 'sent' : r.response_type === 'list_menu' ? 'delivered' : r.response_type === 'buttons' ? 'read' : 'pending'}">${r.response_type.replace(/_/g, ' ')}</span></td>
                <td><label class="form-checkbox" style="justify-content:center"><input type="checkbox" ${r.is_active ? 'checked' : ''} onchange="chatbot.toggleRule('${r.id}', this.checked)" /></label></td>
                <td>${r.priority}</td>
                <td>${r.is_fallback ? '<span class="badge badge-warning">Fallback</span>' : '—'}</td>
                <td>
                  <button class="btn btn-sm btn-secondary" onclick="chatbot.editRule('${r.id}')">Edit</button>
                  <button class="btn btn-sm btn-danger" onclick="chatbot.deleteRule('${r.id}')">Delete</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  },

  async toggleRule(id, active) {
    try {
      await api.patch(`/api/chatbot/rules/${id}/`, { is_active: active });
    } catch (err) {
      app.toast(err.message, 'error');
      this.renderRules();
    }
  },

  async deleteRule(id) {
    if (!confirm('Delete this rule?')) return;
    try {
      await api.delete(`/api/chatbot/rules/${id}/`);
      app.toast('Rule deleted');
      this.renderRules();
    } catch (err) {
      app.toast(err.message, 'error');
    }
  },

  async newRule() {
    this._showRuleModal(null);
  },

  async editRule(id) {
    this._showRuleModal(id);
  },

  async _showRuleModal(ruleId) {
    let rule = {
      match_type: 'keyword_contains',
      response_type: 'text',
      is_active: true,
      is_fallback: false,
      priority: 0,
      cooldown_seconds: 0,
      keyword: '',
      reply_text: '',
      menu_config: null,
      attachment_url: '',
      flow: null,
    };
    let branches = [];
    if (ruleId) {
      try {
        rule = await api.get(`/api/chatbot/rules/${ruleId}/`);
        branches = rule.branches || [];
      } catch { return; }
    }

    const flows = await api.get('/api/chatbot/flows/').catch(() => []);

    const isEdit = !!ruleId;
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal-body');
    overlay.classList.add('open');
    document.getElementById('modal-title').textContent = isEdit ? 'Edit Rule' : 'New Rule';

    const menuConfigJson = rule.menu_config ? JSON.stringify(rule.menu_config, null, 2) : '';

    modal.innerHTML = `
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Flow</label>
          <select class="form-select" id="r-flow">
            <option value="">No flow (standalone)</option>
            ${flows.map(f => `<option value="${f.id}" ${rule.flow === f.id ? 'selected' : ''}>${app.esc(f.name)}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Match Type</label>
          <select class="form-select" id="r-match-type" onchange="chatbot._toggleMatchFields()">
            <option value="keyword_contains" ${rule.match_type === 'keyword_contains' ? 'selected' : ''}>Keyword Contains</option>
            <option value="keyword_exact" ${rule.match_type === 'keyword_exact' ? 'selected' : ''}>Keyword Exact</option>
            <option value="keyword_regex" ${rule.match_type === 'keyword_regex' ? 'selected' : ''}>Keyword Regex</option>
            <option value="button_id" ${rule.match_type === 'button_id' ? 'selected' : ''}>Button ID</option>
            <option value="list_selection" ${rule.match_type === 'list_selection' ? 'selected' : ''}>List Selection</option>
            <option value="always" ${rule.match_type === 'always' ? 'selected' : ''}>Always</option>
          </select>
        </div>
      </div>

      <div class="form-group" id="r-keyword-group">
        <label class="form-label">Keyword / Trigger Value</label>
        <input class="form-input" id="r-keyword" value="${app.esc(rule.keyword || '')}" placeholder='e.g., "hello", "yes", "opt_1"' />
      </div>

      <div class="form-group">
        <label class="form-label">Response Type</label>
        <select class="form-select" id="r-response-type" onchange="chatbot._toggleResponseFields()">
          <option value="text" ${rule.response_type === 'text' ? 'selected' : ''}>Text</option>
          <option value="list_menu" ${rule.response_type === 'list_menu' ? 'selected' : ''}>List Menu (Dropdown)</option>
          <option value="buttons" ${rule.response_type === 'buttons' ? 'selected' : ''}>Buttons</option>
          <option value="image" ${rule.response_type === 'image' ? 'selected' : ''}>Image</option>
          <option value="document" ${rule.response_type === 'document' ? 'selected' : ''}>Document</option>
          <option value="audio" ${rule.response_type === 'audio' ? 'selected' : ''}>Audio</option>
          <option value="video" ${rule.response_type === 'video' ? 'selected' : ''}>Video</option>
        </select>
      </div>

      <div class="form-group" id="r-reply-group">
        <label class="form-label">Reply Text</label>
        <textarea class="form-textarea" id="r-reply" style="min-height:60px" placeholder="Reply message text">${app.esc(rule.reply_text || '')}</textarea>
      </div>

      <div class="form-group" id="r-menu-group" style="display:${rule.response_type === 'list_menu' || rule.response_type === 'buttons' ? 'block' : 'none'}">
        <label class="form-label">Menu / Button Configuration (JSON)</label>
        <textarea class="form-textarea" id="r-menu-config" style="min-height:120px;font-family:monospace;font-size:12px" placeholder='${rule.response_type === 'list_menu' ? '{\n  "title": "Choose",\n  "description": "Select an option",\n  "button_text": "Tap",\n  "sections": [\n    {\n      "title": "Menu",\n      "rows": [\n        {"title": "Option 1", "description": "Desc", "row_id": "opt_1"}\n      ]\n    }\n  ]\n}' : '{\n  "title": "Confirm",\n  "description": "Pick one",\n  "buttons": [\n    {"type": "reply", "text": "Yes", "id": "yes"},\n    {"type": "reply", "text": "No", "id": "no"}\n  ]\n}'}>${menuConfigJson}</textarea>
        <div style="font-size:11px;color:var(--text-muted);margin-top:4px">
          ${rule.response_type === 'list_menu'
            ? 'List menu format: { title, description, button_text, sections: [{ title, rows: [{ title, description, row_id }] }] }'
            : 'Button format: { title, description, buttons: [{ type: "reply", text, id }] }'}
        </div>
      </div>

      <div class="form-group" id="r-attachment-group" style="display:${['image','document','audio','video'].includes(rule.response_type) ? 'block' : 'none'}">
        <label class="form-label">Media URL</label>
        <input class="form-input" id="r-attachment" value="${app.esc(rule.attachment_url || '')}" placeholder="https://example.com/image.jpg" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Priority (lower = higher)</label>
          <input class="form-input" type="number" id="r-priority" value="${rule.priority}" />
        </div>
        <div class="form-group">
          <label class="form-label">Cooldown (seconds)</label>
          <input class="form-input" type="number" id="r-cooldown" value="${rule.cooldown_seconds}" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-checkbox">
            <input type="checkbox" id="r-active" ${rule.is_active ? 'checked' : ''} />
            <span>Active</span>
          </label>
        </div>
        <div class="form-group">
          <label class="form-checkbox">
            <input type="checkbox" id="r-fallback" ${rule.is_fallback ? 'checked' : ''} />
            <span>Fallback (catch-all)</span>
          </label>
        </div>
      </div>

      <div class="card" style="margin-top:12px">
        <div class="card-header">
          <span class="card-title">Branch Routing</span>
          <button class="btn btn-sm btn-secondary" onclick="chatbot._addBranchRow()">+ Add Branch</button>
        </div>
        <div id="branches-list">
          ${branches.length ? branches.map(b => chatbot._branchRowHTML(b)).join('') : '<div style="color:var(--text-muted);font-size:13px;padding:8px 0">No branches configured. Branches let you route responses to follow-up rules when a user interacts with menus or buttons.</div>'}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="document.getElementById('modal-overlay').classList.remove('open')">Cancel</button>
        <button class="btn btn-primary" onclick="chatbot._saveRule('${ruleId || ''}')">${isEdit ? 'Update' : 'Create'} Rule</button>
      </div>
    `;
  },

  _toggleMatchFields() {
    const mt = document.getElementById('r-match-type').value;
    document.getElementById('r-keyword-group').style.display = (mt === 'always') ? 'none' : 'block';
  },

  _toggleResponseFields() {
    const rt = document.getElementById('r-response-type').value;
    document.getElementById('r-menu-group').style.display = (rt === 'list_menu' || rt === 'buttons') ? 'block' : 'none';
    document.getElementById('r-attachment-group').style.display = (['image','document','audio','video'].includes(rt)) ? 'block' : 'none';
  },

  _branchRowHTML(b) {
    return `
      <div class="expander open" style="margin-bottom:6px">
        <div class="expander-header" style="padding:8px 12px">
          <span class="expander-arrow">▶</span>
          <span>Match: <strong>${app.esc(b.match_value)}</strong> → Rule: <strong>${b.next_rule ? b.next_rule.substring(0, 8)+'...' : '—'}</strong></span>
          <span style="margin-left:auto">
            <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();chatbot._deleteBranch('${b.id}')" style="padding:2px 8px;font-size:11px">Remove</button>
          </span>
        </div>
      </div>
    `;
  },

  _addBranchRow() {
    const list = document.getElementById('branches-list');
    const div = document.createElement('div');
    div.className = 'expander open';
    div.style.marginBottom = '6px';
    div.innerHTML = `
      <div class="expander-body" style="display:block;padding:8px 12px">
        <div class="form-row" style="grid-template-columns:1fr 1fr auto">
          <div class="form-group" style="margin:0">
            <label style="font-size:11px;color:var(--text-secondary)">Match Value (button ID / list row ID)</label>
            <input class="form-input" style="padding:6px 8px;font-size:13px" placeholder="e.g., yes_btn" />
          </div>
          <div class="form-group" style="margin:0">
            <label style="font-size:11px;color:var(--text-secondary)">Next Rule ID</label>
            <input class="form-input" style="padding:6px 8px;font-size:13px" placeholder="Rule UUID" />
          </div>
          <button class="btn btn-sm btn-danger" style="margin-top:18px;padding:2px 8px;font-size:11px" onclick="this.closest('.expander').remove()">✕</button>
        </div>
      </div>
    `;
    list.appendChild(div);
    if (list.querySelector('div[style]') && list.children.length === 1) {
      list.innerHTML = '';
      list.appendChild(div);
    }
  },

  async _deleteBranch(id) {
    try {
      await api.delete(`/api/chatbot/branches/${id}/`);
      app.toast('Branch removed');
    } catch (err) {
      app.toast(err.message, 'error');
    }
  },

  async _saveRule(ruleId) {
    const payload = {
      flow: document.getElementById('r-flow').value || null,
      match_type: document.getElementById('r-match-type').value,
      keyword: document.getElementById('r-keyword').value.trim(),
      reply_text: document.getElementById('r-reply').value.trim(),
      response_type: document.getElementById('r-response-type').value,
      priority: parseInt(document.getElementById('r-priority').value) || 0,
      cooldown_seconds: parseInt(document.getElementById('r-cooldown').value) || 0,
      is_active: document.getElementById('r-active').checked,
      is_fallback: document.getElementById('r-fallback').checked,
      attachment_url: document.getElementById('r-attachment').value.trim(),
    };

    // Parse menu config
    const menuEl = document.getElementById('r-menu-config');
    if (menuEl && menuEl.value.trim()) {
      try {
        payload.menu_config = JSON.parse(menuEl.value.trim());
      } catch {
        app.toast('Invalid JSON in menu configuration', 'error');
        return;
      }
    }

    if (!payload.keyword && payload.match_type !== 'always' && !payload.is_fallback) {
      app.toast('Enter a keyword or trigger value', 'warning');
      return;
    }

    try {
      if (ruleId) {
        await api.patch(`/api/chatbot/rules/${ruleId}/`, payload);
      } else {
        await api.post('/api/chatbot/rules/', payload);
      }
      app.toast(ruleId ? 'Rule updated' : 'Rule created');

      // Save branches if any
      const branchInputs = document.querySelectorAll('#branches-list .expander');
      if (branchInputs.length > 0 && !ruleId) {
        app.toast('Branches can be added after the rule is created. Edit the rule to add branches.', 'warning');
      }

      document.getElementById('modal-overlay').classList.remove('open');
      this.renderRules();
    } catch (err) {
      app.toast(err.message, 'error');
    }
  },

  /* ================================================================
     SESSIONS
     ================================================================ */

  async renderSessions() {
    const el = document.getElementById('tab-chatbot-sessions');
    el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    try {
      const sessions = await api.get('/api/chatbot/sessions/');
      el.innerHTML = `
        <div class="card">
          ${sessions.length ? `
            <div class="table-container">
              <table>
                <thead><tr>
                  <th>Phone</th>
                  <th>Current Flow</th>
                  <th>Current Rule</th>
                  <th>Last Interaction</th>
                  <th></th>
                </tr></thead>
                <tbody>
                  ${sessions.map(s => `
                    <tr>
                      <td style="font-family:monospace">${app.esc(s.sender_phone)}</td>
                      <td style="color:var(--text-secondary);font-size:12px">${s.current_flow || '—'}</td>
                      <td style="color:var(--text-secondary);font-size:12px">${s.current_rule || '—'}</td>
                      <td style="font-size:11px;color:var(--text-muted)">${new Date(s.last_interaction).toLocaleString()}</td>
                      <td><button class="btn btn-sm btn-danger" onclick="chatbot.endSession('${s.id}')">End</button></td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : '<div class="empty-state"><div class="empty-state-icon">💬</div><div class="empty-state-title">No active sessions</div><div class="empty-state-text">Sessions appear here when users interact with your chatbot flows.</div></div>'}
        </div>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },

  async endSession(id) {
    if (!confirm('End this session?')) return;
    try {
      await api.delete(`/api/chatbot/sessions/${id}/`);
      app.toast('Session ended');
      this.renderSessions();
    } catch (err) {
      app.toast(err.message, 'error');
    }
  },

  /* ================================================================
     MATCH LOGS
     ================================================================ */

  async renderLogs() {
    const el = document.getElementById('tab-chatbot-logs');
    el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    try {
      const logs = await api.get('/api/chatbot/logs/');
      el.innerHTML = `
        <div class="card">
          ${logs.length ? `
            <div class="table-container">
              <table>
                <thead><tr>
                  <th>Sender</th>
                  <th>Matched Keyword</th>
                  <th>Rule</th>
                  <th>Flow</th>
                  <th>Fallback</th>
                  <th>Time</th>
                </tr></thead>
                <tbody>
                  ${logs.map(l => `
                    <tr>
                      <td style="font-family:monospace">${app.esc(l.sender_phone)}</td>
                      <td style="font-weight:500">${app.esc(l.matched_keyword || '—')}</td>
                      <td style="color:var(--text-secondary);font-size:12px">${l.matched_rule ? l.matched_rule.substring(0, 8)+'...' : '—'}</td>
                      <td style="color:var(--text-secondary);font-size:12px">${l.matched_flow ? l.matched_flow.substring(0, 8)+'...' : '—'}</td>
                      <td>${l.is_fallback ? '<span class="badge badge-warning">Yes</span>' : 'No'}</td>
                      <td style="font-size:11px;color:var(--text-muted)">${new Date(l.created_at).toLocaleString()}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : '<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-title">No match logs yet</div><div class="empty-state-text">Logs appear here when incoming messages match chatbot rules.</div></div>'}
        </div>
      `;
    } catch (err) {
      el.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
    }
  },
};
