const API_BASE = '';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  health: () => request('/api/health'),

  login: (farm_id, password) =>
    request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ farm_id, password }),
    }),

  signup: (data) =>
    request('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  analyzeSoil: (data) =>
    request('/api/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  chat: (query, location, language) =>
    request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ query, location, language }),
    }),

  analyzeImage: async (file, query, language) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('query', query);
    formData.append('language', language);
    const res = await fetch(`${API_BASE}/api/analyze-image`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Request failed');
    }
    return res.json();
  },

  farmHistory: (farm_id) => request(`/api/farm/${farm_id}/history`),
};
