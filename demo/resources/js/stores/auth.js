import { defineStore } from 'pinia';
import { ref } from 'vue';
export const useAuth = defineStore('auth', () => {
    const token = ref('');
    const user = ref(null);
    async function request(path, options = {}) {
        const headers = { Accept: 'application/json', ...options.headers };
        if (token.value) headers.Authorization = `Bearer ${token.value}`;
        if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
        const response = await fetch(path, { ...options, headers });
        const body = response.status === 204 ? null : await response.json();
        if (!response.ok) {
            if (response.status === 401) { token.value = ''; user.value = null; }
            const error = new Error(body?.error?.message || '요청 실패');
            error.fields = body?.error?.fields || {};
            error.status = response.status;
            throw error;
        }
        return body;
    }
    async function login(values, signup = false) {
        const result = await request(`/api/auth/${signup ? 'signup' : 'login'}`, { method: 'POST', body: JSON.stringify(values) });
        token.value = result.data.accessToken;
        user.value = result.data.user;
    }
    async function logout() {
        try { await request('/api/auth/logout', { method: 'POST' }); }
        finally { token.value = ''; user.value = null; }
    }
    return { token, user, request, login, logout };
});
