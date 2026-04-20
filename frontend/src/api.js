const API_BASE = '';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse(res) {
  if (res.status === 401) {
    localStorage.clear();
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  return handleResponse(res);
}

export async function fetchDocuments() {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: authHeaders(),
  });
  return handleResponse(res);
}

export async function fetchDocument(docId) {
  const res = await fetch(`${API_BASE}/documents/${docId}`, {
    headers: authHeaders(),
  });
  return handleResponse(res);
}

export async function uploadDocument(formData) {
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  });
  return handleResponse(res);
}

export async function queryPolicy(question, policyType) {
  const body = { question };
  if (policyType) body.policy_type = policyType;
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}
