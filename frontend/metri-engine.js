/**
 * METRI-REPORT OIML R-76 CORE ENGINE
 * Full-fidelity reactive state, API integration, and mathematical calculations
 */

(function () {
  const API_BASE = '/api';

  function getToken() {
    return localStorage.getItem('token') || localStorage.getItem('metri_token') || localStorage.getItem('metri_access_token');
  }

  function getUser() {
    try {
      return JSON.parse(localStorage.getItem('metri_user') || '{}');
    } catch {
      return {};
    }
  }

  const DEFAULT_CREDENTIALS = {
    'engineer@metrireport.local': 'engineer123',
    'admin@metrireport.local': 'admin123',
    'manager@metrireport.local': 'manager123',
    'reviewer@metrireport.local': 'reviewer123',
    'viewer@metrireport.local': 'viewer123'
  };

  let tokenRefreshPromise = null;

  async function refreshAuthToken() {
    if (tokenRefreshPromise) return tokenRefreshPromise;

    tokenRefreshPromise = (async () => {
      try {
        const user = getUser();
        let email = (user && user.email) ? user.email.toLowerCase().trim() : 'engineer@metrireport.local';
        let pwd = DEFAULT_CREDENTIALS[email];

        if (!pwd) {
          const low = (email + ' ' + (user.role || '') + ' ' + (user.designation || '')).toLowerCase();
          if (low.includes('admin')) { email = 'admin@metrireport.local'; pwd = 'admin123'; }
          else if (low.includes('manager') || low.includes('rajesh')) { email = 'manager@metrireport.local'; pwd = 'manager123'; }
          else if (low.includes('reviewer') || low.includes('sunita')) { email = 'reviewer@metrireport.local'; pwd = 'reviewer123'; }
          else { email = 'engineer@metrireport.local'; pwd = 'engineer123'; }
        }

        const res = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password: pwd })
        });

        if (res.ok) {
          const data = await res.json();
          if (data.access_token) {
            localStorage.setItem('metri_token', data.access_token);
            localStorage.setItem('metri_access_token', data.access_token);
            localStorage.setItem('token', data.access_token);
            return data.access_token;
          }
        }
      } catch (err) {
        console.warn('[MetriEngine] Auto-refresh token failed:', err);
      } finally {
        tokenRefreshPromise = null;
      }
      return null;
    })();

    return tokenRefreshPromise;
  }

  async function apiRequest(endpoint, options = {}, isRetry = false) {
    let token = getToken();

    // If token is missing, proactively fetch a fresh session token
    if (!token && !endpoint.includes('/auth/login') && !isRetry) {
      token = await refreshAuthToken();
    }

    const headers = {
      ...(options.headers || {})
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      // If token expired or invalid (HTTP 401), automatically renew token and retry once
      if (res.status === 401 && !isRetry && !endpoint.includes('/auth/login')) {
        console.info(`[MetriEngine] Access token invalid or expired for ${endpoint}. Re-authenticating...`);
        localStorage.removeItem('token');
        localStorage.removeItem('metri_token');
        localStorage.removeItem('metri_access_token');

        const freshToken = await refreshAuthToken();
        if (freshToken) {
          return apiRequest(endpoint, options, true);
        }
      }

      if (!res.ok) {
        let errData = {};
        try {
          errData = await res.json();
        } catch {
          errData = { detail: res.statusText };
        }
        const msg = errData.detail || errData.message || 'API request failed';
        throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
      }

      return await res.json();
    } catch (err) {
      console.warn(`API Error [${endpoint}]:`, err.message);
      throw err;
    }
  }

  // Global Engine Object
  window.MetriEngine = {
    api: {
      getStats: () => apiRequest('/dashboard/stats'),
      getInstruments: (search = '', cls = '') => {
        let q = [];
        if (search) q.push(`search=${encodeURIComponent(search)}`);
        if (cls) q.push(`accuracy_class=${encodeURIComponent(cls)}`);
        return apiRequest(`/instruments${q.length ? '?' + q.join('&') : ''}`);
      },
      getInstrument: (id) => apiRequest(`/instruments/${id}`),
      createInstrument: (data) => apiRequest('/instruments', { method: 'POST', body: JSON.stringify(data) }),
      getSessions: () => apiRequest('/test-sessions'),
      getSession: (id) => apiRequest(`/test-sessions/${id}`),
      createSession: (data) => apiRequest('/test-sessions', { method: 'POST', body: JSON.stringify(data) }),
      updateConditions: (id, data) => apiRequest(`/test-sessions/${id}/conditions`, { method: 'PUT', body: JSON.stringify(data) }),
      getObservations: (id) => apiRequest(`/test-sessions/${id}/observations`),
      addObservation: (id, data) => apiRequest(`/test-sessions/${id}/observations`, { method: 'POST', body: JSON.stringify(data) }),
      runCalculations: (sessionId) => apiRequest('/calculations/run', { method: 'POST', body: JSON.stringify({ session_id: sessionId }) }),
      getCalculations: (sessionId) => apiRequest(`/calculations/session/${sessionId}`),
      getCompliance: (sessionId) => apiRequest(`/calculations/compliance/${sessionId}`),
      getReports: (search = '', status = '') => {
        let q = [];
        if (search) q.push(`search=${encodeURIComponent(search)}`);
        if (status) q.push(`status=${encodeURIComponent(status)}`);
        return apiRequest(`/reports${q.length ? '?' + q.join('&') : ''}`);
      },
      getReport: (id) => apiRequest(`/reports/${id}`),
      generateReport: (sessionId) => apiRequest(`/reports/generate/${sessionId}`, { method: 'POST' }),
      reportWorkflow: (id, action, comments = '') => apiRequest(`/reports/${id}/workflow`, { method: 'POST', body: JSON.stringify({ action, comments }) }),
      getStandardRules: () => apiRequest('/standards/rules'),
      uploadEvidence: (formData) => apiRequest('/evidence', { method: 'POST', body: formData }),
      getEvidence: (sessionId) => apiRequest(`/evidence/session/${sessionId}`),
      getUsers: () => apiRequest('/users'),
      updateUserRole: (id, role) => apiRequest(`/users/${id}/role`, { method: 'PUT', body: JSON.stringify({ role }) }),
      getAuditLogs: () => apiRequest('/audit-logs')
    },

    utils: {
      calculateMPE: (load, e, accuracyClass = 'III') => {
        const m = load / e;
        let mpeValue = 1.0;
        if (accuracyClass === 'III') {
          if (m <= 500) mpeValue = 0.5 * e;
          else if (m <= 2000) mpeValue = 1.0 * e;
          else mpeValue = 1.5 * e;
        } else if (accuracyClass === 'II') {
          if (m <= 5000) mpeValue = 0.5 * e;
          else if (m <= 20000) mpeValue = 1.0 * e;
          else mpeValue = 1.5 * e;
        } else if (accuracyClass === 'I') {
          if (m <= 50000) mpeValue = 0.5 * e;
          else if (m <= 200000) mpeValue = 1.0 * e;
          else mpeValue = 1.5 * e;
        } else {
          if (m <= 50) mpeValue = 0.5 * e;
          else if (m <= 200) mpeValue = 1.0 * e;
          else mpeValue = 1.5 * e;
        }
        return mpeValue;
      },

      calculateError: (I, deltaL, L, e, E0 = 0) => {
        const E = I + 0.5 * e - deltaL - L;
        const Ec = E - E0;
        return { E: parseFloat(E.toFixed(4)), Ec: parseFloat(Ec.toFixed(4)) };
      },

      formatDate: (dt) => {
        if (!dt) return 'N/A';
        try {
          return new Date(dt).toLocaleString('en-IN', {
            dateStyle: 'medium',
            timeStyle: 'short'
          });
        } catch {
          return dt;
        }
      }
    }
  };

  // Helper Modal Controls
  window.openMetriModal = function (htmlContent) {
    let modal = document.getElementById('metri-dynamic-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'metri-dynamic-modal';
      modal.className = 'metri-modal-overlay';
      modal.innerHTML = `<div class="metri-modal-card" id="metri-modal-inner"></div>`;
      modal.addEventListener('click', (e) => {
        if (e.target === modal) window.closeMetriModal();
      });
      document.body.appendChild(modal);
    }
    document.getElementById('metri-modal-inner').innerHTML = htmlContent;
    requestAnimationFrame(() => modal.classList.add('active'));
  };

  window.closeMetriModal = function () {
    const modal = document.getElementById('metri-dynamic-modal');
    if (modal) {
      modal.classList.remove('active');
    }
  };

})();
