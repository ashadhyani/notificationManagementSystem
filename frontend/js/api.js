// API Client Module
const API_BASE = window.location.port === '5173' && window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : '/api';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export const api = {
    async request(endpoint, options = {}) {
        const csrfToken = getCookie('csrftoken');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        const config = {
            headers,
            credentials: 'include',
            ...options,
        };

        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(data.error || data.detail || `Request failed with status ${response.status}`);
            }
            return data;
        } catch (err) {
            console.error(`API Error on ${endpoint}:`, err);
            throw err;
        }
    },

    // Auth & Trigger Actions
    async login(username, password, phone = '') {
        return this.request('/auth/login/', {
            method: 'POST',
            body: { username, password, phone },
        });
    },

    async logout() {
        return this.request('/auth/logout/', {
            method: 'POST',
        });
    },

    async register(username, email, password, isAdmin = false) {
        return this.request('/auth/register/', {
            method: 'POST',
            body: { username, email, password, is_admin: isAdmin },
        });
    },

    async getCurrentUser() {
        return this.request('/auth/me/');
    },

    // Admin Matrix & Templates
    async getMatrix() {
        return this.request('/matrix/');
    },

    async toggleTemplate(templateId) {
        return this.request(`/templates/${templateId}/toggle/`, {
            method: 'PATCH',
        });
    },

    async updateTemplate(templateId, subject, body) {
        return this.request(`/templates/${templateId}/`, {
            method: 'PUT',
            body: { subject, body },
        });
    },

    async testSendTemplate(templateId, recipient = '') {
        return this.request(`/templates/${templateId}/test-send/`, {
            method: 'POST',
            body: { recipient },
        });
    },

    // Web Push
    async getVapidPublicKey() {
        return this.request('/webpush/vapid-key/');
    },

    async subscribeWebPush(subscription) {
        return this.request('/webpush/subscribe/', {
            method: 'POST',
            body: subscription,
        });
    },

    // Delivery Logs
    async getLogs() {
        return this.request('/logs/');
    },

    async clearLogs() {
        return this.request('/logs/', {
            method: 'DELETE',
        });
    },
};
